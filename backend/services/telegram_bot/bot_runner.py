import asyncio
from core.config import settings
from core.logging import get_logger
from core.http import http_client

logger = get_logger("blackrose.telegram_bot")

class TelegramBotRunner:
    def __init__(self):
        self._task = None
        self._running = False

    async def start(self):
        token = settings.BOT_TOKEN
        if not token or len(token) < 20:
            logger.info("Telegram Bot Token is not configured, bot runner skipped.")
            return

        self._running = True
        self._task = asyncio.create_task(self._poll_loop(token))
        logger.info("Telegram Bot Runner started polling.")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()

    async def _poll_loop(self, token: str):
        offset = 0
        # Clear any existing webhook conflict to allow polling
        try:
            delete_url = f"https://api.telegram.org/bot{token}/deleteWebhook"
            await http_client.post(delete_url, json={"drop_pending_updates": False}, timeout=10.0)
            logger.info("Telegram Bot Webhook cleared successfully for polling mode.")
        except Exception as e:
            logger.warning(f"Telegram deleteWebhook notice: {e}")

        get_updates_url = f"https://api.telegram.org/bot{token}/getUpdates"
        send_msg_url = f"https://api.telegram.org/bot{token}/sendMessage"
        app_url = (settings.FRONTEND_URL or "https://blackrosesl.me/").rstrip("/") + "/"

        while self._running:
            try:
                params = {"offset": offset, "timeout": 15, "allowed_updates": '["message"]'}
                res = await http_client.get(get_updates_url, params=params, timeout=20.0)
                if res.status_code == 200:
                    data = res.json()
                    for update in data.get("result", []):
                        offset = update["update_id"] + 1
                        msg = update.get("message", {})
                        chat_id = msg.get("chat", {}).get("id")

                        if chat_id:
                            first_name = msg.get("from", {}).get("first_name", "Слеер")
                            reply_text = (
                                f"🌹 *Приветствуем, {first_name}!*\n\n"
                                f"Добро пожаловать в *BlackRose* — главное сообщество и базу знаний по *Slayer Legend*!\n\n"
                                f"Нажмите на **Inline-кнопку** ниже, чтобы войти в веб-приложение:"
                            )
                            keyboard = {
                                "inline_keyboard": [
                                    [
                                        {
                                            "text": "🚀 Открыть BlackRose App",
                                            "web_app": {"url": app_url}
                                        }
                                    ]
                                ]
                            }
                            await http_client.post(
                                send_msg_url,
                                json={
                                    "chat_id": chat_id,
                                    "text": reply_text,
                                    "parse_mode": "Markdown",
                                    "reply_markup": keyboard
                                },
                                timeout=10.0
                            )
            except asyncio.CancelledError:
                break
            except Exception as err:
                logger.debug(f"Telegram bot polling loop notice: {err}")
                await asyncio.sleep(5)

telegram_bot_runner = TelegramBotRunner()
