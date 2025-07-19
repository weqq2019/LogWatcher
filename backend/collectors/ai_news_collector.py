"""
AI新闻收集器
使用AI API来获取最新的AI领域新闻
"""

import requests
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re
import logging
import time
import urllib3
import os
import httpx

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .base import BaseCollector, CollectorItem
from config import settings  # 🔄 修复导入：使用settings而不是Config


class AINewsCollector(BaseCollector):
    """AI新闻收集器"""

    def __init__(self, name: str = "ai_news", test_mode: bool = True):
        """
        初始化AI新闻收集器

        Args:
            name (str): 收集器名称
            test_mode (bool): 是否使用测试模式（不调用API，使用本地测试数据）
        """
        super().__init__()
        self.name = name
        self.test_mode = test_mode

        # 从配置获取API设置
        self.api_url = settings.deepseek_api_url  # 🔄 使用settings
        self.api_key = settings.deepseek_api_key  # 🔄 使用settings
        self.model = settings.ai_model  # 🔄 使用可配置的模型

        # 创建logger
        self.logger = logging.getLogger(__name__)

        # 使用httpx替代requests，支持HTTP/2
        import ssl
        
        # 创建自定义SSL上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')
        
        # 创建HTTP客户端，不强制使用HTTP/2
        self.client = httpx.AsyncClient(
            http2=False,  # 禁用HTTP/2，使用HTTP/1.1确保稳定性
            verify=False,  # 禁用SSL验证
            timeout=httpx.Timeout(
                connect=30.0,  # 连接超时
                read=600.0,    # 读取超时增加到10分钟
                write=30.0,    # 写入超时
                pool=60.0      # 连接池超时
            ),
            limits=httpx.Limits(
                max_keepalive_connections=1,  # 保持连接数
                max_connections=1,            # 最大连接数
                keepalive_expiry=60.0        # 连接保持时间
            )
        )
        
        # 配置代理设置 (容器内通常不需要代理)
        proxy_url = os.getenv('https_proxy') or os.getenv('HTTPS_PROXY')
        if proxy_url:
            # httpx代理配置
            self.client = httpx.AsyncClient(
                http2=False,
                verify=False,
                proxies=proxy_url,
                timeout=httpx.Timeout(connect=30.0, read=600.0, write=30.0, pool=60.0),
                limits=httpx.Limits(max_keepalive_connections=1, max_connections=1, keepalive_expiry=60.0)
            )
            self.logger.info(f"使用代理: {proxy_url}")
        else:
            self.logger.info("未配置代理，使用HTTP/1.1直连")

        self.logger.info(f"AI新闻收集器初始化完成: {self.name}")
        if self.test_mode:
            self.logger.info("🧪 测试模式：将使用本地测试数据，不调用API")
        else:
            self.logger.info(f"🌐 API模式：{self.api_url}")
            self.logger.info(f"API Key: {self.api_key[:20]}...")
            self.logger.info(f"使用模型: {self.model}")  # 🔄 记录使用的模型

    def get_source_name(self) -> str:
        return "AI新闻助手"

    async def collect(self) -> List[CollectorItem]:
        """收集AI新闻项目"""
        try:
            if self.test_mode:
                self.logger.info("🧪 使用测试模式：从本地文件读取数据")
                return await self._collect_from_test_data()
            else:
                self.logger.info("🌐 使用API模式：调用远程API")
                return await self._collect_from_api()

        except Exception as e:
            self.logger.error(f"收集AI新闻时发生错误: {str(e)}")
            return self._create_fallback_news()

    async def _collect_from_test_data(self) -> List[CollectorItem]:
        """从测试数据收集新闻（不调用API）"""
        try:
            test_file = os.path.join(os.path.dirname(__file__), '..', 'test_api_response.txt')
            
            with open(test_file, 'r', encoding='utf-8') as f:
                result = f.read()
                
            self.logger.info(f"✅ 成功读取测试数据，长度: {len(result)} 字符")
            
            # 使用同样的解析器处理测试数据
            parsed_content = self._parse_response(result)
            
            if parsed_content:
                self.logger.info(f"✅ 解析成功，内容长度: {len(parsed_content)} 字符")
                news_items = self._parse_ai_response(parsed_content)
                return news_items if news_items else self._create_fallback_news()
            else:
                self.logger.error("❌ 测试数据解析失败")
                return self._create_fallback_news()
                
        except FileNotFoundError:
            self.logger.error("❌ 测试文件未找到: test_api_response.txt")
            return self._create_fallback_news()
        except Exception as e:
            self.logger.error(f"❌ 读取测试数据失败: {e}")
            return self._create_fallback_news()

    async def _collect_from_api(self) -> List[CollectorItem]:
        """从API收集新闻（调用远程API）"""
        try:
            # 准备API请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }

            # 构建提问词
            today = datetime.now().strftime("%Y年%m月%d日")
            prompt = f"请先搜索网络获取{today}的最新AI新闻，然后整理最近10条AI新闻。开头标注当天日期。内容优先关注OpenAI、Claude、Google、Grok等大厂的最新动态。请确保搜索到真实的最新信息，新闻内容简洁清晰，无需多余解释。"

            data = {
                "max_tokens": 1200,
                "model": self.model,
                "temperature": 0.8,
                "top_p": 1,
                "presence_penalty": 1,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的AI新闻收集助手，具有网络搜索能力。请先搜索网络获取最新的AI行业新闻，然后根据用户要求整理，内容要准确、简洁、有价值。确保信息来源于真实的最新网络搜索结果。",
                    },
                    {"role": "user", "content": prompt},
                ],
            }

            # 发送API请求，使用与 test_official_api.py 相同的成功配置
            self.logger.info("发送API请求（简化直连模式）...")
            response = requests.post(
                self.api_url, 
                headers=headers, 
                data=json.dumps(data).encode('utf-8'),
                proxies={'http': None, 'https': None}  # 禁用代理
            )
            
            if response.status_code == 200:
                # 使用经过验证的解析器处理响应
                result = response.content.decode("utf-8")
                parsed_content = self._parse_response(result)
                
                if parsed_content:
                    self.logger.info(f"✅ 解析成功，内容长度: {len(parsed_content)} 字符")
                    news_items = self._parse_ai_response(parsed_content)
                    return news_items if news_items else self._create_fallback_news()
                else:
                    self.logger.error("❌ 响应解析失败")
                    return self._create_fallback_news()
            else:
                self.logger.error(f"API请求失败: {response.status_code}, {response.text}")
                return []

        except (requests.ConnectionError, requests.ReadTimeout, requests.Timeout) as e:
            self.logger.error(f"HTTP连接错误: {str(e)}")
            return self._create_fallback_news()

        except Exception as e:
            self.logger.error(f"收集AI新闻时发生错误: {str(e)}")
            return self._create_fallback_news()

    def _create_fallback_news(self) -> List[CollectorItem]:
        """创建备用新闻数据（当API调用失败时）"""
        today = datetime.now().strftime("%Y年%m月%d日")

        fallback_items = [
            CollectorItem(
                title=f"AI新闻收集服务暂时不可用 - {today}",
                summary="由于网络连接问题，AI新闻收集服务暂时不可用。请稍后重试。",
                content="AI新闻收集服务遇到网络连接问题，可能是SSL证书验证或网络超时导致。系统将在下次调用时自动重试。",
                url="",
                source=self.get_source_name(),
                author="系统",
                published_at=datetime.now(),
                tags=["系统通知", "服务状态"],
                model=self.model,
            ),
            CollectorItem(
                title="AI行业动态关注建议",
                summary="建议关注OpenAI、Claude、Google、Grok等主要AI公司的官方动态。",
                content="在AI新闻收集服务不可用期间，建议直接关注以下渠道：\n1. OpenAI官方博客和Twitter\n2. Anthropic Claude更新\n3. Google AI研究进展\n4. Grok AI发布动态\n5. 主要科技媒体的AI版块",
                url="",
                source=self.get_source_name(),
                author="系统",
                published_at=datetime.now(),
                tags=["AI动态", "关注建议"],
                model=self.model,
            ),
        ]

        return fallback_items

    def _parse_ai_response(self, content: str) -> List[CollectorItem]:
        """解析AI返回的新闻内容"""
        items = []
        
        self.logger.info("🔍 解析器步骤1: 检查输入内容")
        self.logger.info(f"📊 原始内容长度: {len(content)} 字符")
        self.logger.info(f"📄 原始内容前200字符: {content[:200]}")

        # 步骤2：清理内容
        self.logger.info("🔍 解析器步骤2: 清理AI思考标签")
        original_length = len(content)
        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
        
        self.logger.info(f"✅ 清理完成，从 {original_length} 字符缩减到 {len(content)} 字符")
        if len(content) < original_length:
            self.logger.info(f"🗑️ 移除了 {original_length - len(content)} 字符的思考内容")
        
        if len(content.strip()) > 0:
            self.logger.info(f"📝 清理后内容前300字符: {content[:300]}")
        else:
            self.logger.error(f"❌ 清理后内容为空！")
        
        # 步骤3：尝试解析多条新闻
        self.logger.info("🔍 解析器步骤3: 尝试解析多条新闻")
        
        if len(content.strip()) > 100:
            self.logger.info(f"✅ 内容长度足够({len(content.strip())} > 100)，开始解析")
            self.logger.info(f"📝 内容前500字符: {content[:500]}")
        else:
            self.logger.warning(f"⚠️ 内容长度不足({len(content.strip())} <= 100)，使用备用方案")
        
        # 步骤4：多种解析策略
        self.logger.info("🔍 解析器步骤4: 尝试多种解析策略")
        
        # 策略1: 按编号分割 (1. 2. 3. ...)
        self.logger.info("📋 策略1: 按编号分割新闻")
        news_sections = re.split(r"\n(?=\d+\.)", content)
        if len(news_sections) > 1:
            self.logger.info(f"✅ 策略1成功：找到 {len(news_sections)} 个编号段落")
        
        # 策略2: 按标题格式分割 (**标题**: 内容)
        if len(news_sections) <= 1:
            self.logger.info("📋 策略2: 按标题格式分割")
            news_sections = re.split(r"\n(?=\*\*[^*]+\*\*)", content)
            if len(news_sections) > 1:
                self.logger.info(f"✅ 策略2成功：找到 {len(news_sections)} 个标题段落")
        
        # 策略3: 按公司名称分割
        if len(news_sections) <= 1:
            self.logger.info("📋 策略3: 按公司名称分割")
            company_pattern = r"\n(?=(?:OpenAI|Claude|Google|Grok|Anthropic|xAI))"
            news_sections = re.split(company_pattern, content)
            if len(news_sections) > 1:
                self.logger.info(f"✅ 策略3成功：找到 {len(news_sections)} 个公司段落")
        
        # 寻找日期标记（保留原逻辑）
        date_pattern = r"(\d{4}年\d{1,2}月\d{1,2}日)"
        date_match = re.search(date_pattern, content)
        if date_match:
            content = content[date_match.start() :]

        self.logger.info(f"🔍 解析器步骤5: 处理 {len(news_sections)} 个段落")
        
        for i, section in enumerate(news_sections):
            section = section.strip()
            if not section or len(section) < 20:
                self.logger.info(f"⏭️ 跳过段落{i+1}: 长度不足({len(section)})")
                continue

            self.logger.info(f"📝 处理段落{i+1}: {section[:100]}...")
            
            # 提取新闻标题和内容
            lines = section.split("\n")
            title_line = lines[0] if lines else ""

            # 多种标题提取策略
            title = self._extract_title(title_line, section)
            
            if title and len(title) > 5:
                # 构建完整内容
                full_content = "\n".join(lines[1:]) if len(lines) > 1 else section
                
                # 如果内容太短，使用整个段落
                if len(full_content.strip()) < 50:
                    full_content = section

                # 创建新闻项
                item = CollectorItem(
                    title=title,
                    summary=(
                        full_content[:200] + "..."
                        if len(full_content) > 200
                        else full_content
                    ),
                    content=full_content,
                    url="",
                    source=self.get_source_name(),
                    author=f"{self.model} AI助手",
                    published_at=datetime.now(),
                    tags=["AI新闻", "科技动态"],
                    model=self.model,
                )
                items.append(item)
                self.logger.info(f"✅ 创建新闻项{len(items)}: {title[:50]}...")
            else:
                self.logger.info(f"⏭️ 跳过段落{i+1}: 无有效标题")

        # 🔄 如果没有找到结构化新闻，尝试简单分割
        if not items and content:
            # 按双换行分割
            sections = content.split("\n\n")
            for section in sections:
                section = section.strip()
                if len(section) > 30 and self._contains_ai_keywords(section):
                    items.append(
                        CollectorItem(
                            title=f"AI新闻 - {datetime.now().strftime('%Y-%m-%d')}",
                            summary=(
                                section[:200] + "..." if len(section) > 200 else section
                            ),
                            content=section,
                            url="",
                            source=self.get_source_name(),
                            author="AI助手",
                            published_at=datetime.now(),
                            tags=["AI", "科技新闻"],
                            model=self.model,
                        )
                    )

        # 🔄 最后的备用方案
        if not items and content:
            items.append(
                CollectorItem(
                    title=f"AI新闻摘要 - {datetime.now().strftime('%Y-%m-%d')}",
                    summary=content[:200] + "..." if len(content) > 200 else content,
                    content=content,
                    url="",
                    source=self.get_source_name(),
                    author="AI助手",
                    published_at=datetime.now(),
                    tags=["AI", "科技新闻", "每日摘要"],
                    model=self.model,
                )
            )

        return items[:10]  # 🔄 限制返回最多10条新闻

    def _parse_response(self, response_text):
        """解析API响应，提取AI新闻内容（从test_official_api.py移植）"""
        try:
            # 先尝试直接解析JSON
            response_data = json.loads(response_text)
            
            # 检查响应格式
            if 'choices' not in response_data:
                self.logger.error("响应格式错误：缺少 'choices' 字段")
                return None
                
            if not response_data['choices']:
                self.logger.error("响应为空：'choices' 数组为空")
                return None
                
            # 提取内容
            choice = response_data['choices'][0]
            if 'message' not in choice:
                self.logger.error("响应格式错误：缺少 'message' 字段")
                return None
                
            message = choice['message']
            if 'content' not in message:
                self.logger.error("响应格式错误：缺少 'content' 字段")
                return None
                
            content = message['content']
            
            self.logger.info("=" * 50)
            self.logger.info("解析成功！AI新闻内容:")
            self.logger.info("=" * 50)
            self.logger.info(content[:500] + "..." if len(content) > 500 else content)
            self.logger.info("=" * 50)
            
            return content
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON直接解析失败: {e}")
            self.logger.info("尝试修复JSON格式...")
            
            try:
                # 尝试手动修复JSON格式问题
                fixed_content = self._fix_json_content(response_text)
                if fixed_content:
                    self.logger.info("=" * 50)
                    self.logger.info("修复JSON后解析成功！AI新闻内容:")
                    self.logger.info("=" * 50)
                    self.logger.info(fixed_content[:500] + "..." if len(fixed_content) > 500 else fixed_content)
                    self.logger.info("=" * 50)
                    return fixed_content
                else:
                    self.logger.error("JSON修复失败")
                    return None
                    
            except Exception as fix_error:
                self.logger.error(f"JSON修复过程中发生错误: {fix_error}")
                self.logger.error("原始响应内容（前500字符）:")
                self.logger.error(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                return None
                
        except Exception as e:
            self.logger.error(f"解析响应时发生错误: {e}")
            return None

    def _fix_json_content(self, response_text):
        """尝试修复损坏的JSON格式（从test_official_api.py移植）"""
        try:
            # 查找content字段的开始位置
            content_start = response_text.find('"content":"')
            if content_start == -1:
                self.logger.error("找不到content字段")
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
                
            self.logger.error("未能找到content字段的结束位置")
            return None
            
        except Exception as e:
            self.logger.error(f"修复JSON时发生错误: {e}")
            return None

    def _is_valid_news_title(self, line: str) -> bool:
        """判断是否是有效的新闻标题"""
        # 过滤掉思考过程
        if any(
            keyword in line.lower()
            for keyword in ["<think>", "first,", "let me", "i should", "i need"]
        ):
            return False

        # 匹配编号开头的新闻
        if re.match(r"^\d+\.\s*", line):
            return True

        # 包含AI公司名称且长度合理
        ai_companies = [
            "OpenAI",
            "Claude",
            "Google",
            "Grok",
            "Microsoft",
            "Meta",
            "Anthropic",
        ]
        if any(company in line for company in ai_companies) and 20 < len(line) < 150:
            return True

        return False

    def _contains_ai_keywords(self, text: str) -> bool:
        """检查文本是否包含AI关键词"""
        keywords = [
            "AI",
            "人工智能",
            "OpenAI",
            "Claude",
            "Google",
            "Grok",
            "机器学习",
            "深度学习",
        ]
        return any(keyword in text for keyword in keywords)

    def _extract_title(self, title_line: str, full_section: str) -> str:
        """多种策略提取新闻标题"""
        if not title_line:
            return ""
            
        # 策略1: **标题** 格式
        bold_match = re.search(r'\*\*([^*]+)\*\*', title_line)
        if bold_match:
            title = bold_match.group(1).strip()
            if len(title) > 5:
                return title
        
        # 策略2: 编号格式 (1. 标题, 2. 标题)
        number_match = re.search(r'^\d+[.、)\s]+(.+?)(?:\*\*|：|:|\n|$)', title_line)
        if number_match:
            title = number_match.group(1).strip()
            if len(title) > 5:
                return title
        
        # 策略3: 公司名开头
        company_match = re.search(r'^(OpenAI|Claude|Google|Grok|Anthropic|xAI)[^。！？]*[。！？]?', title_line)
        if company_match:
            title = company_match.group(0).strip()
            if len(title) > 10:
                return title
        
        # 策略4: 直接使用清理后的标题行
        cleaned = self._clean_title(title_line)
        if len(cleaned) > 5 and self._is_valid_news_title(title_line):
            return cleaned
        
        # 策略5: 从段落中提取第一句话作为标题
        sentences = re.split(r'[。！？.]', full_section)
        if sentences and len(sentences[0].strip()) > 10:
            return sentences[0].strip()[:100]
        
        return ""

    def _clean_title(self, title: str) -> str:
        """清理标题格式"""
        # 移除编号和特殊字符
        title = re.sub(r"^\d+[.、)\s]+", "", title)
        title = re.sub(r"^[\*\-•\s]+", "", title)
        title = title.strip()

        # 限制标题长度
        if len(title) > 100:
            title = title[:100] + "..."

        return title

    async def run(self) -> Dict[str, Any]:
        """运行收集器"""
        if not self.enabled:
            return {
                "success": False,
                "error": "收集器已禁用",
                "count": 0,
                "execution_time": 0,
            }

        start_time = time.time()

        try:
            self.logger.info(f"开始运行AI新闻收集器: {self.name}")

            # 收集新闻项目
            items = await self.collect()

            execution_time = time.time() - start_time

            if items:
                self.logger.info(f"成功收集到 {len(items)} 条AI新闻")
                return {
                    "success": True,
                    "count": len(items),
                    "items": items,
                    "execution_time": execution_time,
                    "source": self.get_source_name(),
                }
            else:
                return {
                    "success": False,
                    "error": "未收集到任何新闻",
                    "count": 0,
                    "execution_time": execution_time,
                }

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"AI新闻收集器运行失败: {str(e)}"
            self.logger.error(error_msg)
            # 打印详细的异常信息
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": error_msg,
                "count": 0,
                "execution_time": execution_time,
            }

    def __str__(self):
        return f"AINewsCollector(name={self.name}, model={self.model})"
