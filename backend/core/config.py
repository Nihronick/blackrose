import os
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings # type: ignore
from typing import Optional

class Settings(BaseSettings):
    # Base
    PROJECT_NAME: str = "BlackRose"
    VERSION: str = "2.0.0"

    # DB
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/blackrose"

    # Bot & Auth
    BOT_TOKEN: str = ""
    JWT_SECRET: str = "dev_secret_key_change_me"
    INIT_DATA_MAX_AGE: int = 86400 # 24 hours
    ADMIN_USERS: str = "" # Comma separated user IDs
    ADMIN_EMERGENCY_KEY: str = "BlackRose_ProjectAdmin_Emergency_Key_2026_Secure_Key"
    WEBHOOK_URL: str = ""
    WEBHOOK_SECRET: str = ""
    WEBHOOK_PATH: str = "/bot/webhook"
    INGEST_TOKEN: str = "dev_ingest_token"

    # Error Reporting
    HONEYBADGER_API_KEY: str = ""

    # Initial Admin (for setup)
    INITIAL_ADMIN: str = ""
    INITIAL_ADMINS: str = "" # multi-admin format

    # Logging
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "production"

    # Redis
    REDIS_URL: str = ""

    # AI Translation & LLM Services
    HF_TOKEN: str = ""
    HF_DATASET_REPO: str = "" # e.g. "Nihronick/blackrose-media"
    DEEPL_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    NVIDIA_API_KEY: str = "" # https://build.nvidia.com/ (Llama 3.3 70B, DeepSeek V3, Qwen 2.5 72B)
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    AI_TRANSLATION_PROVIDER: str = "auto" # auto | nvidia | gemini | deepseek | groq | hf | google

    # Inngest Background Jobs
    INNGEST_SIGNING_KEY: str = ""
    INNGEST_EVENT_KEY: str = ""

    # Media Optimization (imgproxy)
    IMGPROXY_URL: str = "" # e.g. "https://img.blackrose.ru"
    IMGPROXY_KEY: str = ""
    IMGPROXY_SALT: str = ""

    # Git-Sync (Wiki-style backup)
    GITHUB_TOKEN: str = ""
    GITHUB_REPO: str = "" # e.g. "Nihronick/blackrose-wiki"
    GITHUB_BRANCH: str = "main"

    # Telegram Notification Settings
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    # Frontend/WebApp
    FRONTEND_URL: str = "http://localhost:5173"
    MINIAPP_URL: Optional[str] = None

    # AIO Sandbox (agent environment)
    SANDBOX_URL: str = "http://sandbox:8080"
    SANDBOX_API_KEY: str = "blackrose-dev-key"
    @property
    def admin_user_ids(self) -> set[int]:
        if not self.ADMIN_USERS:
            return set()
        return {int(x.strip()) for x in self.ADMIN_USERS.split(",") if x.strip().isdigit()}

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def BASE_DIR(self) -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @property
    def GLOSSARY_PATH(self) -> str:
        return os.path.join(self.BASE_DIR, "core", "glossary.json")

    @property
    def LOGS_DIR(self) -> str:
        return os.path.join(os.path.dirname(self.BASE_DIR), "logs")

settings = Settings()

def get_settings() -> Settings:
    return settings

