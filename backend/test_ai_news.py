#!/usr/bin/env python3
"""
测试AI新闻收集功能
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from collectors.ai_news_collector import AINewsCollector
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_ai_news_collector():
    """测试AI新闻收集器"""
    print("🤖 开始测试AI新闻收集器...")

    # 创建收集器实例
    collector = AINewsCollector()

    # 运行收集器
    result = await collector.run()

    # 显示结果
    print(f"\n📊 收集结果:")
    print(f"成功: {result['success']}")
    print(f"执行时间: {result['execution_time']:.2f}秒")
    print(f"收集数量: {result['count']}")

    if result["success"]:
        print(f"\n📰 收集到的新闻:")
        for i, item in enumerate(result["items"], 1):
            print(f"\n{i}. {item.title}")
            print(f"   来源: {item.source}")
            print(f"   作者: {item.author}")
            print(f"   摘要: {item.summary[:100]}...")
            print(f"   标签: {item.tags}")
            print(f"   发布时间: {item.published_at}")
    else:
        print(f"\n❌ 收集失败: {result.get('error', '未知错误')}")


if __name__ == "__main__":
    asyncio.run(test_ai_news_collector())
