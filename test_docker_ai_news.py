#!/usr/bin/env python3
"""
🧠 AI新闻收集功能Docker测试脚本
测试LogWatcher系统的AI新闻收集功能
"""

import requests
import json
import time
from datetime import datetime

# 🌐 配置 - 对应docker-compose.yml中的端口映射
BASE_URL = "http://localhost:28000/api"
HEADERS = {"Content-Type": "application/json"}


def test_backend_health():
    """
    🩺 测试后端健康状态
    """
    print("🔍 测试后端健康状态...")

    try:
        response = requests.get(f"{BASE_URL}/", headers=HEADERS, timeout=10)

        if response.status_code == 200:
            print("✅ 后端服务运行正常")
            return True
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 无法连接到后端服务: {e}")
        return False


def test_ai_news_collection():
    """
    🧠 测试AI新闻收集功能
    """
    print("\n🔍 测试AI新闻收集功能...")

    try:
        # 1. 触发AI新闻收集
        print("📊 1. 触发AI新闻收集...")
        response = requests.post(
            f"{BASE_URL}/news/ai/collect", headers=HEADERS, timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ 收集请求成功: {result}")

            # 2. 等待收集完成
            print("⏳ 等待10秒后检查结果...")
            time.sleep(10)

            # 3. 获取AI新闻列表
            print("📰 2. 获取AI新闻列表...")
            response = requests.get(f"{BASE_URL}/news/ai", headers=HEADERS, timeout=10)

            if response.status_code == 200:
                news_list = response.json()
                print(f"✅ 获取成功，共 {len(news_list)} 条新闻")

                # 显示最新的3条新闻
                for i, news in enumerate(news_list[:3]):
                    print(f"\n📌 新闻 {i+1}:")
                    print(f"   📰 标题: {news.get('title', '无标题')}")
                    print(f"   🏷️ 来源: {news.get('source', '未知')}")
                    print(f"   📅 时间: {news.get('created_at', '未知')}")
                    print(f"   📝 摘要: {news.get('summary', '无摘要')[:100]}...")

                return True
            else:
                print(f"❌ 获取新闻列表失败: {response.status_code} - {response.text}")
                return False

        else:
            print(f"❌ 收集请求失败: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False


def test_news_sources():
    """
    📈 测试新闻来源功能
    """
    print("\n🔍 测试新闻来源功能...")

    try:
        # 测试AI新闻来源
        response = requests.get(
            f"{BASE_URL}/news/sources/ai", headers=HEADERS, timeout=10
        )

        if response.status_code == 200:
            news_list = response.json()
            print(f"✅ AI新闻来源测试成功，共 {len(news_list)} 条新闻")
            return True
        else:
            print(f"❌ AI新闻来源测试失败: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False


def test_database_connection():
    """
    🗃️ 测试数据库连接
    """
    print("\n🔍 测试数据库连接...")

    try:
        # 通过获取新闻总数来测试数据库连接
        response = requests.get(f"{BASE_URL}/news/ai", headers=HEADERS, timeout=10)

        if response.status_code == 200:
            print("✅ 数据库连接正常")
            return True
        else:
            print(f"❌ 数据库连接异常: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False


def main():
    """
    🎯 主测试函数
    """
    print("🚀 开始Docker环境AI新闻收集测试...")
    print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API地址: {BASE_URL}")
    print("=" * 60)

    # 测试结果统计
    test_results = []

    # 1. 健康检查
    result = test_backend_health()
    test_results.append(("后端健康检查", result))

    if not result:
        print("\n❌ 后端服务未正常运行，请检查Docker容器状态")
        return

    # 2. 数据库连接测试
    result = test_database_connection()
    test_results.append(("数据库连接", result))

    # 3. AI新闻收集测试
    result = test_ai_news_collection()
    test_results.append(("AI新闻收集", result))

    # 4. 新闻来源测试
    result = test_news_sources()
    test_results.append(("新闻来源功能", result))

    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print("=" * 60)

    for test_name, passed in test_results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")

    passed_count = sum(1 for _, passed in test_results if passed)
    total_count = len(test_results)

    print(f"\n🎯 总计: {passed_count}/{total_count} 项测试通过")

    if passed_count == total_count:
        print("🎉 所有测试都通过了！AI新闻收集功能运行正常")
    else:
        print("⚠️ 部分测试失败，请检查系统配置")


if __name__ == "__main__":
    main()
