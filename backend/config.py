import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Settings:
    """应用配置类"""

    def __init__(self):
        # 数据库配置
        self.database_url = os.getenv(
            "DATABASE_URL",
            "mysql+pymysql://logwatcher:logwatcher123@mysql:3306/logwatcher",
        )

        # Redis 配置
        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

        # DeepSeek API 配置 - 使用用户指定的地址和密钥
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_api_url = "https://api.openai-hk.com/v1/chat/completions"

        # 应用配置
        self.app_name = os.getenv("APP_NAME", "LogWatcher")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"

        # AI新闻收集限制配置
        self.daily_ai_collect_limit = int(os.getenv("DAILY_AI_COLLECT_LIMIT", "10"))

        # AI模型配置
        self.ai_model = os.getenv(
            "AI_MODEL", "grok-3-deepsearch"
        )  # 使用grok-3-deepsearch模型


settings = Settings()
