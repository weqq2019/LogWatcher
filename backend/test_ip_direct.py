#!/usr/bin/env python3
"""
IP直连测试 - 绕过TUN虚拟网卡
"""

import requests
import json
import urllib3
from datetime import datetime
from config import settings

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_ip_direct():
    """使用IP地址直连，绕过DNS和TUN拦截"""
    
    # 直接使用IP地址
    ip_url = "https://198.18.1.195/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Host": "api.openai-hk.com",  # 重要：保留原始Host头
        "User-Agent": "LogWatcher/1.0 (IP-Direct)",
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
    
    try:
        print("🚀 开始IP直连测试...")
        print(f"📡 目标IP: 198.18.1.195")
        print(f"🌐 Host头: api.openai-hk.com")
        
        # 创建会话，完全绕过代理和环境变量
        session = requests.Session()
        session.trust_env = False  # 关键：忽略所有环境变量
        session.proxies = {}       # 清空代理设置
        
        response = session.post(
            ip_url,
            headers=headers,
            data=json.dumps(data).encode('utf-8'),
            timeout=(10, 120),  # 连接10秒，读取2分钟
            verify=False,       # 跳过SSL验证
            allow_redirects=False
        )
        
        print(f"✅ 连接成功: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            print("📰 AI新闻收集成功:")
            print("-" * 50)
            print(content[:500] + "..." if len(content) > 500 else content)
            return True
        else:
            print(f"❌ API错误: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except requests.exceptions.ConnectTimeout:
        print("❌ 连接超时 - TUN模式可能仍在拦截")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 连接错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

if __name__ == "__main__":
    success = test_ip_direct()
    if success:
        print("\n🎉 IP直连方案可行！")
    else:
        print("\n💡 建议:")
        print("1. 暂时关闭Clash代理测试")
        print("2. 或部署到无代理环境")
        print("3. 或配置Clash排除规则")