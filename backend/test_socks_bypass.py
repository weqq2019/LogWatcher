#!/usr/bin/env python3
"""
SOCKS5代理绕过TUN - 最后尝试
"""

import requests
import json
import urllib3
from datetime import datetime
from config import settings

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_socks_bypass():
    """使用SOCKS5代理绕过TUN"""
    
    url = "https://api.openai-hk.com/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "User-Agent": "LogWatcher/1.0 (SOCKS-Bypass)",
        "Connection": "close"
    }
    
    data = {
        "max_tokens": 1200,
        "model": "grok-3-deepsearch", 
        "temperature": 0.8,
        "top_p": 1,
        "presence_penalty": 1,
        "messages": [
            {
                "role": "system",
                "content": "你是一个专业的AI新闻收集助手，具有网络搜索能力。请先搜索网络获取最新的AI行业新闻，然后根据用户要求整理，内容要准确、简洁、有价值。确保信息来源于真实的最新网络搜索结果。"
            },
            {
                "role": "user", 
                "content": f"请先搜索网络获取{datetime.now().strftime('%Y年%m月%d日')}的最新AI新闻，然后整理最近5条AI新闻。开头标注当天日期。内容优先关注OpenAI、Claude、Google、Grok等大厂的最新动态。请确保搜索到真实的最新信息，新闻内容简洁清晰，无需多余解释。"
            }
        ]
    }
    
    # 尝试多种代理配置
    proxy_configs = [
        # 1. 无代理（强制清空）
        {"name": "无代理", "proxies": {}},
        
        # 2. 本地SOCKS5（如果Clash提供）
        {"name": "本地SOCKS5", "proxies": {
            'http': 'socks5://127.0.0.1:17890',
            'https': 'socks5://127.0.0.1:17890'
        }},
        
        # 3. 本地HTTP代理
        {"name": "本地HTTP", "proxies": {
            'http': 'http://127.0.0.1:17890',
            'https': 'http://127.0.0.1:17890'
        }},
        
        # 4. 显式绕过
        {"name": "显式绕过", "proxies": {
            'http': None,
            'https': None
        }},
    ]
    
    for config in proxy_configs:
        print(f"\n🚀 尝试配置: {config['name']}")
        
        try:
            session = requests.Session()
            session.trust_env = False
            
            # 设置代理
            if config['proxies']:
                session.proxies.update(config['proxies'])
                print(f"   代理设置: {config['proxies']}")
            else:
                session.proxies = {}
                print("   无代理模式")
            
            response = session.post(
                url,
                headers=headers,
                data=json.dumps(data).encode('utf-8'),
                timeout=(10, 120),
                verify=False,
                allow_redirects=False
            )
            
            print(f"✅ 连接成功: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                print("📰 AI新闻收集成功:")
                print("-" * 50)
                print(content[:500] + "..." if len(content) > 500 else content)
                print(f"\n🎉 方案 '{config['name']}' 可行！")
                return True
            else:
                print(f"❌ API错误: {response.status_code}")
                print(f"响应: {response.text[:200]}")
                
        except requests.exceptions.ConnectTimeout:
            print(f"❌ 连接超时 - {config['name']} 无效")
        except requests.exceptions.ConnectionError as e:
            print(f"❌ 连接错误 - {config['name']}: {e}")
        except Exception as e:
            print(f"❌ 其他错误 - {config['name']}: {e}")
    
    return False

if __name__ == "__main__":
    print("🧪 SOCKS5代理绕过测试")
    print("=" * 50)
    
    success = test_socks_bypass()
    
    if not success:
        print("\n💡 所有方案都失败了，建议:")
        print("1. 临时关闭 Clash TUN 模式测试")
        print("2. 部署到无代理的服务器环境")
        print("3. 使用 Clash 的 Rule 模式替代 TUN 模式")
        print("4. 在 Clash 配置中添加更精确的排除规则")