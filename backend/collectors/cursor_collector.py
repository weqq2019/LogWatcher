import requests
import json
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re
import time
from .base import BaseCollector, CollectorItem
from config import settings
from websocket_manager import ProgressReporter


class CursorCollector(BaseCollector):
    """Cursor IDE 更新日志采集器"""

    def __init__(self):
        super().__init__()
        self.name = "cursor_collector"
        self.description = "Cursor IDE 更新日志采集器"
        self.url = "https://cursor.com/changelog"
        self.progress_reporter = ProgressReporter("cursor_collection")
        self.db_session = None  # 数据库会话，由路由设置

    def _print_progress(
        self, current: int, total: int, message: str, extra_info: str = ""
    ):
        """打印进度条"""
        percentage = (current / total) * 100 if total > 0 else 0
        bar_length = 20
        filled_length = int(bar_length * current // total) if total > 0 else 0
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        print(
            f"📊 [{bar}] {percentage:.1f}% ({current}/{total}) {message} {extra_info}"
        )

    async def collect(self) -> List[CollectorItem]:
        """
        采集 Cursor 更新日志
        """
        try:
            # 发送开始状态
            await self.progress_reporter.report_status(
                "started", "开始采集 Cursor 更新日志..."
            )

            print("🔄 开始采集 cursor_collector 更新日志...")
            start_time = time.time()

            # 采集信息统计
            collection_info = {
                "total_versions": 0,
                "new_versions": 0,
                "existing_versions": 0,
                "api_calls_made": 0,
                "processing_details": [],
                "total_time": 0,
            }

            # 步骤1: 获取网页数据
            await self.progress_reporter.report_status(
                "processing", "正在获取 Cursor 网站数据..."
            )

            print("📥 正在获取 Cursor 网站数据...")
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            print("✅ 成功获取网站数据")

            # 步骤2: 解析HTML
            await self.progress_reporter.report_status(
                "processing", "正在解析HTML页面..."
            )

            print("🔍 正在解析HTML页面...")
            soup = BeautifulSoup(response.text, "html.parser")
            versions = self._parse_versions(soup)
            collection_info["total_versions"] = len(versions)

            # 发送解析完成状态
            await self.progress_reporter.report_status(
                "processing",
                f"解析完成，找到 {len(versions)} 个版本",
                {"versions_found": len(versions)},
            )

            print(f"📋 找到 {len(versions)} 个版本，开始处理...")

            if not versions:
                await self.progress_reporter.report_status(
                    "completed", "未找到任何版本，采集完成"
                )
                return []

            # 步骤3: 处理版本数据
            await self.progress_reporter.report_status(
                "processing", "开始处理版本数据..."
            )

            print(f"\n🔄 开始处理版本数据...")
            results = []

            for i, version in enumerate(versions):
                version_start_time = time.time()
                current_progress = i + 1

                # 发送进度更新
                await self.progress_reporter.report_progress(
                    current_progress,
                    len(versions),
                    f"处理版本 {version['version']}",
                    {
                        "version": version["version"],
                        "release_date": version["release_date"],
                        "title": (
                            version["title"][:100] + "..."
                            if len(version["title"]) > 100
                            else version["title"]
                        ),
                    },
                )

                # 打印进度
                self._print_progress(
                    current_progress,
                    len(versions),
                    f"处理版本 {version['version']}",
                    f"⏱️ 已用时 {time.time() - start_time:.1f}s",
                )

                # 检查版本是否已存在
                existing = self._check_existing_version(version["version"])
                if existing:
                    # 版本已存在，跳过API调用
                    await self.progress_reporter.report_version_progress(
                        version["version"],
                        "skipped",
                        f"版本 {version['version']} 已存在，跳过API调用",
                        api_calls=0,
                        processing_time=time.time() - version_start_time,
                    )

                    print(f"📋 版本 {version['version']} 已存在，跳过API调用")
                    collection_info["existing_versions"] += 1

                    collection_info["processing_details"].append(
                        {
                            "version": version["version"],
                            "status": "existing",
                            "message": f"版本 {version['version']} 已存在，跳过API调用",
                            "api_calls": 0,
                            "processing_time": time.time() - version_start_time,
                        }
                    )

                    # 创建 CollectorItem（从数据库获取）
                    if existing:
                        item = CollectorItem(
                            title=f"{version['title']} ({existing.translated_title})",
                            summary=f"Cursor {version['version']} 更新",
                            content=existing.original_content,
                            url=existing.url,
                            source="Cursor",
                            published_at=existing.release_date,
                            tags=["cursor", "ide", "update"],
                            extra_data={
                                "version": existing.version,
                                "release_date": existing.release_date.isoformat(),
                                "original_title": version["title"],
                                "translated_title": existing.translated_title,
                                "original_content": existing.original_content,
                                "translated_content": existing.translated_content,
                                "analysis": existing.analysis,
                                "is_major": existing.is_major,
                                "collection_status": "existing",
                            },
                        )
                        results.append(item)
                        continue

                # 💰 只有新版本才会调用API
                await self.progress_reporter.report_version_progress(
                    version["version"],
                    "processing",
                    f"新版本 {version['version']}，开始API调用...",
                )

                print(f"\n🆕 新版本 {version['version']}，开始API调用...")
                collection_info["new_versions"] += 1
                collection_info["api_calls_made"] += 1  # 现在只需要1次API调用

                # API调用进度显示
                api_start_time = time.time()

                # 一次性完成翻译和分析
                await self.progress_reporter.report_status(
                    "processing", f"正在进行AI翻译和分析 - 版本 {version['version']}"
                )

                print(f"   🔄 [1/1] 正在进行AI翻译和分析...")
                api_result = self._translate_and_analyze_with_deepseek(
                    version["title"], version["content"]
                )
                print(
                    f"   ✅ [1/1] AI翻译和分析完成 (用时 {time.time() - api_start_time:.1f}s)"
                )

                total_api_time = time.time() - api_start_time
                print(
                    f"   🎉 版本 {version['version']} API调用完成 (总用时 {total_api_time:.1f}s)"
                )

                # 发送版本完成状态
                await self.progress_reporter.report_version_progress(
                    version["version"],
                    "completed",
                    f"版本 {version['version']} 处理完成",
                    api_calls=1,
                    processing_time=time.time() - version_start_time,
                )

                # 解析API返回结果
                translated_title = api_result.get("translated_title", "翻译失败")
                translated_content = api_result.get("translated_content", "翻译失败")
                analysis = api_result.get("analysis", "分析失败")

                collection_info["processing_details"].append(
                    {
                        "version": version["version"],
                        "status": "new",
                        "message": f"新版本 {version['version']}，已完成API调用",
                        "api_calls": 1,  # 现在只需要1次
                        "processing_time": time.time() - version_start_time,
                        "api_time": total_api_time,
                    }
                )

                # 创建 CollectorItem
                item = CollectorItem(
                    title=f"{version['title']} ({translated_title})",
                    summary=f"Cursor {version['version']} 更新",
                    content=version["content"],
                    url=self.url + f"#{version['version']}",
                    source="Cursor",
                    published_at=datetime.fromisoformat(version["release_date"]),
                    tags=["cursor", "ide", "update"],
                    extra_data={
                        "version": version["version"],
                        "release_date": version["release_date"],
                        "original_title": version["title"],
                        "translated_title": translated_title,
                        "original_content": version["content"],
                        "translated_content": translated_content,
                        "analysis": analysis,
                        "is_major": version["version"].count(".")
                        == 1,  # 主版本如 1.0, 1.1
                        "collection_status": "new",
                    },
                )

                results.append(item)

            # 最终进度显示
            await self.progress_reporter.report_progress(
                len(versions), len(versions), "所有版本处理完成"
            )

            self._print_progress(
                len(versions),
                len(versions),
                "处理完成",
                f"⏱️ 总用时 {time.time() - start_time:.1f}s",
            )

            # 汇总统计
            total_time = time.time() - start_time
            collection_info["total_time"] = total_time

            # 发送最终统计
            await self.progress_reporter.report_stats(
                {
                    "total_versions": collection_info["total_versions"],
                    "new_versions": collection_info["new_versions"],
                    "existing_versions": collection_info["existing_versions"],
                    "api_calls_made": collection_info["api_calls_made"],
                    "total_time": total_time,
                }
            )

            # 发送完成状态
            await self.progress_reporter.report_status(
                "completed",
                f"采集完成！共处理 {collection_info['total_versions']} 个版本",
                collection_info,
            )

            print(f"\n🎉 采集完成！")
            print(f"📊 统计信息：")
            print(f"   📋 总版本数: {collection_info['total_versions']}")
            print(f"   🆕 新版本数: {collection_info['new_versions']}")
            print(f"   📚 已存在版本: {collection_info['existing_versions']}")
            print(f"   💰 API调用次数: {collection_info['api_calls_made']}")
            print(f"   ⏱️ 总用时: {total_time:.1f}s")
            if collection_info["new_versions"] > 0:
                avg_time = total_time / collection_info["new_versions"]
                print(f"   📈 平均每个新版本用时: {avg_time:.1f}s")

            # 将采集信息存储到结果中
            if results:
                results[0].extra_data["collection_info"] = collection_info

            return results

        except Exception as e:
            # 发送错误状态
            await self.progress_reporter.report_status(
                "error", f"采集 Cursor 更新日志失败: {str(e)}"
            )

            print(f"\n❌ 采集 Cursor 更新日志失败: {e}")
            return []

    def _check_existing_version(self, version: str):
        """检查版本是否已存在于数据库中"""
        if not self.db_session:
            return None

        try:
            from models import CursorUpdate

            existing = (
                self.db_session.query(CursorUpdate)
                .filter(CursorUpdate.version == version)
                .first()
            )
            return existing
        except Exception as e:
            print(f"检查版本时出错: {e}")
            return None

    def _parse_versions(self, soup: BeautifulSoup) -> List[Dict]:
        """解析版本信息 - 基于实际页面结构优化"""
        versions = []

        try:
            print("🔍 开始解析HTML页面...")

            # 基于实际页面结构的解析策略
            print("   🔄 查找版本信息...")

            # 1. 查找所有日期
            page_text = soup.get_text()
            date_pattern = re.compile(r"([A-Za-z]+ \d+, \d{4})")
            dates = date_pattern.findall(page_text)
            print(f"   📅 找到 {len(dates)} 个日期: {dates}")

            # 2. 智能版本号查找 - 多策略组合
            valid_versions = []

            # 策略1: 查找页面中明确标记的版本号（文本内容）
            version_elements = soup.find_all(string=re.compile(r"^\d+\.\d+$"))
            for element in version_elements:
                version = element.strip()
                if version and re.match(r"^\d+\.\d+$", version):
                    if self._is_valid_cursor_version(version):
                        valid_versions.append(version)

            # 策略2: 智能元素搜索 - 基于语义而非特定标签
            # 查找可能包含版本号的元素（不限于p标签）
            potential_version_elements = soup.find_all(
                lambda tag: tag.name in ["p", "span", "div", "h1", "h2", "h3", "strong"]
                and tag.get_text().strip()
                and re.match(r"^\d+\.\d+$", tag.get_text().strip())
            )

            for element in potential_version_elements:
                version = element.get_text().strip()
                if self._is_valid_cursor_version(version):
                    # 验证上下文 - 确保是版本号而非其他数字
                    if self._validate_version_context(element):
                        valid_versions.append(version)

            # 策略3: CSS选择器搜索 - 针对常见的版本号容器
            version_selectors = [
                # 常见的版本号容器模式
                '[class*="version"]',
                '[class*="tag"]',
                '[class*="badge"]',
                '[class*="label"]',
                # 基于您提供的HTML结构
                'div[class*="flex"] p',
                'div[class*="items-center"] p',
                # 通用的可能包含版本号的元素
                'p:not([class*="text-"]):not([class*="description"])',
            ]

            for selector in version_selectors:
                try:
                    elements = soup.select(selector)
                    for element in elements:
                        text = element.get_text().strip()
                        if re.match(
                            r"^\d+\.\d+$", text
                        ) and self._is_valid_cursor_version(text):
                            valid_versions.append(text)
                except Exception:
                    continue

            # 策略4: 如果以上方法找到的版本不够，使用文本模式匹配
            if len(valid_versions) < 3:
                print("   🔄 使用文本模式匹配策略...")
                version_pattern = re.compile(r"\b(\d+\.\d+)\b")
                version_matches = version_pattern.findall(page_text)

                for version in version_matches:
                    if self._is_valid_cursor_version(version):
                        valid_versions.append(version)

            # 去重并按版本号排序
            unique_versions = list(set(valid_versions))
            unique_versions.sort(
                key=lambda x: [int(v) for v in x.split(".")], reverse=True
            )

            # 智能过滤：优先选择已知版本，同时支持新版本
            filtered_versions = self._filter_cursor_versions(unique_versions)

            # 限制版本数量，取前6个最新版本
            unique_versions = filtered_versions[:6]

            print(f"   🔢 找到 {len(unique_versions)} 个版本号: {unique_versions}")

            # 3. 查找所有h2标签（版本标题）
            h2_headers = soup.find_all("h2")
            version_titles = []
            for h2 in h2_headers:
                title = h2.get_text().strip()
                if title.lower() != "changelog":  # 跳过主标题
                    version_titles.append(title)

            print(f"   📄 找到 {len(version_titles)} 个版本标题")

            # 4. 将版本号、日期和标题配对
            version_info_pairs = []

            # 确保我们有足够的数据来配对
            min_count = min(len(unique_versions), len(dates), len(version_titles))

            for i in range(min_count):
                version_info_pairs.append(
                    (unique_versions[i], dates[i], version_titles[i])
                )

            # 如果还有剩余的版本号，使用估算的数据
            if len(unique_versions) > min_count:
                for i in range(min_count, len(unique_versions)):
                    version_info_pairs.append(
                        (
                            unique_versions[i],
                            (
                                dates[0] if dates else "January 1, 2025"
                            ),  # 使用第一个日期或默认日期
                            f"Cursor {unique_versions[i]} Update",
                        )
                    )

            print(f"   📋 创建了 {len(version_info_pairs)} 个版本信息对")

            # 5. 为每个版本创建详细信息
            for i, (version_num, date, title) in enumerate(version_info_pairs):
                try:
                    print(f"   🔄 处理版本 {version_num}: {title[:50]}...")

                    # 查找版本相关的内容
                    content = self._find_version_content_by_title(soup, title)

                    # 解析发布日期
                    release_date = self._parse_date(date)

                    version_info = {
                        "version": version_num,
                        "release_date": release_date,
                        "title": title,
                        "content": content,
                    }

                    versions.append(version_info)
                    print(f"   ✅ 版本 {version_num} 处理成功")

                except Exception as e:
                    print(f"   ❌ 版本 {version_num} 处理失败: {e}")
                    continue

            print(f"   ✅ 成功解析 {len(versions)} 个版本")

            # 如果解析失败，使用备用数据
            if not versions:
                print("   ⚠️ 解析失败，使用备用数据...")
                versions = self._get_fallback_versions()

            return versions

        except Exception as e:
            print(f"   ❌ 解析HTML失败: {e}")
            print("   🔄 使用备用数据")
            return self._get_fallback_versions()

    def _find_version_content_by_title(self, soup: BeautifulSoup, title: str) -> str:
        """根据标题查找版本相关的内容"""
        try:
            content_parts = []

            # 查找标题对应的h2元素
            h2_element = soup.find("h2", string=title)
            if not h2_element:
                # 尝试模糊匹配
                h2_elements = soup.find_all("h2")
                for h2 in h2_elements:
                    if title in h2.get_text():
                        h2_element = h2
                        break

            if h2_element:
                # 查找该h2元素后面的内容
                current = h2_element

                # 向后查找兄弟元素
                for sibling in current.find_next_siblings():
                    # 如果遇到下一个h2，停止
                    if sibling.name == "h2":
                        break

                    # 收集h3标签内容
                    if sibling.name == "h3":
                        h3_text = sibling.get_text().strip()
                        if h3_text and len(h3_text) > 3:
                            content_parts.append(h3_text)

                    # 收集段落内容
                    elif sibling.name == "p":
                        p_text = sibling.get_text().strip()
                        if p_text and len(p_text) > 10:
                            content_parts.append(p_text)

                    # 收集div内容
                    elif sibling.name == "div":
                        div_text = sibling.get_text().strip()
                        if div_text and len(div_text) > 10:
                            # 查找功能相关的内容
                            if any(
                                keyword in div_text.lower()
                                for keyword in [
                                    "agent",
                                    "planning",
                                    "context",
                                    "tab",
                                    "memory",
                                    "search",
                                    "improvement",
                                    "feature",
                                    "better",
                                    "faster",
                                    "new",
                                    "background",
                                    "slack",
                                    "to-do",
                                    "todo",
                                    "queued",
                                    "messages",
                                    "pr",
                                    "indexing",
                                    "embeddings",
                                    "semantic",
                                    "merge",
                                    "conflicts",
                                    "bugbot",
                                    "mcp",
                                    "pricing",
                                    "rules",
                                    "terminal",
                                    "images",
                                ]
                            ):
                                content_parts.append(div_text)

                    # 限制内容数量
                    if len(content_parts) >= 10:
                        break

            # 如果没有找到足够内容，尝试通用搜索
            if len(content_parts) < 3:
                # 搜索包含标题关键词的内容
                title_keywords = title.lower().split()
                all_elements = soup.find_all(["h3", "p", "div"])

                for element in all_elements:
                    text = element.get_text().strip()
                    if len(text) > 10:
                        # 如果文本包含标题中的关键词
                        if any(keyword in text.lower() for keyword in title_keywords):
                            content_parts.append(text)
                            if len(content_parts) >= 8:
                                break

            # 返回内容
            if content_parts:
                return "\n".join(content_parts[:8])  # 返回前8个内容
            else:
                return f"New features and improvements: {title}"

        except Exception as e:
            print(f"   ❌ 查找内容失败: {e}")
            return f"New features and improvements: {title}"

    def _find_version_title(self, soup: BeautifulSoup, version: str) -> str:
        """查找版本的主要标题"""
        try:
            # 查找h1, h2标签中的主要功能标题
            major_headers = soup.find_all(["h1", "h2"])

            for header in major_headers:
                header_text = header.get_text().strip()

                # 跳过页面标题
                if header_text.lower() in ["changelog", "cursor changelog"]:
                    continue

                # 查找有意义的功能标题
                if len(header_text) > 10 and any(
                    keyword in header_text.lower()
                    for keyword in [
                        "agent",
                        "planning",
                        "context",
                        "tab",
                        "better",
                        "faster",
                        "background",
                        "slack",
                        "improvement",
                        "feature",
                        "new",
                        "update",
                    ]
                ):
                    return header_text

            # 如果没有找到，返回默认标题
            return f"Cursor Version {version} Update"

        except Exception as e:
            print(f"   ❌ 查找标题失败: {e}")
            return f"Cursor Version {version} Update"

    def _find_version_content(self, soup: BeautifulSoup, version: str) -> str:
        """查找版本相关的内容"""
        try:
            content_parts = []

            # 查找所有h3标签（功能描述）
            h3_tags = soup.find_all("h3")

            for h3 in h3_tags:
                h3_text = h3.get_text().strip()

                # 跳过空内容
                if not h3_text or len(h3_text) < 3:
                    continue

                # 添加功能相关的内容
                if any(
                    keyword in h3_text.lower()
                    for keyword in [
                        "agent",
                        "planning",
                        "context",
                        "tab",
                        "memory",
                        "search",
                        "improvement",
                        "feature",
                        "better",
                        "faster",
                        "new",
                        "background",
                        "slack",
                        "to-do",
                        "todo",
                        "queued",
                        "messages",
                        "pr",
                        "indexing",
                        "embeddings",
                        "semantic",
                        "merge",
                        "conflicts",
                    ]
                ):
                    content_parts.append(h3_text)

                # 限制内容数量
                if len(content_parts) >= 10:
                    break

            # 查找改进项目的分类（Improvements, Fixes, Patches）
            categories = ["Improvements", "Fixes", "Patches"]
            for category in categories:
                category_elements = soup.find_all(
                    string=lambda text: text and category in text
                )
                for element in category_elements:
                    parent = element.parent
                    if parent:
                        # 查找数字（如 "Improvements (7)"）
                        category_text = parent.get_text().strip()
                        if "(" in category_text and ")" in category_text:
                            content_parts.append(category_text)

            # 查找段落描述
            paragraphs = soup.find_all("p")
            for p in paragraphs:
                p_text = p.get_text().strip()
                if len(p_text) > 20 and any(
                    keyword in p_text.lower()
                    for keyword in [
                        "agent",
                        "cursor",
                        "background",
                        "slack",
                        "feature",
                        "improvement",
                        "plan",
                        "task",
                        "context",
                        "chat",
                        "update",
                    ]
                ):
                    content_parts.append(p_text)
                    if len(content_parts) >= 15:
                        break

            # 返回内容
            if content_parts:
                return "\n".join(content_parts[:10])  # 返回前10个内容
            else:
                return "New features and improvements for Cursor IDE"

        except Exception as e:
            print(f"   ❌ 查找内容失败: {e}")
            return "New features and improvements for Cursor IDE"

    def _extract_title_near_version(self, soup: BeautifulSoup, version: str) -> str:
        """提取版本附近的标题"""
        try:
            # 查找所有标题
            headers = soup.find_all(["h1", "h2", "h3"])

            # 查找版本号
            version_element = soup.find(
                string=lambda text: text and text.strip() == version
            )

            if not version_element:
                return f"Cursor {version} Update"

            # 查找最接近版本号的标题
            best_title = None
            min_distance = float("inf")

            for header in headers:
                try:
                    # 计算标题与版本号的距离（简单的文本位置比较）
                    header_text = header.get_text().strip()

                    # 跳过主标题
                    if header_text.lower() in ["changelog", "cursor changelog"]:
                        continue

                    # 如果标题内容有意义，计算距离
                    if len(header_text) > 5:
                        # 获取元素在页面中的位置
                        version_pos = str(soup).find(str(version_element))
                        header_pos = str(soup).find(str(header))

                        if version_pos != -1 and header_pos != -1:
                            distance = abs(version_pos - header_pos)
                            if distance < min_distance:
                                min_distance = distance
                                best_title = header_text

                except Exception:
                    continue

            return best_title if best_title else f"Cursor {version} Update"

        except Exception as e:
            print(f"   ❌ 提取标题失败: {e}")
            return f"Cursor {version} Update"

    def _extract_content_near_version(self, soup: BeautifulSoup, version: str) -> str:
        """提取版本附近的内容"""
        try:
            # 查找版本号附近的所有h3标签（功能描述）
            content_parts = []

            # 查找所有h3标签
            h3_tags = soup.find_all("h3")

            # 获取版本号的位置
            version_element = soup.find(
                string=lambda text: text and text.strip() == version
            )

            if not version_element:
                return "No content available"

            # 简单方法：获取页面中该版本附近的所有h3标签
            page_html = str(soup)
            version_pos = page_html.find(version)

            # 查找版本号前后的内容
            nearby_content = []

            for h3 in h3_tags:
                h3_text = h3.get_text().strip()

                # 跳过空内容
                if not h3_text or len(h3_text) < 3:
                    continue

                # 添加有意义的功能描述
                if any(
                    keyword in h3_text.lower()
                    for keyword in [
                        "agent",
                        "planning",
                        "context",
                        "tab",
                        "memory",
                        "search",
                        "improvement",
                        "feature",
                        "better",
                        "faster",
                        "new",
                    ]
                ):
                    nearby_content.append(h3_text)

                # 限制内容数量
                if len(nearby_content) >= 10:
                    break

            # 如果找到内容，返回前几个
            if nearby_content:
                return "\n".join(nearby_content[:8])  # 返回前8个功能
            else:
                return "New features and improvements"

        except Exception as e:
            print(f"   ❌ 提取内容失败: {e}")
            return "No content available"

    def _estimate_release_date(self, version: str) -> str:
        """估算版本发布日期"""
        try:
            # 基于版本号估算日期
            parts = version.split(".")
            major = int(parts[0])
            minor = int(parts[1])
            patch = int(parts[2]) if len(parts) > 2 else 0

            # 估算发布日期（这里可以根据实际情况调整）
            from datetime import datetime, timedelta

            # 假设从2024年开始
            base_date = datetime(2024, 1, 1)

            # 每个大版本间隔约3个月，小版本间隔约1周
            estimated_days = major * 90 + minor * 7 + patch * 1

            estimated_date = base_date + timedelta(days=estimated_days)

            return estimated_date.strftime("%Y-%m-%d")

        except Exception:
            # 如果估算失败，返回当前日期
            from datetime import datetime

            return datetime.now().strftime("%Y-%m-%d")

    def _parse_by_containers(self, soup: BeautifulSoup) -> List[Dict]:
        """通过容器结构解析版本信息"""
        versions = []

        try:
            # 查找可能包含版本信息的容器
            containers = soup.find_all(["div", "section", "article"])

            for container in containers:
                text = container.get_text()

                # 查找版本号
                version_match = re.search(r"(\d+\.\d+)", text)
                if version_match:
                    version = version_match.group(1)

                    # 查找日期
                    date_match = re.search(r"([A-Za-z]+ \d+, \d{4})", text)
                    date = date_match.group(1) if date_match else "January 1, 2025"

                    # 提取标题和内容
                    title = self._extract_title_from_container(container)
                    content = self._extract_content_from_container(container)

                    versions.append(
                        {
                            "version": version,
                            "release_date": self._parse_date(date),
                            "title": title,
                            "content": content,
                        }
                    )

            return versions

        except Exception as e:
            print(f"❌ 容器解析失败: {e}")
            return []

    def _parse_by_patterns(self, soup: BeautifulSoup) -> List[Dict]:
        """通过模式匹配解析版本信息"""
        versions = []

        try:
            # 获取页面所有文本
            page_text = soup.get_text()

            # 基于已知的版本模式，尝试提取信息
            known_versions = ["1.2", "1.1", "1.0", "0.50", "0.49"]

            for version in known_versions:
                if version in page_text:
                    # 查找版本附近的日期
                    version_pos = page_text.find(version)
                    surrounding_text = page_text[
                        max(0, version_pos - 100) : version_pos + 500
                    ]

                    date_match = re.search(r"([A-Za-z]+ \d+, \d{4})", surrounding_text)
                    date = date_match.group(1) if date_match else "January 1, 2025"

                    # 提取标题和内容
                    title = self._extract_title_from_text(surrounding_text, version)
                    content = self._extract_content_from_text(page_text, version)

                    versions.append(
                        {
                            "version": version,
                            "release_date": self._parse_date(date),
                            "title": title,
                            "content": content,
                        }
                    )

            return versions

        except Exception as e:
            print(f"❌ 模式解析失败: {e}")
            return []

    def _extract_title_from_container(self, container) -> str:
        """从容器中提取标题"""
        try:
            # 查找标题元素
            title_elements = container.find_all(["h1", "h2", "h3", "h4"])
            for element in title_elements:
                text = element.get_text().strip()
                if len(text) > 10 and len(text) < 100:
                    return text

            # 如果没有找到标题元素，查找可能的标题文本
            texts = container.find_all(text=True)
            for text in texts:
                text = text.strip()
                if (
                    len(text) > 10
                    and len(text) < 100
                    and any(
                        keyword in text.lower()
                        for keyword in [
                            "agent",
                            "update",
                            "feature",
                            "improvement",
                            "new",
                            "better",
                            "faster",
                        ]
                    )
                ):
                    return text

            return "Cursor Update"

        except Exception:
            return "Cursor Update"

    def _extract_content_from_container(self, container) -> str:
        """从容器中提取内容"""
        try:
            # 提取所有段落和列表内容
            content_elements = container.find_all(["p", "li", "div"])
            content_parts = []

            for element in content_elements:
                text = element.get_text().strip()
                if len(text) > 20:
                    content_parts.append(text)

            return (
                "\n\n".join(content_parts) if content_parts else "No content available"
            )

        except Exception:
            return "No content available"

    def _extract_title_from_text(self, text: str, version: str) -> str:
        """从文本中提取标题"""
        try:
            lines = text.split("\n")
            for line in lines:
                line = line.strip()
                if (
                    len(line) > 10
                    and len(line) < 100
                    and any(
                        keyword in line.lower()
                        for keyword in [
                            "agent",
                            "update",
                            "feature",
                            "improvement",
                            "new",
                            "better",
                            "faster",
                        ]
                    )
                ):
                    return line

            return f"Cursor {version} Update"

        except Exception:
            return f"Cursor {version} Update"

    def _extract_content_from_text(self, text: str, version: str) -> str:
        """从文本中提取内容"""
        try:
            # 查找版本号的位置
            version_pos = text.find(version)
            if version_pos == -1:
                return "No content available"

            # 提取版本号后面的内容（到下一个版本号或固定长度）
            content_start = version_pos + len(version)
            content_end = content_start + 2000  # 限制内容长度

            # 查找下一个版本号
            next_version_pos = -1
            for v in ["1.2", "1.1", "1.0", "0.50", "0.49"]:
                if v != version:
                    pos = text.find(v, content_start)
                    if pos != -1 and (next_version_pos == -1 or pos < next_version_pos):
                        next_version_pos = pos

            if next_version_pos != -1:
                content_end = next_version_pos

            content = text[content_start:content_end]

            # 清理内容
            content = re.sub(r"\s+", " ", content)  # 合并多个空格
            content = content.strip()

            return content if content else "No content available"

        except Exception:
            return "No content available"

    def _is_date(self, text: str) -> bool:
        """检查文本是否是日期格式"""
        date_patterns = [
            r"[A-Za-z]+ \d+, \d{4}",  # January 1, 2024
            r"\d{4}-\d{2}-\d{2}",  # 2024-01-01
            r"\d{2}/\d{2}/\d{4}",  # 01/01/2024
        ]

        for pattern in date_patterns:
            if re.match(pattern, text.strip()):
                return True
        return False

    def _is_valid_cursor_version(self, version: str) -> bool:
        """验证是否是有效的Cursor版本号"""
        if not version or not re.match(r"^\d+\.\d+$", version):
            return False

        try:
            parts = version.split(".")
            if len(parts) != 2:
                return False

            major = int(parts[0])
            minor = int(parts[1])

            # Cursor版本号的合理范围:
            # - 1.x 系列: 1.0, 1.1, 1.2, ...
            # - 0.x 系列: 0.40+（历史版本）
            if (major == 1 and minor >= 0) or (major == 0 and 40 <= minor <= 99):
                return True

            return False

        except (ValueError, IndexError):
            return False

    def _validate_version_context(self, element) -> bool:
        """验证版本号的上下文，确保是真正的版本号而非其他数字"""
        try:
            # 检查元素的父容器和兄弟元素
            parent = element.parent
            if not parent:
                return True  # 如果没有父元素，默认有效

            # 获取周围的文本内容
            surrounding_text = ""

            # 检查前后的兄弟元素
            prev_sibling = element.previous_sibling
            if prev_sibling:
                surrounding_text += str(prev_sibling)

            next_sibling = element.next_sibling
            if next_sibling:
                surrounding_text += str(next_sibling)

            # 检查父元素的文本
            if parent:
                surrounding_text += parent.get_text()

            # 转换为小写进行关键词检查
            context_text = surrounding_text.lower()

            # 版本号相关的关键词
            version_keywords = [
                "version",
                "v",
                "release",
                "update",
                "cursor",
                "changelog",
                "july",
                "june",
                "may",
                "april",
                "march",
                "february",
                "january",
                "2024",
                "2025",
                "agent",
                "planning",
                "feature",
                "improvement",
            ]

            # 非版本号的关键词（排除这些）
            non_version_keywords = [
                "price",
                "cost",
                "dollar",
                "usd",
                "payment",
                "billing",
                "width",
                "height",
                "size",
                "pixel",
                "px",
                "rem",
                "em",
                "rating",
                "star",
                "score",
                "percentage",
                "%",
            ]

            # 如果包含非版本号关键词，返回False
            for keyword in non_version_keywords:
                if keyword in context_text:
                    return False

            # 如果包含版本号关键词，返回True
            for keyword in version_keywords:
                if keyword in context_text:
                    return True

            # 如果没有明确的关键词，检查是否在合理的HTML结构中
            # 版本号通常在特定的容器中
            parent_classes = parent.get("class", []) if parent else []
            parent_class_str = " ".join(parent_classes).lower()

            # 常见的版本号容器类名
            version_container_keywords = [
                "version",
                "tag",
                "badge",
                "label",
                "release",
                "update",
                "flex",
                "items-center",
                "card",
                "container",
            ]

            for keyword in version_container_keywords:
                if keyword in parent_class_str:
                    return True

            # 默认情况下，如果没有明确的反对理由，认为是有效的
            return True

        except Exception:
            # 如果验证过程出错，默认认为有效
            return True

    def _filter_cursor_versions(self, versions: List[str]) -> List[str]:
        """智能过滤和排序Cursor版本号"""
        filtered_versions = []

        # 已知的Cursor版本号（按优先级排序）
        known_cursor_versions = [
            "1.2",
            "1.1",
            "1.0",  # 1.x 系列
            "0.50",
            "0.49",
            "0.48",
            "0.47",
            "0.46",
            "0.45",  # 0.x 系列
        ]

        # 首先添加已知版本（按优先级）
        for known_version in known_cursor_versions:
            if known_version in versions:
                filtered_versions.append(known_version)

        # 然后添加未知但符合格式的新版本
        for version in versions:
            if version not in filtered_versions:
                parts = version.split(".")
                major, minor = int(parts[0]), int(parts[1])

                # 支持未来的版本号
                if (major == 1 and minor >= 0) or (major == 0 and minor >= 40):
                    filtered_versions.append(version)

        # 按版本号排序（降序）
        filtered_versions.sort(
            key=lambda x: [int(v) for v in x.split(".")], reverse=True
        )

        return filtered_versions

    def _parse_date(self, date_str: str) -> str:
        """解析日期字符串为ISO格式"""
        try:
            # 处理 "July 3, 2025" 格式
            if re.match(r"[A-Za-z]+ \d+, \d{4}", date_str):
                date_obj = datetime.strptime(date_str, "%B %d, %Y")
                return date_obj.strftime("%Y-%m-%d")

            # 处理 "2025-07-03" 格式
            elif re.match(r"\d{4}-\d{2}-\d{2}", date_str):
                return date_str

            # 处理其他格式...
            else:
                return "2025-01-01"

        except Exception:
            return "2025-01-01"

    def _get_fallback_versions(self) -> List[Dict]:
        """获取备用版本数据（当网站解析失败时使用）"""
        print("📋 使用备用版本数据")

        return [
            {
                "version": "1.2",
                "release_date": "2025-07-03",
                "title": "Agent Planning, Better Context & Faster Tab",
                "content": """
## Agent Planning, Better Context & Faster Tab

### Agent To-dos
Agents now plan ahead with structured to-do lists, making long-horizon tasks easier to understand and track.

The agent breaks down longer tasks with dependencies, visible to you in chat and streamed into Slack when relevant. It can update this list as work progresses, keeping context fresh and interactions predictable.

### Queued messages
You can now queue follow-up messages for Agent once it's done with current task. Just type your instructions and send. Once in queue, you can reorder tasks and start executing without waiting.

### Memories (now GA)
Memories is now GA. Since 1.0, we've improved memory generation quality, added in-editor UI polish, and introduced user approvals for background-generated memories to preserve trust.

### PR indexing & search
Cursor now indexes and summarizes PRs much like it does files. You can search old PRs semantically or explicitly fetch a PR, issue, commit, or branch into context.

### Improved embeddings for semantic search
Codebase search is now much more accurate with our new embedding model. We've also re-tuned prompts to yield cleaner, more focused results.

### Faster Tab
Tab completions are now ~100ms faster, and TTFT has been reduced by 30%. We made this possible by restructuring our memory management system and optimizing data transfer pathways.

### Let Agent resolve merge conflicts
When merge conflicts occur, Agent can now attempt to resolve them for you. Click Resolve in Chat and relevant context will be added to resolve the conflict.

### Background Agent improvements
Several improvements to Background Agents make them more predictable and resilient:
- PRs follow your team's template
- Changes to the agent branch are auto-pulled in
- Conflicts (like rebases) are now surfaced as actionable follow-ups
- You can commit directly from the sidebar
- Slack and web deeplinks open the associated repo, even if you don't have it open
            """,
            },
            {
                "version": "1.1",
                "release_date": "2025-06-12",
                "title": "Background Agents in Slack",
                "content": """
## Background Agents in Slack

You can now launch Background Agents directly from Slack by mentioning @Cursor. Agents can read the thread, understand what's going on, and create PRs in GitHub, all without leaving the conversation.

### Use Cursor where your team works
Mention @Cursor in any thread with a prompt. Agents run remotely in a secure environment and you'll get updates directly in Slack, including links to Cursor and GitHub, when the work is done.

### Agents understand context
Cursor reads the entire Slack thread before starting, so Background Agents understand the full context when you reference previous discussions or issues.

### Getting started
To use Background Agents in Slack, an admin needs to set up the integration first. Check out our setup documentation or ask your workspace admin to connect Cursor from the Dashboard → Integrations page.
            """,
            },
            {
                "version": "1.0",
                "release_date": "2025-06-04",
                "title": "BugBot, Background Agent access to everyone, and one-click MCP install",
                "content": """
## BugBot, Background Agent access to everyone, and one-click MCP install

### Automatic code review with BugBot
BugBot automatically reviews your PRs and catches potential bugs and issues. When an issue is found, BugBot leaves a comment on your PRs in GitHub.

### Background Agent for everyone
Since we released Background Agent, our remote coding agent, in early access a few weeks ago, early signals have been positive. We're now excited to expand Background Agent to all users!

### Agent in Jupyter Notebooks
Cursor can now implement changes in Jupyter Notebooks! Agent will now create and edit multiple cells directly inside of Jupyter, a significant improvement for research and data science tasks.

### Memories
With Memories, Cursor can remember facts from conversations and reference them in the future. Memories are stored per project on an individual level, and can be managed from Settings.

### MCP one-click install and OAuth support
You can now set up MCP servers in Cursor with one click, and together with OAuth support, you can easily authenticate servers that support it.

### Richer Chat responses
Cursor can now render visualizations inside of a conversation. In particular, Mermaid diagrams and Markdown tables can now be generated and viewed in the same place!
            """,
            },
        ]

    def _translate_content(self, content: str) -> str:
        """翻译内容到中文"""
        try:
            # 添加完整的请求头来解决 428 错误
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.deepseek_api_key}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Cache-Control": "no-cache",
            }

            data = {
                "model": settings.ai_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的技术翻译员，专门翻译软件开发相关的文档。请将以下英文内容翻译成中文，保持技术术语的准确性和专业性。重要：请保持原文的段落结构和格式，使用句号（。）分隔句子，不要使用###或***等标记符号。",
                    },
                    {
                        "role": "user",
                        "content": f"请翻译以下 Cursor 更新日志内容到中文，保持段落分隔和格式结构：\n\n{content}",
                    },
                ],
                "max_tokens": 2000,
                "temperature": 0.3,
                "stream": False,
            }

            # 重试机制
            for attempt in range(3):
                try:
                    print(f"      🔄 第 {attempt + 1}/3 次尝试...", end="", flush=True)
                    start_time = time.time()
                    response = requests.post(
                        settings.deepseek_api_url,
                        headers=headers,
                        json=data,
                        timeout=120,
                    )

                    elapsed_time = time.time() - start_time
                    print(f" (用时 {elapsed_time:.1f}s)")

                    if response.status_code == 200:
                        result = response.json()
                        if "choices" in result and len(result["choices"]) > 0:
                            translated_text = result["choices"][0]["message"]["content"]
                            return translated_text
                        else:
                            print(f"      ❌ 响应格式错误: {result}")
                    else:
                        print(f"      ❌ API 响应错误: {response.status_code}")
                        if attempt < 2:
                            print(f"      ⏳ 等待 {attempt + 1} 秒后重试...")
                            time.sleep(attempt + 1)

                except requests.exceptions.Timeout:
                    print(f"      ⏰ 请求超时，重试中...")
                    continue
                except requests.exceptions.RequestException as e:
                    print(f"      🔌 请求异常: {e}")
                    if attempt < 2:
                        continue
                except Exception as e:
                    print(f"      ❗ 未知错误: {e}")
                    if attempt < 2:
                        continue

            return "❌ 翻译失败：所有重试都失败了"

        except Exception as e:
            print(f"      ❌ 翻译配置错误: {e}")
            return f"❌ 翻译失败: {str(e)}"

    def _translate_title(self, title: str) -> str:
        """翻译标题到中文"""
        try:
            # 添加完整的请求头来解决 428 错误
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.deepseek_api_key}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Cache-Control": "no-cache",
            }

            data = {
                "model": settings.ai_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的技术翻译员。请将以下英文标题翻译成中文，保持简洁和专业性。只返回翻译结果，不需要其他解释。",
                    },
                    {"role": "user", "content": f"请翻译：{title}"},
                ],
                "max_tokens": 100,
                "temperature": 0.3,
                "stream": False,
            }

            # 重试机制
            for attempt in range(2):
                try:
                    print(f"      🔄 第 {attempt + 1}/2 次尝试...", end="", flush=True)
                    start_time = time.time()
                    response = requests.post(
                        settings.deepseek_api_url,
                        headers=headers,
                        json=data,
                        timeout=60,
                    )

                    elapsed_time = time.time() - start_time
                    print(f" (用时 {elapsed_time:.1f}s)")

                    if response.status_code == 200:
                        result = response.json()
                        if "choices" in result and len(result["choices"]) > 0:
                            translated_title = result["choices"][0]["message"][
                                "content"
                            ].strip()
                            return translated_title
                        else:
                            print(f"      ❌ 响应格式错误: {result}")
                    else:
                        print(f"      ❌ API 响应错误: {response.status_code}")
                        if attempt < 1:
                            print(f"      ⏳ 等待 {attempt + 1} 秒后重试...")
                            time.sleep(attempt + 1)

                except requests.exceptions.Timeout:
                    print(f"      ⏰ 请求超时，重试中...")
                    continue
                except requests.exceptions.RequestException as e:
                    print(f"      🔌 请求异常: {e}")
                    if attempt < 1:
                        continue
                except Exception as e:
                    print(f"      ❗ 未知错误: {e}")
                    if attempt < 1:
                        continue

            return "❌ 标题翻译失败"

        except Exception as e:
            print(f"      ❌ 标题翻译配置错误: {e}")
            return "❌ 标题翻译失败"

    def _analyze_with_deepseek(
        self, original_content: str, translated_content: str
    ) -> str:
        """使用 DeepSeek 分析总结"""
        try:
            # 添加完整的请求头来解决 428 错误
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.deepseek_api_key}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Cache-Control": "no-cache",
            }

            data = {
                "model": settings.ai_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的技术分析师，专门分析软件更新和技术趋势。请分析以下 Cursor 更新内容，提供深度见解和总结。请按段落分隔内容，使用句号（。）分隔句子，不要使用###或***等标记符号。",
                    },
                    {
                        "role": "user",
                        "content": f"""
请分析以下 Cursor 更新内容，提供深度见解和总结：

原文：
{original_content}

中文翻译：
{translated_content}

请从以下几个方面进行分析：
1. 主要功能更新和改进
2. 技术创新点
3. 对开发者的影响
4. 市场竞争优势
5. 未来发展趋势
6. 网络搜索相关信息（基于你的知识，分析这些更新在技术社区、开发者论坛、社交媒体等网络平台的讨论热度和关注点）
7. 用户/开发者响应如何（预测和分析开发者社区对这些更新的可能反应、接受度和使用情况）

请提供详细的分析，每个方面都要有具体的论述和见解。
                        """,
                    },
                ],
                "max_tokens": 2000,
                "temperature": 0.7,
                "stream": False,
            }

            # 重试机制
            for attempt in range(3):
                try:
                    print(f"      🔄 第 {attempt + 1}/3 次尝试...", end="", flush=True)
                    start_time = time.time()
                    response = requests.post(
                        settings.deepseek_api_url,
                        headers=headers,
                        json=data,
                        timeout=120,
                    )

                    elapsed_time = time.time() - start_time
                    print(f" (用时 {elapsed_time:.1f}s)")

                    if response.status_code == 200:
                        result = response.json()
                        if "choices" in result and len(result["choices"]) > 0:
                            analysis_result = result["choices"][0]["message"]["content"]
                            return analysis_result
                        else:
                            print(f"      ❌ 响应格式错误: {result}")
                    else:
                        print(f"      ❌ API 响应错误: {response.status_code}")
                        if attempt < 2:
                            print(f"      ⏳ 等待 {attempt + 1} 秒后重试...")
                            time.sleep(attempt + 1)

                except requests.exceptions.Timeout:
                    print(f"      ⏰ 请求超时，重试中...")
                    continue
                except requests.exceptions.RequestException as e:
                    print(f"      🔌 请求异常: {e}")
                    if attempt < 2:
                        continue
                except Exception as e:
                    print(f"      ❗ 未知错误: {e}")
                    if attempt < 2:
                        continue

            return "❌ 分析失败：所有重试都失败了"

        except Exception as e:
            print(f"      ❌ 分析配置错误: {e}")
            return f"❌ 分析失败: {str(e)}"

    def _translate_and_analyze_with_deepseek(self, title: str, content: str) -> Dict:
        """一次性完成翻译和分析"""
        try:
            # 添加完整的请求头来解决 428 错误
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.deepseek_api_key}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Cache-Control": "no-cache",
            }

            data = {
                "model": settings.ai_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的技术翻译员和分析师，专门处理软件开发相关的文档。请严格按照指定的JSON格式返回结果，保持原文的格式结构。",
                    },
                    {
                        "role": "user",
                        "content": f"""
请对以下Cursor IDE更新进行翻译和分析：

标题（英文）：{title}
内容（英文）：{content}

翻译要求：
1. 保持原文的段落结构和格式
2. 保留原文中的标题层级（##, ###）
3. 保持列表格式（- 或数字列表）
4. 技术术语使用准确的中文翻译
5. 语言要流畅自然，符合中文表达习惯

请按照以下JSON格式返回结果：
{{
  "translated_title": "中文翻译的标题（简洁明确）",
  "translated_content": "中文翻译的内容（保持原文格式结构，使用\\n\\n分隔段落，使用\\n分隔行）",
  "analysis": "详细的技术分析（用中文，包括：\\n\\n1. 主要功能更新和改进分析\\n- 具体功能点分析\\n- 技术实现特点\\n\\n2. 技术创新点\\n- 创新技术解读\\n- 与竞品对比\\n\\n3. 对开发者的影响\\n- 开发效率提升\\n- 学习成本评估\\n\\n4. 市场竞争优势\\n- 核心竞争力\\n- 市场定位分析）"
}}

重要：请确保返回严格的JSON格式，translated_content字段要保持原文的段落结构。
                        """,
                    },
                ],
                "max_tokens": 3000,
                "temperature": 0.2,
                "stream": False,
            }

            # 重试机制
            for attempt in range(3):
                try:
                    print(f"      🔄 第 {attempt + 1}/3 次尝试...", end="", flush=True)
                    start_time = time.time()
                    response = requests.post(
                        settings.deepseek_api_url,
                        headers=headers,
                        json=data,
                        timeout=120,
                    )

                    elapsed_time = time.time() - start_time
                    print(f" (用时 {elapsed_time:.1f}s)")

                    if response.status_code == 200:
                        result = response.json()
                        if "choices" in result and len(result["choices"]) > 0:
                            api_content = result["choices"][0]["message"]["content"]

                            # 尝试解析JSON响应
                            try:
                                # 提取JSON部分
                                json_start = api_content.find("{")
                                json_end = api_content.rfind("}") + 1

                                if json_start != -1 and json_end > json_start:
                                    json_str = api_content[json_start:json_end]
                                    parsed_result = json.loads(json_str)

                                    return {
                                        "translated_title": parsed_result.get(
                                            "translated_title", f"{title}（翻译失败）"
                                        ),
                                        "translated_content": parsed_result.get(
                                            "translated_content",
                                            f"{content}（翻译失败）",
                                        ),
                                        "analysis": parsed_result.get(
                                            "analysis", "分析失败"
                                        ),
                                    }
                                else:
                                    # 如果没有找到JSON，使用备用解析方法
                                    return self._parse_fallback_response(
                                        api_content, title, content
                                    )

                            except json.JSONDecodeError:
                                # JSON解析失败，使用备用方法
                                print(f"      ⚠️ JSON解析失败，使用备用方法...")
                                return self._parse_fallback_response(
                                    api_content, title, content
                                )
                        else:
                            print(f"      ❌ 响应格式错误: {result}")
                    else:
                        print(f"      ❌ API 响应错误: {response.status_code}")
                        if attempt < 2:
                            print(f"      ⏳ 等待 {attempt + 1} 秒后重试...")
                            time.sleep(attempt + 1)

                except requests.exceptions.Timeout:
                    print(f"      ⏰ 请求超时，重试中...")
                    continue
                except requests.exceptions.RequestException as e:
                    print(f"      🔌 请求异常: {e}")
                    if attempt < 2:
                        continue
                except Exception as e:
                    print(f"      ❗ 未知错误: {e}")
                    if attempt < 2:
                        continue

            return {
                "translated_title": f"{title}（翻译失败）",
                "translated_content": f"{content}（翻译失败）",
                "analysis": "❌ API调用失败：所有重试都失败了",
            }

        except Exception as e:
            print(f"      ❌ 翻译和分析配置错误: {e}")
            return {
                "translated_title": f"{title}（翻译失败）",
                "translated_content": f"{content}（翻译失败）",
                "analysis": f"❌ 配置错误: {str(e)}",
            }

    def _parse_fallback_response(
        self, content: str, original_title: str, original_content: str
    ) -> Dict:
        """备用响应解析方法"""
        try:
            # 简单的文本解析作为备用方案
            lines = content.split("\n")
            translated_title = original_title
            translated_content = original_content
            analysis = content

            # 尝试找到翻译的标题和内容
            for i, line in enumerate(lines):
                line = line.strip()
                if "翻译" in line and "标题" in line and ":" in line:
                    translated_title = line.split(":", 1)[1].strip()
                elif "翻译" in line and "内容" in line and ":" in line:
                    translated_content = line.split(":", 1)[1].strip()

            return {
                "translated_title": (
                    translated_title
                    if translated_title != original_title
                    else f"{original_title}（AI翻译）"
                ),
                "translated_content": (
                    translated_content
                    if translated_content != original_content
                    else f"{original_content}（AI翻译）"
                ),
                "analysis": analysis,
            }
        except Exception:
            return {
                "translated_title": f"{original_title}（解析失败）",
                "translated_content": f"{original_content}（解析失败）",
                "analysis": content,
            }

    def get_latest_version(self) -> Optional[Dict]:
        """获取最新版本信息"""
        results = self.collect()
        if results:
            return results[0]  # 返回最新版本
        return None
