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

    def __init__(self, name: str = "ai_news"):
        """
        初始化AI新闻收集器

        Args:
            name (str): 收集器名称
        """
        super().__init__()
        self.name = name

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
        self.logger.info(f"API URL: {self.api_url}")
        self.logger.info(f"API Key: {self.api_key[:20]}...")
        self.logger.info(f"使用模型: {self.model}")  # 🔄 记录使用的模型

    def get_source_name(self) -> str:
        return "AI新闻助手"

    async def collect(self) -> List[CollectorItem]:
        """收集AI新闻项目"""
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
            import requests
            import os
            
            self.logger.info("发送API请求（简化直连模式）...")
            response = requests.post(
                self.api_url, 
                headers=headers, 
                data=json.dumps(data).encode('utf-8'),
                proxies={'http': None, 'https': None}  # 禁用代理
            )
            
            if response.status_code == 200:
                # 第一步：接收原始数据
                self.logger.info("=" * 50)
                self.logger.info("步骤1: 接收API响应数据")
                
                try:
                    result = response.content.decode("utf-8")
                    self.logger.info(f"✅ 成功接收原始响应，数据长度: {len(result)} 字符")
                    self.logger.info(f"📄 原始响应前1000字符:")
                    self.logger.info(result[:1000])
                    self.logger.info("=" * 50)
                    
                except Exception as e:
                    self.logger.error(f"❌ 步骤1失败 - 数据接收错误: {e}")
                    return self._create_fallback_news()
                
                # 第二步：解析JSON结构
                self.logger.info("步骤2: 解析JSON响应结构")
                try:
                    response_data = json.loads(result)
                    self.logger.info(f"✅ JSON解析成功")
                    self.logger.info(f"📊 响应结构键: {list(response_data.keys())}")
                    
                    if 'choices' in response_data:
                        choices = response_data.get('choices', [])
                        self.logger.info(f"✅ 找到choices数组，长度: {len(choices)}")
                        if choices and 'message' in choices[0]:
                            self.logger.info(f"✅ 找到message对象")
                        else:
                            self.logger.warning(f"⚠️ choices结构异常: {choices}")
                    else:
                        self.logger.error(f"❌ 响应中缺少choices字段")
                        
                except Exception as e:
                    self.logger.error(f"❌ 步骤2失败 - JSON解析错误: {e}")
                    self.logger.error(f"原始数据: {result[:500]}")
                    return self._create_fallback_news()
                
                # 第三步：提取AI内容
                self.logger.info("步骤3: 提取AI生成内容")
                try:
                    content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    self.logger.info(f"✅ 成功提取AI内容，长度: {len(content)} 字符")
                    
                    if content:
                        self.logger.info(f"📝 AI内容前500字符:")
                        self.logger.info(content[:500])
                        self.logger.info("=" * 50)
                    else:
                        self.logger.error(f"❌ 步骤3失败 - AI内容为空")
                        return self._create_fallback_news()
                        
                except Exception as e:
                    self.logger.error(f"❌ 步骤3失败 - 内容提取错误: {e}")
                    return self._create_fallback_news()
                
                # 第四步：进入内容解析器
                self.logger.info("步骤4: 进入AI内容解析器")
                try:
                    news_items = self._parse_ai_response(content)
                    if news_items:
                        self.logger.info(f"✅ 解析成功，生成 {len(news_items)} 条新闻")
                        return news_items
                    else:
                        self.logger.error(f"❌ 步骤4失败 - 解析器返回空结果")
                        return self._create_fallback_news()
                        
                except Exception as e:
                    self.logger.error(f"❌ 步骤4失败 - 解析器处理错误: {e}")
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
