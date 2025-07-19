import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time


@dataclass
class CollectorItem:
    """收集器数据项"""

    title: str
    summary: str = ""
    content: str = ""
    url: str = ""
    source: str = ""
    author: str = ""
    published_at: Optional[datetime] = None
    tags: List[str] = None
    model: str = ""  # AI模型名称
    extra_data: Dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.extra_data is None:
            self.extra_data = {}


class BaseCollector:
    """基础收集器抽象类"""

    def __init__(self):
        self.name = ""
        self.description = ""
        self.url = ""
        self.enabled = True

    def get_source_name(self) -> str:
        """获取数据源名称"""
        return self.name

    async def run(self) -> Dict[str, Any]:
        """运行收集器"""
        if not self.enabled:
            return {
                "success": False,
                "error": "收集器已禁用",
                "count": 0,
                "execution_time": 0,
            }

        start_time = time.time()
        try:
            items = await self.collect()
            execution_time = time.time() - start_time

            return {
                "success": True,
                "items": items,
                "count": len(items),
                "execution_time": execution_time,
            }

        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "count": 0,
                "execution_time": execution_time,
            }

    async def collect(self) -> List[CollectorItem]:
        """收集数据 - 子类需要实现此方法"""
        raise NotImplementedError("子类必须实现 collect 方法")

    def enable(self):
        """启用收集器"""
        self.enabled = True

    def disable(self):
        """禁用收集器"""
        self.enabled = False
