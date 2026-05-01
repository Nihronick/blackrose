"""
BlackRose Bot v2 — hardened for Hugging Face / modern hosting.
Uses IPv4 forcing and robust error handling for connection stability.
"""

import asyncio
import logging
import os
import sys
import socket
from pathlib import Path

import aiohttp
from aiohttp import TCPConnector
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from loguru import logger

from config import API_TOKEN, WEBHOOK_PATH, WEBHOOK_SECRET, WEBHOOK_URL
from handlers.errors import router as errors_router
from handlers.miniapp import miniapp_router
from handlers.admin import admin_router

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

# ── Dispatcher ───────────────────────────────────────────────
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(errors_router)
dp.include_router(miniapp_router)
dp.include_router(admin_router)


async def perform_shutdown(bot: Bot):
    logger.info("🛑 Bot shutting down...")
    if bot:
        await bot.session.close()
    await dp.storage.close()


async def main():
    # Принудительно используем IPv4 для обхода проблем с SSL Handshake (60s timeout)
    # В aiogram 3 параметры коннектора передаются через _connector_init
    session = AiohttpSession(timeout=40.0)
    session._connector_init = {"family": socket.AF_INET}
    bot = Bot(token=API_TOKEN, session=session)

    try:
        if WEBHOOK_URL:
            # Webhook режим
            from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
            from aiohttp import web

            BOT_PORT = int(os.getenv("BOT_PORT", "8443"))

            async def on_startup(app):
                target = f"{WEBHOOK_URL.rstrip('/')}{WEBHOOK_PATH}"
                info = await bot.get_webhook_info()
                if info.url != target:
                    await bot.set_webhook(url=target, secret_token=WEBHOOK_SECRET or None,
                                          drop_pending_updates=True)
                    logger.info(f"✅ Webhook set to: {target}")

            async def on_shutdown(app):
                await bot.delete_webhook()

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
            # Polling режим
            logger.info("🔄 Bot polling mode")
            try:
                logger.info("Checking Telegram connection (deleting webhook)...")
                try:
                    await asyncio.wait_for(bot.delete_webhook(drop_pending_updates=True), timeout=15.0)
                    logger.info("✅ Webhook deleted successfully")
                except Exception as e:
                    logger.warning(f"⚠️ Could not delete webhook: {e}. Attempting to start polling anyway...")
                
                await dp.start_polling(bot)
            except Exception as e:
                logger.error(f"❌ Critical polling error: {e}")
                await asyncio.sleep(5)
    finally:
        await perform_shutdown(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
