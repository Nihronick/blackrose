import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from core.logging import get_logger
from services.guides.service import guide_service, category_service
from services.guilds.service import guild_service

logger = get_logger("blackrose.bot")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://blackrosesl.me")

dp = Dispatcher()

def get_main_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text="📱 Открыть BlackRose Mini App",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ],
        [
            InlineKeyboardButton(text="📚 Каталог гайдов", callback_data="btn_categories"),
            InlineKeyboardButton(text="⚔️ Билд-планер", web_app=WebAppInfo(url=f"{WEBAPP_URL}/build-planner")),
        ],
        [
            InlineKeyboardButton(text="🏰 Гильдии", callback_data="btn_guilds"),
            InlineKeyboardButton(text="🔍 Поиск", callback_data="btn_search_hint"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Приветственное сообщение с кнопкой запуска Mini App."""
    user_name = message.from_user.first_name if message.from_user else "Охотник"
    text = (
        f"👋 **Привет, {user_name}!**\n\n"
        f"Добро пожаловать в официальный бот сообщества **BlackRose (Slayer Legend)**!\n\n"
        f"📖 **База знаний:** 100+ гайдов по боссам, промоушенам и духам\n"
        f"🏰 **Система гильдий:** ростеры, ранги и заявки\n"
        f"⚔️ **Калькулятор:** расчет урона и подбор билдов\n\n"
        f"Нажмите кнопку ниже, чтобы запустить приложение:"
    )
    await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="Markdown")


@dp.message(Command("guides"))
@dp.callback_query(F.data == "btn_categories")
async def show_categories(event: types.Message | types.CallbackQuery):
    """Показывает 14 официальных категорий Slayerpedia."""
    cats = await category_service.get_all()
    if not cats:
        msg_text = "Категории пока не загружены."
        if isinstance(event, types.CallbackQuery):
            await event.message.edit_text(msg_text)
            await event.answer()
        else:
            await event.answer(msg_text)
        return

    buttons = []
    # Раскладываем по 2 кнопки в ряд
    row = []
    for c in cats:
        row.append(
            InlineKeyboardButton(
                text=f"📂 {c.get('title', c.get('key'))}",
                web_app=WebAppInfo(url=f"{WEBAPP_URL}/category/{c.get('key')}")
            )
        )
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton(text="⬅️ Главное меню", callback_data="btn_main_menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    text = "📚 **Официальные разделы Slayerpedia:**\nВыберите категорию для перехода:"
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb, parse_mode="Markdown")


@dp.message(Command("guilds"))
@dp.callback_query(F.data == "btn_guilds")
async def show_guilds(event: types.Message | types.CallbackQuery):
    """Показывает информацию о гильдиях."""
    guilds = await guild_service.get_all_guilds()
    text = "🏰 **Гильдии BlackRose:**\n\n"
    if not guilds:
        text += "Список гильдий пуст."
    else:
        for g in guilds:
            text += f"• **{g.get('name')}** — {g.get('member_count', 0)}/{g.get('max_members', 20)} участников\n"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Открыть в Mini App", web_app=WebAppInfo(url=f"{WEBAPP_URL}/guilds"))],
        [InlineKeyboardButton(text="⬅️ Главное меню", callback_data="btn_main_menu")]
    ])

    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb, parse_mode="Markdown")


@dp.callback_query(F.data == "btn_main_menu")
async def callback_main_menu(call: types.CallbackQuery):
    await call.message.edit_text(
        "🗡️ **BlackRose Slayer Legend Knowledge Hub**\nВыберите действие:",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )
    await call.answer()


@dp.callback_query(F.data == "btn_search_hint")
async def callback_search_hint(call: types.CallbackQuery):
    await call.message.answer(
        "🔍 Чтобы найти гайд, просто напишите `/search <запрос>` или любое слово в чат бота (например: `Блиц Голд`, `Духи`, `Ярость`).",
        parse_mode="Markdown"
    )
    await call.answer()


@dp.message(Command("search"))
async def cmd_search(message: types.Message):
    """Поиск по базе знаний."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("ℹ️ Использование: `/search <название гайда или темы>`\nПример: `/search Блиц Голд`", parse_mode="Markdown")
        return

    q = args[1].strip()
    guides = await guide_service.search(q)
    if not guides:
        await message.answer(f"🥀 По запросу «{q}» ничего не найдено.")
        return

    text = f"🔍 **Результаты поиска по «{q}» ({len(guides)}):**\n\n"
    buttons = []
    for g in guides[:5]:
        title = g.get("title", "Гайд")
        key = g.get("key", "")
        text += f"• **{title}**\n"
        buttons.append([
            InlineKeyboardButton(text=f"📖 {title[:35]}", web_app=WebAppInfo(url=f"{WEBAPP_URL}/guide/{key}"))
        ])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")


@dp.message(F.text & ~F.text.startswith("/"))
async def handle_text_search(message: types.Message):
    """Автоматический поиск при отправке текста без слэша."""
    q = message.text.strip()
    if len(q) < 2:
        return
    guides = await guide_service.search(q)
    if not guides:
        return

    buttons = [
        [InlineKeyboardButton(text=f"📖 {g.get('title', 'Гайд')[:35]}", web_app=WebAppInfo(url=f"{WEBAPP_URL}/guide/{g.get('key')}"))]
        for g in guides[:4]
    ]
    buttons.append([InlineKeyboardButton(text="📱 Открыть поиск в Mini App", web_app=WebAppInfo(url=f"{WEBAPP_URL}/search"))])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(f"🔍 Найдено по запросу «{q}»:", reply_markup=kb)


async def start_bot():
    """Запуск long-polling бота (если задан токен)."""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN не задан, бот не запущен.")
        return
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    logger.info("Запуск Telegram Bot (aiogram 3.x)...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())
