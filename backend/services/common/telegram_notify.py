import httpx
from core.config import get_settings
from core.logging import get_logger

logger = get_logger("blackrose.services.telegram_notify")

class TelegramNotifyService:
    @classmethod
    async def send_guide_notification(
        cls,
        title: str,
        category_key: str,
        guide_key: str,
        author_tag: str | None = None,
        chat_id: str | None = None,
        bot_token: str | None = None,
    ) -> bool:
        settings = get_settings()
        token = bot_token or settings.TELEGRAM_BOT_TOKEN
        target_chat = chat_id or settings.TELEGRAM_CHAT_ID

        if not token or not target_chat:
            logger.info("Telegram notification skipped: bot token or chat ID not set")
            return False

        message = (
            f"<b>🔥 Новый гайд на сайте BlackRose!</b>\n\n"
            f"📖 <b>{title}</b>\n"
            f"📂 <b>Категория:</b> {category_key}\n"
        )
        if author_tag:
            message += f"✍️ <b>Автор в Discord:</b> {author_tag}\n"

        message += f"\n👉 <a href='https://blackrosesl.me/#/guide/{guide_key}'><b>Читать гайд на сайте</b></a>"

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": target_chat,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    logger.info(f"Telegram notification sent for guide {guide_key}")
                    return True
                else:
                    logger.warning(f"Failed to send Telegram message: {res.status_code} {res.text}")
                    return False
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
            return False


telegram_notify_service = TelegramNotifyService()
