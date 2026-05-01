import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Единственный токен бота — тот же что и в backend
    BOT_TOKEN: str

    # Администраторы бота (Telegram user_id через запятую)
    ADMIN_USERS: str = ""

    # URL фронтенда
    MINIAPP_URL: str = "https://nihronick.github.io/blackrose"

    # URL бэкенда — localhost т.к. бот и API в одном контейнере
    API_URL: str = f"http://localhost:{os.getenv('PORT', '7860')}"

    # Webhook — если пустой, бот работает в polling-режиме
    WEBHOOK_URL:    str = ""
    WEBHOOK_SECRET: str = ""
    WEBHOOK_PATH:   str = "/bot/webhook"

    TEXT_SPLIT_LIMIT: int   = 4000
    CAPTION_LIMIT:    int   = 1024
    DELETE_DELAY:     float = 0.1

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()  # type: ignore[call-arg]

if not settings.BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан!")

API_TOKEN      = settings.BOT_TOKEN
MINIAPP_URL    = settings.MINIAPP_URL
API_URL        = settings.API_URL
WEBHOOK_URL    = settings.WEBHOOK_URL
WEBHOOK_SECRET = settings.WEBHOOK_SECRET
WEBHOOK_PATH   = settings.WEBHOOK_PATH
ADMIN_USERS    = set(int(x.strip()) for x in settings.ADMIN_USERS.split(",") if x.strip().isdigit())
