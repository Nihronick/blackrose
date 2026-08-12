import asyncio
from core.config import settings
from core.logging import get_logger
from services.telegram_bot.telegram_api import send_telegram_request

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

        res = await send_telegram_request(token, "deleteWebhook", payload={"drop_pending_updates": False})
        logger.info(f"Telegram deleteWebhook result: {res}")

        self._running = True
        self._task = asyncio.create_task(self._poll_loop(token))
        logger.info("Telegram Bot Runner started.")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()

    async def _poll_loop(self, token: str):
        offset = 0
        app_url = (settings.FRONTEND_URL or "https://blackrosesl.me/").rstrip("/") + "/"

        while self._running:
            try:
                res = await send_telegram_request(token, "getUpdates", params={"offset": offset, "timeout": 15}, timeout=20.0)
                if res.get("ok"):
                    for update in res.get("result", []):
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
                            await send_telegram_request(
                                token,
                                "sendMessage",
                                payload={
                                    "chat_id": chat_id,
                                    "text": reply_text,
                                    "parse_mode": "Markdown",
                                    "reply_markup": keyboard
                                }
                            )
            except asyncio.CancelledError:
                break
            except Exception as err:
                logger.debug(f"Telegram bot polling loop notice: {err}")
                await asyncio.sleep(5)

telegram_bot_runner = TelegramBotRunner()
