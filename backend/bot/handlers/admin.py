from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from bot.middleware.admin import AdminMiddleware
from bot.lib.api_client import api_client

admin_router = Router()
# Подключаем middleware, чтобы роутер пропускал только админов
admin_router.message.middleware(AdminMiddleware())

@admin_router.message(Command("add_user"))
async def cmd_add_user(message: Message):
    args = message.text.split() if message.text else []
    if len(args) < 2 or not args[1].lstrip("-").isdigit():
        await message.answer("Использование: /add_user <user_id>")
        return
        
    target_id = int(args[1])
    res = await api_client.add_member(target_id, "member")
    if res and "_error" not in res:
        action = "добавлен" if res.get("created") else "обновлён"
        await message.answer(f"✅ Пользователь {target_id} {action}.")
    else:
        err = res.get("_error", "Unknown") if res else "Unknown"
        await message.answer(f"❌ Ошибка API: {err}")

@admin_router.message(Command("add_admin"))
async def cmd_add_admin(message: Message):
    args = message.text.split() if message.text else []
    if len(args) < 2 or not args[1].lstrip("-").isdigit():
        await message.answer("Использование: /add_admin <user_id>")
        return
        
    target_id = int(args[1])
    res = await api_client.add_member(target_id, "admin")
    if res and "_error" not in res:
        await message.answer(f"✅ Пользователь {target_id} назначен администратором.")
    else:
        err = res.get("_error", "Unknown") if res else "Unknown"
        await message.answer(f"❌ Ошибка API: {err}")

@admin_router.message(Command("remove_user"))
async def cmd_remove_user(message: Message):
    args = message.text.split() if message.text else []
    if len(args) < 2 or not args[1].lstrip("-").isdigit():
        await message.answer("Использование: /remove_user <user_id>")
        return
        
    target_id = int(args[1])
    res = await api_client.delete_member(target_id)
    if res and "_error" not in res:
        await message.answer(f"✅ Пользователь {target_id} удалён.")
    elif res and res.get("_error") == 404:
        await message.answer(f"❌ Пользователь {target_id} не найден.")
    else:
        err = res.get("_error", "Unknown") if res else "Unknown"
        await message.answer(f"❌ Ошибка API: {err}")

@admin_router.message(Command("members"))
async def cmd_members(message: Message):
    members = await api_client.get_members()
    if not members:
        await message.answer("Участников нет (или ошибка API).")
        return
        
    lines = ["👥 <b>Участники гильдии:</b>\n"]
    for m in members:
        role_icon = "👑" if m["role"] == "admin" else "👤"
        name = m.get("first_name") or m.get("username") or str(m["user_id"])
        lines.append(f"{role_icon} {name} (<code>{m['user_id']}</code>)")
    
    await message.answer("\n".join(lines), parse_mode="HTML")
