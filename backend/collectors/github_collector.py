import requests
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import dateparser

from .base import BaseCollector, CollectorItem
from config import config


class GitHubCollector(BaseCollector):
    """GitHub项目收集器"""

    def __init__(self, name: str, repositories: List[str]):
        super().__init__(name)
        self.repositories = repositories
        self.session = requests.Session()

        # 设置GitHub API认证
        if config.GITHUB_TOKEN:
            self.session.headers.update(
                {
                    "Authorization": f"token {config.GITHUB_TOKEN}",
                    "Accept": "application/vnd.github.v3+json",
                }
            )

        self.session.headers.update(
            {"User-Agent": "LogWatcher/1.0 (Tech Release Collector)"}
        )

        self.api_base = "https://api.github.com"

    def get_source_name(self) -> str:
        return "GitHub"

    async def collect(self) -> List[CollectorItem]:
        """收集GitHub项目发布数据"""
        items = []

        for repo in self.repositories:
            try:
                self.logger.info(f"开始收集GitHub项目: {repo}")

                # 获取项目发布信息
                releases = await self.get_releases(repo)

                for release in releases:
                    try:
                        item = self.parse_release(repo, release)
                        if self.validate_item(item):
                            items.append(item)
                    except Exception as e:
                        self.logger.error(f"解析发布信息失败: {repo}, 错误: {e}")
                        continue

                # TODO #3 数据收集器: 添加API请求频率限制
                await asyncio.sleep(0.5)  # 避免触发API限制

            except Exception as e:
                self.logger.error(f"收集GitHub项目失败: {repo}, 错误: {e}")
                continue

        self.logger.info(f"GitHub收集完成，共收集到 {len(items)} 条发布数据")
        return items

    async def get_releases(self, repo: str) -> List[Dict[str, Any]]:
        """获取项目发布列表"""
        url = f"{self.api_base}/repos/{repo}/releases"

        try:
            response = self.session.get(url, params={"per_page": 10})
            response.raise_for_status()

            releases = response.json()

            # 过滤掉预发布版本（可选）
            if not config.DEBUG:
                releases = [r for r in releases if not r.get("prerelease", False)]

            return releases

        except Exception as e:
            self.logger.error(f"获取发布列表失败: {repo}, 错误: {e}")
            return []

    def parse_release(self, repo: str, release: Dict[str, Any]) -> CollectorItem:
        """解析发布信息"""
        # 基本信息
        title = f"{repo} {release.get('tag_name', '')} - {release.get('name', '')}"
        url = release.get("html_url", "")

        # 发布描述
        body = release.get("body", "").strip()
        summary = self.extract_summary(body)

        # 发布时间
        published_at = None
        if release.get("published_at"):
            published_at = dateparser.parse(release["published_at"])

        # 作者信息
        author = None
        if release.get("author"):
            author = release["author"].get("login", "")

        # 标签
        tags = ["release"]
        if release.get("prerelease"):
            tags.append("prerelease")

        # 版本类型判断
        tag_name = release.get("tag_name", "").lower()
        if any(keyword in tag_name for keyword in ["major", "v2", "v3", "v4", "v5"]):
            tags.append("major")

        # TODO #3 数据收集器: 添加更智能的版本重要性判断
        return CollectorItem(
            title=title.strip(),
            url=url,
            content=body,
            summary=summary,
            published_at=published_at,
            source=self.get_source_name(),
            author=author,
            tags=tags,
            extra_data={
                "repo": repo,
                "tag_name": release.get("tag_name"),
                "is_prerelease": release.get("prerelease", False),
                "download_count": sum(
                    asset.get("download_count", 0)
                    for asset in release.get("assets", [])
                ),
            },
        )

    def extract_summary(self, body: str) -> str:
        """提取发布摘要"""
        if not body:
            return ""

        # 简单的markdown清理
        import re

        # 移除markdown标记
        body = re.sub(r"#+\s*", "", body)  # 标题
        body = re.sub(r"\*\*(.*?)\*\*", r"\1", body)  # 粗体
        body = re.sub(r"\*(.*?)\*", r"\1", body)  # 斜体
        body = re.sub(r"```.*?```", "", body, flags=re.DOTALL)  # 代码块
        body = re.sub(r"`([^`]+)`", r"\1", body)  # 行内代码

        # 获取前几行作为摘要
        lines = body.split("\n")
        summary_lines = []

        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                summary_lines.append(line)
                if len(summary_lines) >= 3:
                    break

        summary = " ".join(summary_lines)

        # 限制长度
        if len(summary) > 300:
            summary = summary[:297] + "..."

        return summary


# 预定义的GitHub收集器
class TechToolsCollector(GitHubCollector):
    """技术工具收集器"""

    def __init__(self):
        # 重要的技术工具仓库
        repositories = [
            "openai/openai-python",
            "microsoft/vscode",
            "cli/cli",
            "vercel/next.js",
            "facebook/react",
            "vuejs/vue",
            "golang/go",
            "rust-lang/rust",
            "python/cpython",
            "nodejs/node",
        ]

        super().__init__(name="tech_tools", repositories=repositories)


class AIToolsCollector(GitHubCollector):
    """AI工具收集器"""

    def __init__(self):
        # AI相关工具仓库
        repositories = [
            "openai/openai-python",
            "anthropics/anthropic-sdk-python",
            "microsoft/semantic-kernel",
            "langchain-ai/langchain",
            "run-llama/llama_index",
            "microsoft/guidance",
            "microsoft/autogen",
        ]

        super().__init__(name="ai_tools", repositories=repositories)


class DevToolsCollector(GitHubCollector):
    """开发工具收集器"""

    def __init__(self):
        # 开发工具仓库
        repositories = [
            "microsoft/vscode",
            "neovim/neovim",
            "git/git",
            "docker/docker",
            "kubernetes/kubernetes",
            "hashicorp/terraform",
            "ansible/ansible",
        ]

        super().__init__(name="dev_tools", repositories=repositories)
