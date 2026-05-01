"""
BlackRose Bot v2 — webhook + polling fallback.

В Koyeb контейнере бот запускается рядом с FastAPI на том же порту НЕТ —
бот запускает свой собственный aiohttp сервер на порту 8443 (внутренний).
Nginx/Koyeb проксирует /bot/webhook → порт 8443.

Либо проще: бот слушает на отдельном порту BOT_PORT (по умолчанию 8443),
FastAPI на PORT (8080). Koyeb видит только один внешний порт (8080),
поэтому webhook регистрируем через WEBHOOK_URL без порта.

Самый простой вариант для Koyeb: polling режим для бота,
webhook только если WEBHOOK_URL явно задан.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import API_TOKEN, WEBHOOK_PATH, WEBHOOK_SECRET, WEBHOOK_URL
from handlers.errors import router as errors_router
from handlers.miniapp import miniapp_router
from handlers.admin import admin_router
from loguru import logger

# ── Логи ─────────────────────────────────────────────────────
Path("logs").mkdir(exist_ok=True)
logger.remove()
logger.add(sys.stdout, level="INFO", colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan> | <level>{message}</level>")
logger.add("logs/bot_{time:YYYY-MM-DD}.log", rotation="00:00", retention="7 days",
    level="DEBUG", encoding="utf-8")


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
for _n in ("aiogram.event", "aiohttp.access"):
    logging.getLogger(_n).setLevel(logging.WARNING)

# ── Bot + Dispatcher ─────────────────────────────────────────
bot = Bot(token=API_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())

dp.include_router(errors_router)
dp.include_router(miniapp_router)
dp.include_router(admin_router)


# ── Shutdown ─────────────────────────────────────────────────
async def shutdown():
    logger.info("🛑 Bot shutting down...")
    await bot.session.close()
    await dp.storage.close()


# ── Main ─────────────────────────────────────────────────────
async def main():
    if WEBHOOK_URL:
        # Webhook режим — регистрируем и запускаем aiohttp сервер
        from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
        from aiohttp import web

        BOT_PORT = int(os.getenv("BOT_PORT", "8443"))

        async def on_startup(app):
            target = f"{WEBHOOK_URL.rstrip('/')}{WEBHOOK_PATH}"
            info = await bot.get_webhook_info()
            if info.url != target:
                await bot.set_webhook(url=target, secret_token=WEBHOOK_SECRET or None,
                                      drop_pending_updates=True)
                logger.info(f"✅ Webhook: {target}")

        async def on_shutdown(app):
            await bot.delete_webhook()
            await shutdown()

        app = web.Application()
        app.on_startup.append(on_startup)
        app.on_shutdown.append(on_shutdown)

        async def health(req):
            return web.json_response({"status": "ok", "mode": "webhook"})
        app.router.add_get("/health", health)

        SimpleRequestHandler(dispatcher=dp, bot=bot,
                             secret_token=WEBHOOK_SECRET or None).register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)

        runner = web.AppRunner(app)
        await runner.setup()
        await web.TCPSite(runner, "0.0.0.0", BOT_PORT).start()
        logger.info(f"🤖 Bot webhook server on port {BOT_PORT}")
        try:
            await asyncio.Event().wait()
        finally:
            await runner.cleanup()
    else:
        # Polling режим (локально или если WEBHOOK_URL не задан)
        logger.info("🔄 Bot polling mode")
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass
        finally:
            await shutdown()


if __name__ == "__main__":
    asyncio.run(main())
