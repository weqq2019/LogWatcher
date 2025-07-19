#!/usr/bin/env python3
"""
容器网络连接测试脚本
"""

import requests
import json
import socket
import ssl
import urllib3
from urllib.parse import urlparse
from config import settings

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_dns_resolution():
    """测试DNS解析"""
    print("🔍 测试1: DNS解析")
    try:
        host = "api.openai-hk.com"
        ip = socket.gethostbyname(host)
        print(f"✅ DNS解析成功: {host} -> {ip}")
        return True
    except Exception as e:
        print(f"❌ DNS解析失败: {e}")
        return False

def test_tcp_connection():
    """测试TCP连接"""
    print("\n🔍 测试2: TCP连接")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(("api.openai-hk.com", 443))
        sock.close()
        
        if result == 0:
            print("✅ TCP连接成功")
            return True
        else:
            print(f"❌ TCP连接失败: {result}")
            return False
    except Exception as e:
        print(f"❌ TCP连接异常: {e}")
        return False

def test_ssl_handshake():
    """测试SSL握手"""
    print("\n🔍 测试3: SSL握手")
    try:
        context = ssl.create_default_context()
        with socket.create_connection(("api.openai-hk.com", 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname="api.openai-hk.com") as ssock:
                print(f"✅ SSL握手成功")
                print(f"   SSL版本: {ssock.version()}")
                print(f"   加密套件: {ssock.cipher()}")
                return True
    except Exception as e:
        print(f"❌ SSL握手失败: {e}")
        return False

def test_simple_http():
    """测试简单HTTP请求"""
    print("\n🔍 测试4: 简单HTTP请求")
    try:
        response = requests.get("https://httpbin.org/ip", timeout=10, verify=False)
        print(f"✅ HTTP请求成功: {response.status_code}")
        print(f"   响应: {response.text[:100]}")
        return True
    except Exception as e:
        print(f"❌ HTTP请求失败: {e}")
        return False

def test_api_endpoint():
    """测试API端点连接"""
    print("\n🔍 测试5: API端点基础连接")
    try:
        # 不发送完整请求，只测试连接
        response = requests.get(
            "https://api.openai-hk.com", 
            timeout=10, 
            verify=False,
            headers={"User-Agent": "Mozilla/5.0 (compatible; LogWatcher/1.0)"}
        )
        print(f"✅ API端点连接成功: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ API端点连接失败: {e}")
        return False

def test_api_post():
    """测试API POST请求（最小化）"""
    print("\n🔍 测试6: API POST请求")
    try:
        url = "https://api.openai-hk.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.deepseek_api_key}",
            "User-Agent": "Mozilla/5.0 (compatible; LogWatcher/1.0)"
        }
        
        # 最小化请求
        data = {
            "model": "grok-3-deepsearch", 
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "hi"}]
        }
        
        response = requests.post(
            url, 
            headers=headers, 
            data=json.dumps(data).encode('utf-8'),
            timeout=30,
            verify=False
        )
        
        print(f"✅ API POST成功: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"   响应内容: {content}")
        else:
            print(f"   错误响应: {response.text[:200]}")
        return True
        
    except Exception as e:
        print(f"❌ API POST失败: {e}")
        return False

def main():
    print("🧪 容器网络连接测试开始\n")
    print("=" * 50)
    
    tests = [
        test_dns_resolution,
        test_tcp_connection, 
        test_ssl_handshake,
        test_simple_http,
        test_api_endpoint,
        test_api_post
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append(False)
        print("-" * 30)
    
    print(f"\n📊 测试结果汇总:")
    print(f"✅ 成功: {sum(results)}/{len(results)}")
    print(f"❌ 失败: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 所有网络测试通过！")
    else:
        print("⚠️ 部分网络测试失败，需要检查网络配置")

if __name__ == "__main__":
    main()