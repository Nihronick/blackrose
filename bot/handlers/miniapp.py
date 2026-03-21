"""
Bot handlers v2.2
Вход — только через inline-кнопку в одном сообщении.
Reply-клавиатура полностью убрана (не передаёт initData, визуальный мусор).
"""
import urllib.parse
import aiohttp

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    InlineQueryResultArticle, InputTextMessageContent,
    Message, ReplyKeyboardRemove,
    WebAppInfo, InlineQuery,
)
from config import ADMIN_USERS, MINIAPP_URL, API_URL
from loguru import logger

miniapp_router = Router()


# ── Keyboards ─────────────────────────────────────────

def get_open_keyboard(url: str | None = None) -> InlineKeyboardMarkup:
    """Inline-кнопка входа — единственный способ передать initData корректно."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="📖 Открыть гайды",
            web_app=WebAppInfo(url=url or MINIAPP_URL),
        )
    ]])


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Inline-кнопка для администраторов."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="⚙️ Открыть как администратор",
            web_app=WebAppInfo(url=MINIAPP_URL),
        )
    ]])


# ── Helpers ───────────────────────────────────────────

async def api_search(query: str) -> list[dict]:
    if not API_URL:
        return []
    try:
        url = f"{API_URL}/api/search?q={urllib.parse.quote(query)}"
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=4)) as r:
                if r.status == 200:
                    data = await r.json()
                    return data.get("results", [])
    except Exception as e:
        logger.warning(f"api_search error: {e}")
    return []


def guide_url(key: str) -> str:
    return f"{MINIAPP_URL}?guide={key}"


# ── /start ────────────────────────────────────────────

@miniapp_router.message(CommandStart())
async def cmd_start(message: Message):
    user     = message.from_user
    is_admin = user.id in ADMIN_USERS
    args     = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""

    logger.info(f"👋 /start uid={user.id} args={args!r} admin={is_admin}")

    # Deep link: /start guide_<key>
    if args.startswith("guide_"):
        guide_key = args[6:]
        await message.answer(
            f"👋 <b>{user.first_name}</b>, открываю гайд:",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove(),
        )
        await message.answer(
            "📖 Нажми кнопку чтобы открыть гайд:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text="📖 Открыть гайд",
                    web_app=WebAppInfo(url=guide_url(guide_key)),
                )
            ]]),
        )
        return

    # Одно сообщение с кнопкой — текст и кнопка вместе
    text = (
        f"👋 Привет, <b>{user.first_name}</b>!\n\n"
        f"🗡 Добро пожаловать в <b>BlackRose</b> — справочник гильдии."
    )
    if is_admin:
        text += "\n\n🔑 <i>Вы вошли как администратор.</i>"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📖 Открыть гайды",
                web_app=WebAppInfo(url=MINIAPP_URL),
            )],
            [InlineKeyboardButton(
                text="⚙️ Открыть как администратор",
                web_app=WebAppInfo(url=MINIAPP_URL),
            )],
        ])
    else:
        keyboard = get_open_keyboard()

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer(
        "⬇️ Выбери действие:",
        reply_markup=keyboard,
    )


# ── /guides ───────────────────────────────────────────

@miniapp_router.message(Command("guides", "miniapp", "app"))
async def cmd_guides(message: Message):
    user     = message.from_user
    is_admin = user.id in ADMIN_USERS
    logger.info(f"📖 /guides uid={user.id} admin={is_admin}")

    if is_admin:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📖 Открыть гайды",
                web_app=WebAppInfo(url=MINIAPP_URL),
            )],
            [InlineKeyboardButton(
                text="⚙️ Открыть как администратор",
                web_app=WebAppInfo(url=MINIAPP_URL),
            )],
        ])
    else:
        keyboard = get_open_keyboard()

    await message.answer(
        "🗡 <b>BlackRose Guides</b> — справочник гильдии",
        parse_mode="HTML",
        reply_markup=keyboard,
    )


# ── /admin ────────────────────────────────────────────

@miniapp_router.message(Command("admin"))
async def cmd_admin(message: Message):
    user = message.from_user
    if user.id not in ADMIN_USERS:
        logger.warning(f"🚫 /admin denied uid={user.id}")
        await message.answer("❌ У вас нет прав администратора.")
        return
    logger.info(f"⚙️ /admin uid={user.id}")
    await message.answer(
        "⚙️ <b>Панель администратора</b>",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(),
    )


# ── /search ───────────────────────────────────────────

@miniapp_router.message(Command("search"))
async def cmd_search(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or len(args[1].strip()) < 2:
        await message.answer(
            "🔍 <b>Поиск гайдов</b>\n\n"
            "Использование: <code>/search &lt;запрос&gt;</code>\n\n"
            "Пример: <code>/search промоут</code>",
            parse_mode="HTML",
        )
        return

    query = args[1].strip()
    logger.info(f"🔍 /search uid={message.from_user.id} q={query!r}")

    results = await api_search(query)
    if not results:
        await message.answer(
            f"🔍 По запросу <b>{query}</b> ничего не найдено.",
            parse_mode="HTML",
        )
        return

    buttons = [
        [InlineKeyboardButton(text=f"📖 {g['title']}", web_app=WebAppInfo(url=guide_url(g["key"])))]
        for g in results[:8]
    ]
    await message.answer(
        f"🔍 Результаты по <b>{query}</b>:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


# ── /help ─────────────────────────────────────────────

@miniapp_router.message(Command("help"))
async def cmd_help(message: Message):
    user     = message.from_user
    is_admin = user.id in ADMIN_USERS
    admin_text = "\n/admin — Панель администратора\n" if is_admin else ""
    await message.answer(
        "📚 <b>Доступные команды:</b>\n\n"
        "/start — Приветствие и кнопка входа\n"
        "/guides — Открыть справочник\n"
        "/search &lt;запрос&gt; — Найти гайд\n"
        f"{admin_text}"
        "/help — Эта справка\n\n"
        "🔎 Inline-поиск: введите <code>@blackrosesl1_bot запрос</code> в любом чате.",
        parse_mode="HTML",
    )


# ── Уведомления подписчикам ───────────────────────────

async def notify_subscribers(
    bot,
    guide_key: str,
    guide_title: str,
    category_key: str,
) -> int:
    """Fetch subscriber list from backend and push Telegram notifications.
    Returns number of successfully sent messages."""
    if not API_URL or not MINIAPP_URL:
        return 0
    try:
        from config import API_TOKEN as _token
        payload = {
            "guide_key":    guide_key,
            "guide_title":  guide_title,
            "category_key": category_key,
            "bot_token":    _token,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/api/internal/notify",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as r:
                if r.status != 200:
                    logger.warning(f"notify endpoint status: {r.status}")
                    return 0
                data = await r.json()

        user_ids = data.get("user_ids", [])
        if not user_ids:
            return 0

        url = f"{MINIAPP_URL}?guide={guide_key}"
        text = (
            f"🆕 Новый гайд в <b>BlackRose</b>!\n\n"
            f"📖 <b>{guide_title}</b>\n"
            f"Категория: {category_key}"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="📖 Открыть гайд",
                web_app=WebAppInfo(url=url),
            )
        ]])

        sent = 0
        for uid in user_ids:
            try:
                await bot.send_message(uid, text, parse_mode="HTML", reply_markup=kb)
                sent += 1
            except Exception as e:
                logger.debug(f"notify skip uid={uid}: {e}")

        logger.info(f"Notifications sent: {sent}/{len(user_ids)} for guide={guide_key}")
        return sent
    except Exception as e:
        logger.warning(f"notify_subscribers error: {e}")
        return 0


# ── Inline-режим ──────────────────────────────────────

@miniapp_router.inline_query()
async def inline_search(query: InlineQuery):
    q = query.query.strip()
    logger.info(f"🔎 inline uid={query.from_user.id} q={q!r}")

    if len(q) < 2:
        await query.answer(
            results=[InlineQueryResultArticle(
                id="tip",
                title="🗡 BlackRose Guides",
                description="Введите название гайда для поиска",
                input_message_content=InputTextMessageContent(
                    message_text="🗡 <b>BlackRose Guides</b> — справочник гильдии\nОткройте бота: @blackrosesl1_bot",
                    parse_mode="HTML",
                ),
            )],
            cache_time=10,
        )
        return

    results_data = await api_search(q)
    if not results_data:
        await query.answer(
            results=[InlineQueryResultArticle(
                id="noresult",
                title="Ничего не найдено",
                description=f"По запросу «{q}» гайдов нет",
                input_message_content=InputTextMessageContent(
                    message_text=f"🔍 По запросу «{q}» в BlackRose Guides ничего не найдено.",
                ),
            )],
            cache_time=10,
        )
        return

    items = []
    for g in results_data[:10]:
        url = guide_url(g["key"])
        items.append(InlineQueryResultArticle(
            id=g["key"],
            title=g["title"],
            description=f"📂 {g.get('category_key', '')} · Открыть в BlackRose",
            thumbnail_url=g.get("icon") or None,
            input_message_content=InputTextMessageContent(
                message_text=f"📖 <b>{g['title']}</b>\n\nОткрыть в BlackRose Guides:",
                parse_mode="HTML",
            ),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text="📖 Открыть гайд",
                    web_app=WebAppInfo(url=url),
                )
            ]]),
        ))

    await query.answer(results=items, cache_time=30)
