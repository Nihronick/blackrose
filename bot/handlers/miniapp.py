"""
MiniApp handler — показывает кнопку WebApp при /start, /guides
и как постоянную reply-клавиатуру.
"""
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    WebAppInfo,
)
from config import MINIAPP_URL
from loguru import logger

miniapp_router = Router()


def get_reply_keyboard() -> ReplyKeyboardMarkup:
    """Постоянная reply-клавиатура с кнопкой WebApp."""
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(
                text="📖 Открыть гайды",
                web_app=WebAppInfo(url=MINIAPP_URL),
            )
        ]],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_inline_keyboard() -> InlineKeyboardMarkup:
    """Inline-кнопка WebApp в сообщении."""
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="📖 Открыть гайды",
                web_app=WebAppInfo(url=MINIAPP_URL),
            )
        ]]
    )


@miniapp_router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    logger.info(f"👋 /start от {user.id} ({user.first_name})")
    await message.answer(
        f"👋 Привет, <b>{user.first_name}</b>!\n\n"
        f"🗡 Добро пожаловать в <b>BlackRose</b>.\n\n"
        f"Нажмите кнопку <b>«📖 Открыть гайды»</b> внизу экрана.",
        parse_mode="HTML",
        reply_markup=get_reply_keyboard(),
    )


@miniapp_router.message(Command("guides", "miniapp", "app"))
async def cmd_guides(message: Message):
    user = message.from_user
    logger.info(f"📖 /guides от {user.id} ({user.first_name})")
    await message.answer(
        "🗡 <b>BlackRose Guides</b>\n\n"
        "Нажмите кнопку ниже или используйте кнопку внизу экрана.",
        parse_mode="HTML",
        reply_markup=get_inline_keyboard(),
    )


@miniapp_router.message(Command("help"))
async def cmd_help(message: Message):
    logger.info(f"❓ /help от {message.from_user.id}")
    await message.answer(
        "📚 <b>Доступные команды:</b>\n\n"
        "/start — Приветствие и кнопка\n"
        "/guides — Открыть справочник гильдии\n"
        "/help — Эта справка\n\n"
        "💡 Кнопка <b>«📖 Открыть гайды»</b> всегда доступна внизу экрана.",
        parse_mode="HTML",
        reply_markup=get_reply_keyboard(),
    )
