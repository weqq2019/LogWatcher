from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
from datetime import datetime

from database import get_db
from models import NewsArticle, APICallRecord
from collectors.manager import CollectorManager
from collectors.ai_news_collector import AINewsCollector
from config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# 创建收集器管理器实例
collector_manager = CollectorManager()


@router.get("/")
async def get_news(db: Session = Depends(get_db)):
    """获取所有新闻"""
    try:
        news_articles = (
            db.query(NewsArticle)
            .order_by(NewsArticle.published_at.desc())
            .limit(50)
            .all()
        )

        # 转换为字典格式
        news_list = []
        for article in news_articles:
            news_list.append(
                {
                    "id": article.id,
                    "title": article.title,
                    "summary": article.summary,
                    "content": article.content,
                    "url": article.url,
                    "source": article.source,
                    "author": article.author,
                    "published_at": (
                        article.published_at.isoformat()
                        if article.published_at
                        else None
                    ),
                    "created_at": (
                        article.created_at.isoformat() if article.created_at else None
                    ),
                    "tags": article.tags,
                    "model": article.model,
                }
            )

        return {"success": True, "data": news_list, "count": len(news_list)}
    except Exception as e:
        logger.error(f"获取新闻列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取新闻列表失败: {str(e)}")


@router.get("/ai")
async def get_ai_news(db: Session = Depends(get_db)):
    """获取AI新闻"""
    try:
        ai_news = (
            db.query(NewsArticle)
            .filter(NewsArticle.source == "AI新闻助手")
            .order_by(NewsArticle.published_at.desc())
            .limit(20)
            .all()
        )

        news_list = []
        for article in ai_news:
            news_list.append(
                {
                    "id": article.id,
                    "title": article.title,
                    "summary": article.summary,
                    "content": article.content,
                    "url": article.url,
                    "source": article.source,
                    "author": article.author,
                    "published_at": (
                        article.published_at.isoformat()
                        if article.published_at
                        else None
                    ),
                    "created_at": (
                        article.created_at.isoformat() if article.created_at else None
                    ),
                    "tags": article.tags,
                }
            )

        return {"success": True, "data": news_list, "count": len(news_list)}
    except Exception as e:
        logger.error(f"获取AI新闻失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取AI新闻失败: {str(e)}")


@router.post("/ai/collect")
async def collect_ai_news(db: Session = Depends(get_db)):
    """手动触发AI新闻收集 - 每日限制3次"""
    try:
        # 🔒 检查每日调用次数限制
        today = datetime.now().strftime("%Y-%m-%d")
        api_record = (
            db.query(APICallRecord)
            .filter(
                APICallRecord.api_name == APICallRecord.API_AI_NEWS_COLLECT,
                APICallRecord.call_date == today,
            )
            .first()
        )

        # 检查是否超过每日限制
        if api_record and api_record.call_count >= settings.daily_ai_collect_limit:
            raise HTTPException(
                status_code=429,
                detail=f"每日AI新闻收集次数已达限制({settings.daily_ai_collect_limit}次)，今日已调用{api_record.call_count}次，请明天再试",
            )

        # 获取AI新闻收集器
        ai_collector = collector_manager.get_collector("AI新闻收集器")
        if not ai_collector:
            raise HTTPException(status_code=404, detail="AI新闻收集器未找到")

        # 运行收集器
        result = await ai_collector.run()

        if result["success"]:
            # 保存新闻到数据库
            items = result.get("items", [])
            saved_count = 0

            for item in items:
                try:
                    # 检查是否已存在相同标题的新闻
                    existing = (
                        db.query(NewsArticle)
                        .filter(
                            NewsArticle.title == item.title,
                            NewsArticle.source == item.source,
                        )
                        .first()
                    )

                    if not existing:
                        news_article = NewsArticle(
                            title=item.title,
                            summary=item.summary,
                            content=item.content,
                            url=item.url,
                            source=item.source,
                            author=item.author,
                            published_at=item.published_at,
                            tags=item.tags,
                            model=item.model,
                        )
                        db.add(news_article)
                        saved_count += 1

                except Exception as e:
                    logger.error(f"保存新闻项失败: {str(e)}")
                    continue

            db.commit()

            # 🔒 更新API调用记录
            if api_record:
                api_record.call_count += 1
                api_record.last_call_time = datetime.now()
                api_record.updated_at = datetime.now()
            else:
                # 创建新的调用记录
                api_record = APICallRecord(
                    api_name=APICallRecord.API_AI_NEWS_COLLECT,
                    call_date=today,
                    call_count=1,
                    last_call_time=datetime.now(),
                )
                db.add(api_record)

            db.commit()

            return {
                "success": True,
                "message": f"成功收集并保存 {saved_count} 条AI新闻",
                "collected_count": result["count"],
                "saved_count": saved_count,
                "execution_time": result["execution_time"],
                "remaining_calls": settings.daily_ai_collect_limit
                - api_record.call_count,  # 🔒 返回剩余调用次数
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "收集失败"),
                "execution_time": result.get("execution_time", 0),
            }

    except Exception as e:
        logger.error(f"AI新闻收集失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI新闻收集失败: {str(e)}")


@router.get("/ai/status")
async def get_ai_collect_status(db: Session = Depends(get_db)):
    """获取AI新闻收集状态和剩余次数"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        api_record = (
            db.query(APICallRecord)
            .filter(
                APICallRecord.api_name == APICallRecord.API_AI_NEWS_COLLECT,
                APICallRecord.call_date == today,
            )
            .first()
        )

        current_calls = api_record.call_count if api_record else 0
        remaining_calls = max(0, settings.daily_ai_collect_limit - current_calls)

        return {
            "success": True,
            "data": {
                "current_calls": current_calls,
                "remaining_calls": remaining_calls,
                "max_calls": settings.daily_ai_collect_limit,
                "can_collect": remaining_calls > 0,
                "current_model": settings.ai_model,  # 返回当前使用的模型
                "last_call_time": (
                    api_record.last_call_time.isoformat() if api_record else None
                ),
            },
        }
    except Exception as e:
        logger.error(f"获取AI收集状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取AI收集状态失败: {str(e)}")


@router.get("/{news_id}")
async def get_news_detail(news_id: int, db: Session = Depends(get_db)):
    """获取新闻详情"""
    try:
        news_article = db.query(NewsArticle).filter(NewsArticle.id == news_id).first()

        if not news_article:
            raise HTTPException(status_code=404, detail="新闻不存在")

        return {
            "success": True,
            "data": {
                "id": news_article.id,
                "title": news_article.title,
                "summary": news_article.summary,
                "content": news_article.content,
                "url": news_article.url,
                "source": news_article.source,
                "author": news_article.author,
                "published_at": (
                    news_article.published_at.isoformat()
                    if news_article.published_at
                    else None
                ),
                "created_at": (
                    news_article.created_at.isoformat()
                    if news_article.created_at
                    else None
                ),
                "tags": news_article.tags,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取新闻详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取新闻详情失败: {str(e)}")


@router.get("/sources/list")
async def get_news_sources(db: Session = Depends(get_db)):
    """获取新闻来源列表"""
    try:
        sources = db.query(NewsArticle.source).distinct().all()
        source_list = [source[0] for source in sources if source[0]]

        return {"success": True, "data": source_list, "count": len(source_list)}
    except Exception as e:
        logger.error(f"获取新闻来源失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取新闻来源失败: {str(e)}")


@router.get("/sources/{source_name}")
async def get_news_by_source(source_name: str, db: Session = Depends(get_db)):
    """根据来源获取新闻"""
    try:
        news_articles = (
            db.query(NewsArticle)
            .filter(NewsArticle.source == source_name)
            .order_by(NewsArticle.published_at.desc())
            .limit(30)
            .all()
        )

        news_list = []
        for article in news_articles:
            news_list.append(
                {
                    "id": article.id,
                    "title": article.title,
                    "summary": article.summary,
                    "content": article.content,
                    "url": article.url,
                    "source": article.source,
                    "author": article.author,
                    "published_at": (
                        article.published_at.isoformat()
                        if article.published_at
                        else None
                    ),
                    "created_at": (
                        article.created_at.isoformat() if article.created_at else None
                    ),
                    "tags": article.tags,
                }
            )

        return {
            "success": True,
            "data": news_list,
            "count": len(news_list),
            "source": source_name,
        }
    except Exception as e:
        logger.error(f"获取来源新闻失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取来源新闻失败: {str(e)}")
