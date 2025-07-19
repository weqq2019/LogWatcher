import requests
import json
import argparse
from datetime import datetime
from config import settings

def read_test_data():
    """从测试文件读取API响应数据"""
    import os
    test_file = os.path.join(os.path.dirname(__file__), 'test_api_response.txt')
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"测试文件 {test_file} 未找到")
        return None
    except Exception as e:
        print(f"读取测试文件时发生错误: {e}")
        return None

def call_api():
    """调用实际API获取数据"""
    url = "https://api.openai-hk.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.deepseek_api_key}"
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
                "content": f"请先搜索网络获取{datetime.now().strftime('%Y年%m月%d日')}的最新AI新闻，然后整理最近10条AI新闻。开头标注当天日期。内容优先关注OpenAI、Claude、Google、Grok等大厂的最新动态。请确保搜索到真实的最新信息，新闻内容简洁清晰，无需多余解释。"
            }
        ]
    }

    try:
        response = requests.post(
            url, 
            headers=headers, 
            data=json.dumps(data).encode('utf-8'),
            proxies={'http': None, 'https': None}  # 禁用代理
        )
        return response.content.decode("utf-8")
    except Exception as e:
        print(f"API调用失败: {e}")
        return None

def parse_response(response_text):
    """解析API响应，提取AI新闻内容"""
    try:
        # 先尝试直接解析JSON
        response_data = json.loads(response_text)
        
        # 检查响应格式
        if 'choices' not in response_data:
            print("响应格式错误：缺少 'choices' 字段")
            return None
            
        if not response_data['choices']:
            print("响应为空：'choices' 数组为空")
            return None
            
        # 提取内容
        choice = response_data['choices'][0]
        if 'message' not in choice:
            print("响应格式错误：缺少 'message' 字段")
            return None
            
        message = choice['message']
        if 'content' not in message:
            print("响应格式错误：缺少 'content' 字段")
            return None
            
        content = message['content']
        
        print("=" * 50)
        print("解析成功！AI新闻内容:")
        print("=" * 50)
        print(content)
        print("=" * 50)
        
        return content
        
    except json.JSONDecodeError as e:
        print(f"JSON直接解析失败: {e}")
        print("尝试修复JSON格式...")
        
        try:
            # 尝试手动修复JSON格式问题
            fixed_content = fix_json_content(response_text)
            if fixed_content:
                print("=" * 50)
                print("修复JSON后解析成功！AI新闻内容:")
                print("=" * 50)
                print(fixed_content)
                print("=" * 50)
                return fixed_content
            else:
                print("JSON修复失败")
                return None
                
        except Exception as fix_error:
            print(f"JSON修复过程中发生错误: {fix_error}")
            print("原始响应内容（前500字符）:")
            print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
            return None
            
    except Exception as e:
        print(f"解析响应时发生错误: {e}")
        return None

def fix_json_content(response_text):
    """尝试修复损坏的JSON格式"""
    try:
        # 查找content字段的开始位置
        content_start = response_text.find('"content":"')
        if content_start == -1:
            print("找不到content字段")
            return None
            
        # 找到content内容的开始位置
        content_value_start = content_start + len('"content":"')
        
        # 查找content字段的结束位置
        # 从content值开始，查找下一个字段的开始或对象的结束
        pos = content_value_start
        quote_count = 0
        escape_next = False
        
        while pos < len(response_text):
            char = response_text[pos]
            
            if escape_next:
                escape_next = False
                pos += 1
                continue
                
            if char == '\\':
                escape_next = True
                pos += 1
                continue
                
            if char == '"':
                quote_count += 1
                # 查找content值结束的引号，然后是逗号或右大括号
                if quote_count > 0 and pos + 1 < len(response_text):
                    next_chars = response_text[pos+1:pos+3]
                    if next_chars.startswith(',"') or next_chars.startswith('}'):
                        # 找到了content的结束位置
                        content_value = response_text[content_value_start:pos]
                        
                        # 清理content内容，移除多余的转义字符
                        content_value = content_value.replace('\\"', '"')
                        content_value = content_value.replace('\\n', '\n')
                        content_value = content_value.replace('\\t', '\t')
                        
                        return content_value
                        
            pos += 1
            
        print("未能找到content字段的结束位置")
        return None
        
    except Exception as e:
        print(f"修复JSON时发生错误: {e}")
        return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI新闻收集器测试工具')
    parser.add_argument('--test', action='store_true', help='使用测试数据而不是调用API')
    parser.add_argument('--api', action='store_true', help='调用实际API（默认行为）')
    
    args = parser.parse_args()
    
    # 默认使用测试模式，除非明确指定 --api
    use_test_mode = args.test or not args.api
    
    if use_test_mode:
        print("📝 使用测试模式：从本地文件读取数据")
        result = read_test_data()
        if result is None:
            print("❌ 测试数据读取失败")
            return
    else:
        print("🌐 使用API模式：调用远程API")
        result = call_api()
        if result is None:
            print("❌ API调用失败")
            return
    
    # 解析响应
    parsed_content = parse_response(result)
    
    if parsed_content:
        print("\n✅ 解析器测试成功")
    else:
        print("\n❌ 解析器测试失败")

if __name__ == "__main__":
    main()