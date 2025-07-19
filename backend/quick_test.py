#!/usr/bin/env python3
import asyncio
from collectors.ai_news_collector import AINewsCollector

async def test():
    print('🧪 测试 AI 新闻收集器（测试模式）')
    collector = AINewsCollector(test_mode=True)
    result = await collector.run()
    
    print(f'✅ 成功: {result.get("success")}')
    print(f'📊 数量: {result.get("count")}')
    print(f'⏱️  时间: {result.get("execution_time", 0):.2f}秒')
    
    if result.get('items'):
        print(f'\n📝 新闻列表:')
        for i, item in enumerate(result['items'][:3], 1):
            print(f'{i}. {item.title[:80]}...')
    
    if result.get('error'):
        print(f'❌ 错误: {result["error"]}')

if __name__ == "__main__":
    asyncio.run(test())