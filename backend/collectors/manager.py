import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from .base import BaseCollector, CollectorItem
from .cursor_collector import CursorCollector
from .ai_news_collector import AINewsCollector
from database import get_db_context
from models import NewsArticle, ProjectRelease, ToolUpdate, Category, CursorUpdate

logger = logging.getLogger(__name__)


class CollectorManager:
    """收集器管理器"""

    def __init__(self):
        self.collectors: List[BaseCollector] = []
        self.initialize_collectors()

    def initialize_collectors(self):
        """初始化所有收集器"""
        # Cursor收集器
        self.collectors.append(CursorCollector())

        # AI新闻收集器
        self.collectors.append(AINewsCollector("AI新闻收集器"))

        logger.info(f"初始化了 {len(self.collectors)} 个收集器")

    def get_collector(self, name: str) -> Optional[BaseCollector]:
        """根据名称获取收集器"""
        for collector in self.collectors:
            if collector.name == name:
                return collector
        return None

    def get_collector_list(self) -> List[Dict[str, Any]]:
        """获取收集器列表"""
        return [
            {
                "name": collector.name,
                "source": collector.get_source_name(),
                "type": collector.__class__.__name__,
            }
            for collector in self.collectors
        ]

    async def run_collector(self, collector_name: str) -> Dict[str, Any]:
        """运行指定的收集器"""
        collector = self.get_collector(collector_name)
        if not collector:
            return {"success": False, "error": f"收集器 '{collector_name}' 不存在"}

        try:
            # 运行收集器
            result = await collector.run()

            if result["success"]:
                # 保存数据到数据库
                await self.save_items(result["items"], collector)

                return {
                    "success": True,
                    "collector": collector_name,
                    "items_collected": result["count"],
                    "execution_time": result["execution_time"],
                }
            else:
                return result

        except Exception as e:
            logger.error(f"运行收集器 {collector_name} 失败: {e}")
            return {"success": False, "error": str(e)}

    async def run_all_collectors(self) -> Dict[str, Any]:
        """运行所有收集器"""
        results = []
        total_items = 0

        logger.info("开始运行所有收集器")

        for collector in self.collectors:
            try:
                result = await collector.run()

                if result["success"]:
                    # 保存数据到数据库
                    await self.save_items(result["items"], collector)
                    total_items += result["count"]

                results.append(
                    {
                        "collector": collector.name,
                        "success": result["success"],
                        "items_collected": result.get("count", 0),
                        "execution_time": result.get("execution_time", 0),
                        "error": result.get("error"),
                    }
                )

            except Exception as e:
                logger.error(f"运行收集器 {collector.name} 失败: {e}")
                results.append(
                    {"collector": collector.name, "success": False, "error": str(e)}
                )

        logger.info(f"所有收集器运行完成，共收集 {total_items} 条数据")

        return {"success": True, "total_items": total_items, "results": results}

    async def save_items(self, items: List[CollectorItem], collector: BaseCollector):
        """保存收集到的数据到数据库"""
        if not items:
            return

        logger.info(f"开始保存 {len(items)} 条数据到数据库")

        with get_db_context() as db:
            saved_count = 0

            for item in items:
                try:
                    # TODO #3 数据收集器: 优化数据去重逻辑
                    if await self.is_duplicate(db, item):
                        continue

                    # 根据收集器类型保存到不同的表
                    if self.is_news_collector(collector):
                        await self.save_news_article(db, item)
                    elif self.is_project_collector(collector):
                        await self.save_project_release(db, item)
                    elif self.is_tool_collector(collector):
                        await self.save_tool_update(db, item)
                    elif self.is_cursor_collector(collector):
                        await self.save_cursor_update(db, item)

                    saved_count += 1

                except Exception as e:
                    logger.error(f"保存数据失败: {e}")
                    continue

            db.commit()
            logger.info(f"成功保存 {saved_count} 条数据到数据库")

    def is_news_collector(self, collector: BaseCollector) -> bool:
        """判断是否为新闻收集器"""
        return collector.__class__.__name__ in [
            "AINewsCollector",
        ]

    def is_project_collector(self, collector: BaseCollector) -> bool:
        """判断是否为项目收集器"""
        return False  # 已删除所有项目收集器

    def is_tool_collector(self, collector: BaseCollector) -> bool:
        """判断是否为工具收集器"""
        return False  # 已删除所有工具收集器

    def is_cursor_collector(self, collector: BaseCollector) -> bool:
        """判断是否为 Cursor 收集器"""
        return collector.__class__.__name__ == "CursorCollector"

    async def is_duplicate(self, db, item: CollectorItem) -> bool:
        """检查数据是否已存在"""
        # 检查新闻表
        existing_news = (
            db.query(NewsArticle).filter(NewsArticle.url == item.url).first()
        )
        if existing_news:
            return True

        # 检查项目发布表
        existing_project = (
            db.query(ProjectRelease).filter(ProjectRelease.repo_url == item.url).first()
        )
        if existing_project:
            return True

        # 检查工具更新表
        existing_tool = db.query(ToolUpdate).filter(ToolUpdate.url == item.url).first()
        if existing_tool:
            return True

        # 检查 Cursor 更新表
        if item.extra_data and "version" in item.extra_data:
            existing_cursor = (
                db.query(CursorUpdate)
                .filter(CursorUpdate.version == item.extra_data["version"])
                .first()
            )
            if existing_cursor:
                return True

        return False

    async def save_news_article(self, db, item: CollectorItem):
        """保存新闻文章"""
        article = NewsArticle(
            title=item.title,
            summary=item.summary,
            content=item.content,
            url=item.url,
            source=item.source,
            author=item.author,
            published_at=item.published_at or datetime.utcnow(),
            tags=item.tags or [],
            category_id=await self.get_category_id(db, "技术新闻"),
        )
        db.add(article)

    async def save_project_release(self, db, item: CollectorItem):
        """保存项目发布"""
        extra_data = item.extra_data or {}

        release = ProjectRelease(
            project_name=extra_data.get("repo", "").split("/")[-1],
            repo_url=item.url,
            version=extra_data.get("tag_name", ""),
            tag_name=extra_data.get("tag_name", ""),
            title=item.title,
            description=item.summary,
            changelog=item.content,
            published_at=item.published_at or datetime.utcnow(),
            category_id=await self.get_category_id(db, "开源项目"),
            is_prerelease=extra_data.get("is_prerelease", False),
        )
        db.add(release)

    async def save_tool_update(self, db, item: CollectorItem):
        """保存工具更新"""
        extra_data = item.extra_data or {}

        update = ToolUpdate(
            tool_name=extra_data.get("repo", "").split("/")[-1],
            version=extra_data.get("tag_name", ""),
            title=item.title,
            description=item.summary,
            changelog=item.content,
            url=item.url,
            published_at=item.published_at or datetime.utcnow(),
            category_id=await self.get_category_id(db, "工具更新"),
            tags=item.tags or [],
            is_major="major" in (item.tags or []),
        )
        db.add(update)

    async def save_cursor_update(self, db, item: CollectorItem):
        """保存 Cursor 更新"""
        extra_data = item.extra_data or {}

        # 检查是否已存在该版本
        existing = (
            db.query(CursorUpdate)
            .filter(CursorUpdate.version == extra_data.get("version", ""))
            .first()
        )

        if existing:
            # 更新现有记录
            existing.title = item.title
            existing.original_content = extra_data.get("original_content", "")
            existing.translated_content = extra_data.get("translated_content", "")
            existing.analysis = extra_data.get("analysis", "")
            existing.url = item.url
            existing.collected_at = datetime.utcnow()
            existing.updated_at = datetime.utcnow()
        else:
            # 创建新记录
            cursor_update = CursorUpdate(
                version=extra_data.get("version", ""),
                release_date=item.published_at or datetime.utcnow(),
                title=item.title,
                original_content=extra_data.get("original_content", ""),
                translated_content=extra_data.get("translated_content", ""),
                analysis=extra_data.get("analysis", ""),
                url=item.url,
                collected_at=datetime.utcnow(),
                is_major=extra_data.get("is_major", False),
            )
            db.add(cursor_update)

    async def get_category_id(self, db, category_name: str) -> Optional[int]:
        """获取或创建分类ID"""
        category = db.query(Category).filter(Category.name == category_name).first()

        if not category:
            # TODO #3 数据收集器: 预设分类数据初始化
            category = Category(
                name=category_name, description=f"自动创建的{category_name}分类"
            )
            db.add(category)
            db.flush()

        return category.id


# 全局收集器管理器实例
collector_manager = CollectorManager()
