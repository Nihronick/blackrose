import asyncio
import os
from bot.telegram_bot import start_bot
from core.logging import get_logger

logger = get_logger("blackrose.bot.runner")

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.info("TELEGRAM_BOT_TOKEN is not configured. Telegram bot polling disabled.")
        return
    logger.info("Starting BlackRose Telegram Bot...")
    asyncio.run(start_bot())

if __name__ == "__main__":
    main()
