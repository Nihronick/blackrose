"""
Клиент Discord API v10: каналы, треды, сообщения.
"""
import time
import json
from typing import Any, Dict, List, Tuple

from .config import DISCORD_TOKEN, GUILD_ID, ssl_ctx, http_request


class DiscordAPI:
    """Обёртка над Discord REST API v10."""

    BASE = "https://discord.com/api/v10"

    @classmethod
    def request(cls, path: str) -> Tuple[int, Any]:
        """GET-запрос к Discord API с авторизацией."""
        url = f"{cls.BASE}{path}"
        headers = {
            "Authorization": DISCORD_TOKEN,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        return http_request(url, headers=headers, timeout=20)

    @classmethod
    def get_guild_channels(cls, guild_id: str = "") -> List[Dict]:
        """Получение всех каналов гильдии."""
        gid = guild_id or GUILD_ID
        status, data = cls.request(f"/guilds/{gid}/channels")
        return data if status == 200 and isinstance(data, list) else []

    @classmethod
    def get_forum_threads(cls, channel_id: str) -> List[Dict]:
        """Получение всех тредов форума (активные + архивные с пагинацией)."""
        threads = []
        seen = set()

        # Активные треды
        s, data = cls.request(f"/guilds/{GUILD_ID}/threads/active")
        if s == 200 and isinstance(data, dict):
            for t in data.get("threads", []):
                if str(t.get("parent_id")) == channel_id and t["id"] not in seen:
                    threads.append(t)
                    seen.add(t["id"])

        # Архивные треды с пагинацией (до 15 страниц)
        before = None
        for _ in range(15):
            p = f"/channels/{channel_id}/threads/archived/public"
            if before:
                p += f"?before={before}"
            time.sleep(0.3)
            s, data = cls.request(p)
            if s != 200 or not isinstance(data, dict):
                break
            batch = data.get("threads", [])
            if not batch:
                break
            for t in batch:
                if t["id"] not in seen:
                    threads.append(t)
                    seen.add(t["id"])
            before = batch[-1].get("thread_metadata", {}).get("archive_timestamp")

        return threads

    @classmethod
    def get_messages(cls, channel_id: str, limit: int = 100) -> List[Dict]:
        """Получение последних сообщений канала/треда."""
        status, data = cls.request(f"/channels/{channel_id}/messages?limit={limit}")
        return data if status == 200 and isinstance(data, list) else []
