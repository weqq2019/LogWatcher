#!/usr/bin/env python3
"""
快速测试AI新闻收集器
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from collectors.ai_news_collector import AINewsCollector


async def test_ai_news_collector():
    """快速测试AI新闻收集器"""
    print("🚀 快速测试AI新闻收集器")
    print("=" * 50)

    try:
        # 创建收集器
        collector = AINewsCollector()
        print(f"✅ 收集器创建成功")
        print(f"🤖 模型: {collector.model}")
        print(f"⏰ 超时: 300秒")
        print(f"🔄 重试: 1次")
        print()

        # 开始收集
        print("📊 开始收集AI新闻...")
        items = await collector.collect()

        print(f"✅ 收集完成，共 {len(items)} 条新闻")
        print()

        # 显示前3条新闻
        for i, item in enumerate(items[:3], 1):
            print(f"📌 新闻 {i}:")
            print(f"   📰 标题: {item.title}")
            print(f"   📝 摘要: {item.summary[:100]}...")
            print(f"   🏷️ 标签: {item.tags}")
            print()

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        print(traceback.format_exc())
        return False


if __name__ == "__main__":
    result = asyncio.run(test_ai_news_collector())
    if result:
        print("🎉 测试通过！")
    else:
        print("💥 测试失败！")
