"""
Этап 1: Сбор сырых данных из Discord API.
"""
import sys
import time
from typing import Dict, List

from .config import DISCORD_TOKEN, GUILD_ID, SKIP_CHANNEL_NAMES
from .discord_client import DiscordAPI


def run() -> List[Dict]:
    """Извлечение полного дерева каналов, тредов и сообщений из Discord."""
    print("\n" + "=" * 60)
    print("  📥 Этап 1: Сбор данных из Discord API")
    print("=" * 60)

    if not DISCORD_TOKEN:
        print("❌ DISCORD_TOKEN не задан в .env!")
        sys.exit(1)

    # 1. Получаем все каналы гильдии
    all_channels = DiscordAPI.get_guild_channels(GUILD_ID)
    if not all_channels:
        print("❌ Не удалось получить каналы Discord. Проверьте DISCORD_TOKEN.")
        sys.exit(1)
    print(f"  [+] Всего каналов на сервере: {len(all_channels)}")

    # 2. Поиск категории базы знаний (Slayerpedia)
    parent_categories = {c["id"]: c for c in all_channels if c.get("type") == 4}
    slayerpedia_cat = next(
        (c for c in parent_categories.values()
         if any(w in c.get("name", "").lower() for w in ["slayerpedia", "guide", "spravochnik", "wiki"])),
        None
    )
    slayerpedia_id = slayerpedia_cat["id"] if slayerpedia_cat else None
    if slayerpedia_cat:
        print(f"  [+] Категория базы знаний: «{slayerpedia_cat['name']}» (ID: {slayerpedia_id})")

    # 3. Фильтрация каналов знаний
    knowledge_channels = [
        c for c in all_channels
        if c.get("type") in (0, 5, 15) and (
            c.get("parent_id") == slayerpedia_id or
            (not slayerpedia_id and not any(
                skip in c.get("name", "").lower()
                for skip in ["mod", "chat", "voice", "bot", "ticket", "log", "admin"]
            ))
        ) and not any(skip in c.get("name", "").lower() for skip in SKIP_CHANNEL_NAMES)
    ]
    knowledge_channels.sort(key=lambda x: (x.get("parent_id") != slayerpedia_id, x.get("position", 0)))
    print(f"  [+] Каналов с гайдами: {len(knowledge_channels)}")

    # 4. Загрузка контента каждого канала
    result = []
    for idx, ch in enumerate(knowledge_channels):
        ch_id = ch["id"]
        ch_name = ch.get("name", "unknown")
        ch_type = ch.get("type", 0)

        entry = {
            "channel_id": ch_id,
            "channel_name": ch_name,
            "channel_type": ch_type,
            "position": ch.get("position", 0),
            "threads": [],
            "messages": []
        }

        if ch_type == 15:
            # Форум: собираем все треды
            threads = DiscordAPI.get_forum_threads(ch_id)
            print(f"  [{idx+1}/{len(knowledge_channels)}] 📁 #{ch_name} (форум): {len(threads)} тредов")
            for ti, th in enumerate(threads):
                time.sleep(0.3)
                msgs = DiscordAPI.get_messages(th["id"], limit=50)
                entry["threads"].append({
                    "thread_id": th["id"],
                    "thread_name": th.get("name", "Guide"),
                    "messages": msgs
                })
                if (ti + 1) % 10 == 0:
                    print(f"    ...загружено {ti+1}/{len(threads)} тредов")
        else:
            # Текстовый / анонс-канал
            msgs = DiscordAPI.get_messages(ch_id, limit=100)
            entry["messages"] = msgs
            print(f"  [{idx+1}/{len(knowledge_channels)}] 📄 #{ch_name}: {len(msgs)} сообщений")

        result.append(entry)
        time.sleep(0.3)

    total_threads = sum(len(ch["threads"]) for ch in result)
    total_msgs = sum(len(ch["messages"]) for ch in result)
    print(f"\n  ✅ Этап 1 завершен: {len(result)} каналов, {total_threads} тредов, {total_msgs} сообщений")
    return result
