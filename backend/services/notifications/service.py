import httpx
from core.config import settings
from core.logging import get_logger

logger = get_logger("blackrose.services.notifications")

class NotificationService:
    @classmethod
    async def send_telegram_message(cls, user_id: int, text: str) -> bool:
        """Sends a direct message to a user via the Telegram Bot API."""
        token = settings.BOT_TOKEN
        if not token or not user_id:
            logger.debug("Skipping Telegram notification: BOT_TOKEN or user_id missing")
            return False

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": user_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    logger.info(f"Telegram notification sent to user {user_id}")
                    return True
                else:
                    logger.warning(f"Telegram notification failed ({res.status_code}): {res.text}")
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
        return False

    @classmethod
    async def notify_request_approved(cls, user_id: int, guild_name: str):
        text = f"🎉 <b>Ваша заявка принята!</b>\n\nВы успешно зачислены в гильдию <b>{guild_name}</b>. Зайдите в приложение, чтобы отслеживать свой ранг и стадию!"
        await cls.send_telegram_message(user_id, text)

    @classmethod
    async def notify_request_rejected(cls, user_id: int, guild_name: str):
        text = f"ℹ️ <b>Заявка в гильдию</b>\n\nВаша заявка на вступление в гильдию <b>{guild_name}</b> была отклонена."
        await cls.send_telegram_message(user_id, text)

    @classmethod
    async def notify_rank_updated(cls, user_id: int, guild_name: str, new_rank: int, rank_name: str):
        text = f"🏆 <b>Обновление ранга в гильдии!</b>\n\nВаш ранг в гильдии <b>{guild_name}</b> был изменён на <b>{new_rank} ({rank_name})</b>."
        await cls.send_telegram_message(user_id, text)

notification_service = NotificationService()
