from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TELEGRAM_API_TOKEN: str
    ALLOWED_USERS:  str = ""
    ALLOWED_CHATS:  str = ""
    ADMIN_USERS:    str = ""
    ACCESS_MODE:    str = "users"
    MINIAPP_URL:    str = "https://your-frontend.up.railway.app"
    # URL бэкенда — нужен боту для /search и inline-режима
    API_URL:        str = ""

    TEXT_SPLIT_LIMIT: int   = 4000
    CAPTION_LIMIT:    int   = 1024
    DELETE_DELAY:     float = 0.1

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

if not settings.TELEGRAM_API_TOKEN:
    raise ValueError("TELEGRAM_API_TOKEN не задан!")

API_TOKEN     = settings.TELEGRAM_API_TOKEN
MINIAPP_URL   = settings.MINIAPP_URL
API_URL       = settings.API_URL
ACCESS_MODE   = settings.ACCESS_MODE
ALLOWED_USERS = set(int(x.strip()) for x in settings.ALLOWED_USERS.split(",") if x.strip().isdigit())
ALLOWED_CHATS = [int(x.strip()) for x in settings.ALLOWED_CHATS.split(",") if x.strip().lstrip("-").isdigit()]
ADMIN_USERS   = set(int(x.strip()) for x in settings.ADMIN_USERS.split(",") if x.strip().isdigit())
