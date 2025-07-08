import feedparser
import requests
from typing import List, Dict, Any
from datetime import datetime
import dateparser
from urllib.parse import urljoin, urlparse

from .base import BaseCollector, CollectorItem
from config import config


class RSSCollector(BaseCollector):
    """RSS订阅收集器"""

    def __init__(self, name: str, rss_url: str, source_name: str):
        super().__init__(name)
        self.rss_url = rss_url
        self.source_name = source_name
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "LogWatcher/1.0 (Tech News Collector)"}
        )

    def get_source_name(self) -> str:
        return self.source_name

    def parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        try:
            # 尝试使用feedparser的时间解析
            if hasattr(feedparser, "parse"):
                parsed_time = feedparser._parse_date(date_str)
                if parsed_time:
                    return datetime(*parsed_time[:6])

            # 使用dateparser作为备用
            parsed_date = dateparser.parse(date_str)
            if parsed_date:
                return parsed_date

        except Exception as e:
            self.logger.warning(f"日期解析失败: {date_str}, 错误: {e}")

        return datetime.utcnow()

    def extract_summary(self, entry: Dict[str, Any]) -> str:
        """提取摘要"""
        # TODO #3 数据收集器: 优化摘要提取逻辑，支持HTML内容清理
        summary = entry.get("summary", "")
        if not summary:
            summary = entry.get("description", "")

        # 简单的HTML标签清理
        import re

        summary = re.sub(r"<[^>]+>", "", summary)
        summary = summary.strip()

        # 限制摘要长度
        if len(summary) > 500:
            summary = summary[:497] + "..."

        return summary

    async def collect(self) -> List[CollectorItem]:
        """收集RSS数据"""
        items = []

        try:
            self.logger.info(f"开始收集RSS数据: {self.rss_url}")

            # 获取RSS数据
            response = self.session.get(self.rss_url, timeout=30)
            response.raise_for_status()

            # 解析RSS
            feed = feedparser.parse(response.content)

            if feed.bozo:
                self.logger.warning(f"RSS解析警告: {feed.bozo_exception}")

            # 处理每个条目
            for entry in feed.entries[: config.MAX_ARTICLES_PER_SOURCE]:
                try:
                    item = self.parse_rss_entry(entry)
                    if self.validate_item(item):
                        items.append(item)
                except Exception as e:
                    self.logger.error(f"解析RSS条目失败: {e}")
                    continue

            self.logger.info(f"RSS收集完成，共收集到 {len(items)} 条数据")

        except Exception as e:
            self.logger.error(f"RSS收集失败: {e}")
            raise

        return items

    def parse_rss_entry(self, entry: Dict[str, Any]) -> CollectorItem:
        """解析单个RSS条目"""
        # 提取基本信息
        title = entry.get("title", "").strip()
        url = entry.get("link", "").strip()
        summary = self.extract_summary(entry)

        # 解析发布时间
        published_at = None
        if "published" in entry:
            published_at = self.parse_date(entry.published)
        elif "updated" in entry:
            published_at = self.parse_date(entry.updated)

        # 提取作者
        author = None
        if "author" in entry:
            author = entry.author
        elif "authors" in entry and entry.authors:
            author = entry.authors[0].get("name", "")

        # 提取标签
        tags = []
        if "tags" in entry:
            tags = [tag.term for tag in entry.tags if hasattr(tag, "term")]

        # TODO #3 数据收集器: 添加内容全文抓取功能
        return CollectorItem(
            title=title,
            url=url,
            summary=summary,
            published_at=published_at,
            source=self.source_name,
            author=author,
            tags=tags,
            extra_data={"rss_id": entry.get("id"), "rss_guid": entry.get("guid")},
        )


# 预定义的RSS收集器
class HackerNewsCollector(RSSCollector):
    """Hacker News收集器"""

    def __init__(self):
        super().__init__(
            name="hacker_news",
            rss_url="https://hnrss.org/frontpage",
            source_name="Hacker News",
        )


class ProductHuntCollector(RSSCollector):
    """Product Hunt收集器"""

    def __init__(self):
        super().__init__(
            name="product_hunt",
            rss_url="https://www.producthunt.com/feed",
            source_name="Product Hunt",
        )


class DevToCollector(RSSCollector):
    """Dev.to收集器"""

    def __init__(self):
        super().__init__(
            name="dev_to", rss_url="https://dev.to/feed", source_name="Dev.to"
        )
