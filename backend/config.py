import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """应用配置类"""

    # 基础配置
    APP_NAME = os.getenv("APP_NAME", "LogWatcher")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")

    # 数据库配置
    DATABASE_URL = os.getenv(
        "DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/logwatcher"
    )
    DATABASE_ECHO = os.getenv("DATABASE_ECHO", "False").lower() == "true"

    # Redis配置
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # API配置
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # 收集器配置
    COLLECTOR_INTERVAL = int(os.getenv("COLLECTOR_INTERVAL", "3600"))  # 1小时
    MAX_ARTICLES_PER_SOURCE = int(os.getenv("MAX_ARTICLES_PER_SOURCE", "50"))

    # 分页配置
    DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
    MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "100"))

    # 新闻源配置
    NEWS_SOURCES = [
        {
            "name": "Hacker News",
            "url": "https://news.ycombinator.com/rss",
            "type": "rss",
        },
        {
            "name": "GitHub Trending",
            "url": "https://github.com/trending",
            "type": "web",
        },
        {"name": "Product Hunt", "url": "https://www.producthunt.com/", "type": "web"},
    ]

    # 工具监控配置
    MONITORED_TOOLS = [
        {
            "name": "OpenAI",
            "github_repo": "openai/openai-python",
            "website": "https://openai.com/",
            "changelog_url": "https://openai.com/api/changelog",
        },
        {"name": "Cursor", "website": "https://cursor.com/", "twitter": "@cursor_ai"},
        {
            "name": "GitHub CLI",
            "github_repo": "cli/cli",
            "website": "https://cli.github.com/",
        },
    ]


# 全局配置实例
config = Config()
