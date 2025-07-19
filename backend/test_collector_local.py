#!/usr/bin/env python3
"""
测试AI新闻收集器（本地模式）
不调用API，使用本地测试数据
"""

import asyncio
import logging
from collectors.ai_news_collector import AINewsCollector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_collector_with_test_data():
    """测试收集器（测试模式）"""
    print("🧪 测试AI新闻收集器（测试模式 - 不调用API）")
    print("=" * 60)
    
    # 创建收集器实例（启用测试模式）
    collector = AINewsCollector(name="test_ai_news", test_mode=True)
    
    # 运行收集器
    result = await collector.run()
    
    print("\n📊 测试结果:")
    print(f"成功: {result.get('success', False)}")
    print(f"数量: {result.get('count', 0)}")
    print(f"执行时间: {result.get('execution_time', 0):.2f}秒")
    print(f"来源: {result.get('source', 'N/A')}")
    
    if result.get('success') and result.get('items'):
        print(f"\n📝 新闻列表 ({len(result['items'])} 条):")
        for i, item in enumerate(result['items'][:3], 1):  # 只显示前3条
            print(f"\n{i}. {item.title}")
            print(f"   摘要: {item.summary[:100]}...")
            print(f"   标签: {', '.join(item.tags)}")
    
    if result.get('error'):
        print(f"\n❌ 错误: {result['error']}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")

async def test_collector_with_api():
    """测试收集器（API模式）"""
    print("🌐 测试AI新闻收集器（API模式 - 调用远程API）")
    print("=" * 60)
    
    # 创建收集器实例（API模式）
    collector = AINewsCollector(name="api_ai_news", test_mode=False)
    
    # 运行收集器
    result = await collector.run()
    
    print("\n📊 测试结果:")
    print(f"成功: {result.get('success', False)}")
    print(f"数量: {result.get('count', 0)}")
    print(f"执行时间: {result.get('execution_time', 0):.2f}秒")
    print(f"来源: {result.get('source', 'N/A')}")
    
    if result.get('success') and result.get('items'):
        print(f"\n📝 新闻列表 ({len(result['items'])} 条):")
        for i, item in enumerate(result['items'][:3], 1):  # 只显示前3条
            print(f"\n{i}. {item.title}")
            print(f"   摘要: {item.summary[:100]}...")
            print(f"   标签: {', '.join(item.tags)}")
    
    if result.get('error'):
        print(f"\n❌ 错误: {result['error']}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")

async def main():
    """主函数"""
    print("🔧 AI新闻收集器测试工具")
    print("选择测试模式:")
    print("1. 测试模式 (使用本地数据，不调用API)")
    print("2. API模式 (调用远程API，产生费用)")
    print("3. 两种模式都测试")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == "1":
        await test_collector_with_test_data()
    elif choice == "2":
        confirm = input("⚠️  API模式会产生费用，确认继续？(y/N): ").strip().lower()
        if confirm == 'y':
            await test_collector_with_api()
        else:
            print("❌ 已取消API测试")
    elif choice == "3":
        await test_collector_with_test_data()
        print("\n" + "🔄" * 20)
        confirm = input("⚠️  继续API模式测试会产生费用，确认继续？(y/N): ").strip().lower()
        if confirm == 'y':
            await test_collector_with_api()
        else:
            print("❌ 已跳过API测试")
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    asyncio.run(main())