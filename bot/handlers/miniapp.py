"""
MiniApp handler — показывает кнопку WebApp при /start, /guides
и как постоянную reply-клавиатуру.

Примечание: reply-кнопка с WebAppInfo НЕ передаёт initData в Telegram-клиентах,
поэтому для администраторов используется inline-кнопка через /admin.
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
from config import ADMIN_USERS, MINIAPP_URL
from loguru import logger

miniapp_router = Router()


def get_reply_keyboard() -> ReplyKeyboardMarkup:
    """Постоянная reply-клавиатура для обычных пользователей."""
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
    """Inline-кнопка — единственный надёжный способ передать initData."""
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="📖 Открыть гайды",
                web_app=WebAppInfo(url=MINIAPP_URL),
            )
        ]]
    )


def get_admin_inline_keyboard() -> InlineKeyboardMarkup:
    """Inline-кнопка для администраторов (передаёт initData корректно)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="⚙️ Открыть как администратор",
                web_app=WebAppInfo(url=MINIAPP_URL),
            )
        ]]
    )


@miniapp_router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    is_admin = user.id in ADMIN_USERS
    logger.info(f"👋 /start от {user.id} ({user.first_name}), admin={is_admin}")

    await message.answer(
        f"👋 Привет, <b>{user.first_name}</b>!\n\n"
        f"🗡 Добро пожаловать в <b>BlackRose</b>.\n\n"
        f"Нажмите кнопку <b>«📖 Открыть гайды»</b> внизу экрана.",
        parse_mode="HTML",
        reply_markup=get_reply_keyboard(),
    )

    # Админам дополнительно отправляем inline-кнопку.
    # Только inline передаёт корректный initData, необходимый для доступа к панели.
    if is_admin:
        await message.answer(
            "🔑 <b>Вы администратор.</b>\n\n"
            "Для доступа к панели управления используйте кнопку ниже "
            "или команду /admin — она передаёт корректные данные авторизации.",
            parse_mode="HTML",
            reply_markup=get_admin_inline_keyboard(),
        )


@miniapp_router.message(Command("admin"))
async def cmd_admin(message: Message):
    user = message.from_user
    if user.id not in ADMIN_USERS:
        logger.warning(f"🚫 /admin отклонён для {user.id}")
        await message.answer("❌ У вас нет прав администратора.")
        return
    logger.info(f"⚙️ /admin от {user.id} ({user.first_name})")
    await message.answer(
        "⚙️ <b>Панель администратора</b>\n\n"
        "Нажмите кнопку ниже для входа.\n"
        "<i>Используйте именно эту кнопку — она передаёт данные авторизации корректно.</i>",
        parse_mode="HTML",
        reply_markup=get_admin_inline_keyboard(),
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
    user = message.from_user
    is_admin = user.id in ADMIN_USERS
    logger.info(f"❓ /help от {user.id}")

    admin_text = "\n/admin — Панель администратора\n" if is_admin else ""

    await message.answer(
        "📚 <b>Доступные команды:</b>\n\n"
        "/start — Приветствие и кнопка\n"
        "/guides — Открыть справочник гильдии\n"
        f"{admin_text}"
        "/help — Эта справка\n\n"
        "💡 Кнопка <b>«📖 Открыть гайды»</b> всегда доступна внизу экрана.",
        parse_mode="HTML",
        reply_markup=get_reply_keyboard(),
    )
