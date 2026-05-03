import logging
import html
import re
from urllib.parse import quote
import aiohttp
from core.config import settings

logger = logging.getLogger("blackrose.services.notifications")

class TelegramService:
    def __init__(self):
        self.bot_token = settings.BOT_TOKEN
        self.base_url = settings.MINIAPP_URL or settings.FRONTEND_URL.split(",")[0].strip()

    async def notify_new_guide(self, guide_key: str, guide_title: str, category_key: str, user_ids: list[int]):
        if not self.bot_token or not user_ids or not self.base_url:
            return 0, 0

        webapp_url = f"{self.base_url.rstrip('/')}?guide={quote(guide_key, safe='')}"
        msg_text = f"🆕 Новый гайд в <b>BlackRose</b>!\n\n📖 <b>{html.escape(guide_title)}</b>\nКатегория: {html.escape(category_key)}"
        
        reply_markup = {"inline_keyboard": [[{"text": "📖 Открыть гайд", "web_app": {"url": webapp_url}}]]}
        api = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        sent = 0
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            for uid in user_ids:
                try:
                    async with session.post(api, json={
                        "chat_id": uid, "text": msg_text, "parse_mode": "HTML", "reply_markup": reply_markup
                    }) as r:
                        if r.status == 200: sent += 1
                except Exception as e:
                    logger.debug(f"Failed to notify {uid}: {e}")
        return sent

telegram_service = TelegramService()
