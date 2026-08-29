"""
Клиент бэкенда BlackRose: авторизация, кэш медиа, ingestion, управление категориями.
"""
import json
import os
from typing import Dict, List, Optional

from .config import BACKEND_URL, ADMIN_USER, ADMIN_PASS, ssl_ctx, http_request


class BackendClient:
    """Клиент API бэкенда BlackRose (FastAPI на Hugging Face Spaces)."""

    jwt_token: str = ""

    @classmethod
    def login(cls) -> str:
        """Авторизация администратора, получение JWT."""
        url = f"{BACKEND_URL}/api/auth/emergency-login"
        body = json.dumps({"emergency_key": os.getenv("ADMIN_EMERGENCY_KEY", "")}).encode("utf-8")
        status, data = http_request(url, data=body,
                                    headers={"Content-Type": "application/json"},
                                    method="POST", timeout=15)
        if status == 200 and isinstance(data, dict):
            cls.jwt_token = data.get("token") or data.get("access_token", "")
            return cls.jwt_token

        # Fallback на стандартный логин
        url = f"{BACKEND_URL}/api/auth/login"
        body = json.dumps({"username": ADMIN_USER, "password": ADMIN_PASS}).encode("utf-8")
        status, data = http_request(url, data=body,
                                    headers={"Content-Type": "application/json"},
                                    method="POST", timeout=15)
        if status == 200 and isinstance(data, dict):
            cls.jwt_token = data.get("token") or data.get("access_token", "")
        else:
            cls.jwt_token = ""
        return cls.jwt_token

    @classmethod
    def _auth_headers(cls) -> Dict[str, str]:
        return {"Authorization": f"Bearer {cls.jwt_token}", "Content-Type": "application/json"}

    @classmethod
    def persist_media(cls, raw_url: str) -> str:
        """Перманентное кэширование медиа через бэкенд. Возвращает постоянный URL."""
        if not raw_url or not cls.jwt_token:
            return raw_url
        # Уже перманентная ссылка
        if any(h in raw_url for h in ["huggingface.co", "nihronick", "/api/media/"]):
            return raw_url
        try:
            url = f"{BACKEND_URL}/api/admin/media/import-url"
            body = json.dumps({"url": raw_url}).encode("utf-8")
            status, data = http_request(url, data=body, headers=cls._auth_headers(),
                                        method="POST", timeout=20)
            if status == 200 and isinstance(data, dict):
                return data.get("permanent_url") or data.get("url") or raw_url
        except Exception:
            pass
        return raw_url

    @classmethod
    def ingest_guide(cls, guide_key: str, cat_key: str, cat_title: str,
                     title: str, text: str, photos: List[str],
                     videos: List[str], sort_order: int) -> dict:
        """Отправка гайда на продакшен через /api/webhook/ingest."""
        url = f"{BACKEND_URL}/api/webhook/ingest"
        body = json.dumps({
            "guide_key": guide_key,
            "category_key": cat_key,
            "category_title": cat_title,
            "title": title,
            "text": text,
            "photo": photos[:15],
            "video": videos[:10],
            "document": [],
            "sort_order": sort_order
        }).encode("utf-8")
        headers = {"Content-Type": "application/json", "X-Ingest-Token": os.getenv("INGEST_TOKEN", "")}
        status, data = http_request(url, data=body, headers=headers, method="POST", timeout=30)
        if isinstance(data, dict):
            return data
        return {"error": str(data)}

    @classmethod
    def register_sync_channel(cls, channel_id: str, channel_name: str, category_key: str):
        """Регистрация канала на фоновое автообновление (WebSocket)."""
        if not cls.jwt_token:
            return
        url = f"{BACKEND_URL}/api/admin/discord-sync/channels"
        body = json.dumps({
            "channel_id": str(channel_id),
            "channel_name": channel_name,
            "category_key": category_key,
            "auto_translate": True
        }).encode("utf-8")
        try:
            http_request(url, data=body, headers=cls._auth_headers(), method="POST", timeout=10)
        except Exception:
            pass

    @classmethod
    def clean_obsolete_categories(cls, valid_keys: set):
        """Удаление устаревших/мусорных категорий с сайта."""
        if not cls.jwt_token:
            return
        try:
            url = f"{BACKEND_URL}/api/categories"
            status, data = http_request(url, headers=cls._auth_headers(), timeout=10)
            if status != 200 or not isinstance(data, dict):
                return
            cats = data.get("categories", [])
            for c in cats:
                ckey = c.get("key")
                if ckey and ckey not in valid_keys:
                    del_url = f"{BACKEND_URL}/api/admin/category/{ckey}"
                    http_request(del_url, headers=cls._auth_headers(), method="DELETE", timeout=10)
                    print(f"  [x] Удален нерелевантный раздел: {ckey}")
        except Exception as e:
            print(f"  [WARN] Failed to clean categories: {e}")

    @classmethod
    def get_categories(cls) -> List[Dict]:
        """Получение списка категорий с сайта."""
        url = f"{BACKEND_URL}/api/categories"
        status, data = http_request(url, timeout=10)
        if status == 200 and isinstance(data, dict):
            return data.get("categories", [])
        return []
