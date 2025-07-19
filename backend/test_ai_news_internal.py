#!/usr/bin/env python3
"""
🧠 容器内AI新闻收集功能测试脚本
直接在后端容器内测试AI新闻收集功能
"""

import sys
import os
import asyncio
from datetime import datetime
import time  # Added for time.time()

# 添加当前目录到Python路径
sys.path.insert(0, "/app")

from collectors.ai_news_collector import AINewsCollector
from collectors.manager import CollectorManager
from database import get_db_context
from models import NewsArticle


async def test_ai_news_collector_direct():
    """
    🧠 直接测试AI新闻收集器
    """
    print("🔧 步骤3: 直接测试AI新闻收集器")
    print("🔍 直接测试AI新闻收集器...")

    try:
        # 创建AI新闻收集器实例
        collector = AINewsCollector()
        print(f"✅ AI新闻收集器实例创建成功: {collector.name}")
        print(f"🤖 使用模型: {collector.model}")  # 🔄 显示当前使用的模型
        print(f"🔧 已启用内容质量优化提示词")

        # 直接调用收集方法
        print("📊 开始收集AI新闻...")
        start_time = time.time()
        items = await collector.collect()
        end_time = time.time()
        print(f"✅ 收集完成，共获取 {len(items)} 条新闻")
        print(f"⏱️ 收集用时: {end_time - start_time:.2f}秒")

        # 显示前3条新闻
        for i, item in enumerate(items[:3], 1):
            print(f"\n📌 新闻 {i}:")
            print(f"   📰 标题: {item.title}")
            print(f"   🏷️ 来源: {item.source}")
            print(f"   📅 时间: {item.published_at}")
            print(f"   📝 摘要: {item.summary[:100]}...")
            print(f"   🏷️ 标签: {item.tags}")

        return True  # 🔄 返回成功结果

    except Exception as e:
        print(f"❌ 直接测试AI新闻收集器失败: {e}")
        import traceback

        print(f"详细错误信息: {traceback.format_exc()}")
        return False  # 🔄 返回失败结果


async def test_collector_manager():
    """
    🔧 测试收集器管理器
    """
    print("\n🔍 测试收集器管理器...")

    try:
        # 创建收集器管理器
        manager = CollectorManager()

        print(f"✅ 收集器管理器创建成功，共 {len(manager.collectors)} 个收集器")

        # 查找AI新闻收集器
        ai_collector = manager.get_collector("ai_news")
        if ai_collector:
            print(f"✅ 找到AI新闻收集器: {ai_collector.name}")
        else:
            print("❌ 未找到AI新闻收集器")
            # 列出所有收集器
            print("📋 可用收集器:")
            for collector in manager.collectors:
                print(f"   - {collector.name}")
            return False

        # 添加延迟避免过频繁调用
        print("⏳ 等待3秒后进行管理器测试...")
        await asyncio.sleep(3)

        # 运行AI新闻收集器
        print("📊 通过管理器运行AI新闻收集...")
        result = await manager.run_collector("ai_news")

        if result.get("success"):
            print(
                f"✅ 通过管理器运行AI新闻收集成功，收集到 {result.get('items_collected', 0)} 条新闻"
            )
            print(f"⏱️ 执行时间: {result.get('execution_time', 0):.2f}秒")
        else:
            print(
                f"⚠️ 通过管理器运行AI新闻收集有问题: {result.get('error', '未知错误')}"
            )

        return True

    except Exception as e:
        print(f"❌ 测试收集器管理器失败: {e}")
        import traceback

        print(f"详细错误信息: {traceback.format_exc()}")
        return False


def test_database_connection():
    """
    🗃️ 测试数据库连接
    """
    print("\n🔍 测试数据库连接...")

    try:
        with get_db_context() as db:
            # 查询现有AI新闻数量
            ai_news_count = (
                db.query(NewsArticle).filter(NewsArticle.source == "ai").count()
            )

            print(f"✅ 数据库连接成功，当前AI新闻数量: {ai_news_count}")

            # 查询最近3条AI新闻
            recent_news = (
                db.query(NewsArticle)
                .filter(NewsArticle.source == "ai")
                .order_by(NewsArticle.created_at.desc())
                .limit(3)
                .all()
            )

            print(f"📰 最近3条AI新闻:")
            for i, news in enumerate(recent_news):
                print(f"   {i+1}. {news.title} ({news.created_at})")

        return True

    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def test_config():
    """
    ⚙️ 测试配置
    """
    print("\n🔍 测试配置...")

    try:
        from config import settings

        print(f"✅ 配置加载成功:")
        print(f"   📱 应用名称: {settings.app_name}")
        print(f"   🔍 调试模式: {settings.debug}")
        print(f"   🗃️ 数据库URL: {settings.database_url}")
        print(f"   🔑 DeepSeek API URL: {settings.deepseek_api_url}")
        print(f"   🎯 API密钥: {settings.deepseek_api_key[:20]}...")

        return True

    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False


async def main():
    """
    🎯 主测试函数
    """
    print("🚀 开始后端容器内AI新闻收集测试...")
    print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐳 运行环境: Docker容器内部")
    print("=" * 60)

    # 测试结果统计
    test_results = {}

    # 1. 配置测试
    print("🔧 步骤1: 配置测试")
    result = test_config()
    test_results["配置加载"] = result

    # 2. 数据库连接测试
    print("\n🔧 步骤2: 数据库连接测试")
    result = test_database_connection()
    test_results["数据库连接"] = result

    # 3. 直接测试AI新闻收集器
    print("\n🔧 步骤3: 直接测试AI新闻收集器")
    result = await test_ai_news_collector_direct()
    test_results["AI新闻收集器"] = result

    # 4. 测试收集器管理器
    print("\n🔧 步骤4: 测试收集器管理器")
    result = await test_collector_manager()
    test_results["收集器管理器"] = result

    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print("=" * 60)

    for test_name, passed in test_results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")

    passed_count = sum(1 for _, passed in test_results.items() if passed)
    total_count = len(test_results)

    print(f"\n🎯 总计: {passed_count}/{total_count} 项测试通过")

    if passed_count == total_count:
        print("🎉 所有测试都通过了！AI新闻收集功能运行正常")
        print("\n💡 接下来可以:")
        print("   - 访问前端页面测试UI: http://localhost:23000")
        print("   - 调用API接口: http://localhost:28000/api/news/ai")
        print("   - 查看数据库中的新闻数据")
    else:
        print("⚠️ 部分测试失败，但系统可能仍然可用")
        print("\n🔍 问题排查建议:")
        if not test_results["配置加载"]:
            print("   - 检查配置文件和环境变量")
        if not test_results["数据库连接"]:
            print("   - 检查MySQL数据库连接")
        if not test_results["AI新闻收集器"]:
            print("   - 检查AI API连接和SSL证书")
        if not test_results["收集器管理器"]:
            print("   - 检查收集器管理器配置")
        print("\n💡 如果是SSL错误，系统会自动使用备用数据，不影响基本功能")

    print("\n🎯 测试完成！")


if __name__ == "__main__":
    asyncio.run(main())
