#!/usr/bin/env python3
import sys
import os

sys.path.append("/app")

from collectors.cursor_collector import CursorCollector
import asyncio


async def test_collect():
    print("🔄 开始测试动态采集功能...")

    collector = CursorCollector()
    results = await collector.collect()

    print(f"✅ 采集完成，共获取 {len(results)} 个版本")

    if results:
        print(f'📋 最新版本: {results[0].extra_data.get("version", "unknown")}')
        print(f"📋 标题: {results[0].title}")

        # 显示采集信息
        if "collection_info" in results[0].extra_data:
            info = results[0].extra_data["collection_info"]
            print(f"📊 采集统计:")
            print(f'   - 总版本数: {info.get("total_versions", 0)}')
            print(f'   - 新版本数: {info.get("new_versions", 0)}')
            print(f'   - 已存在版本数: {info.get("existing_versions", 0)}')
            print(f'   - API调用次数: {info.get("api_calls_made", 0)}')

            # 显示处理详情
            if "processing_details" in info:
                print(f"📋 处理详情:")
                for detail in info["processing_details"]:
                    print(
                        f'   - {detail.get("version", "unknown")}: {detail.get("message", "no message")}'
                    )
    else:
        print("❌ 没有获取到任何版本信息")


if __name__ == "__main__":
    asyncio.run(test_collect())
