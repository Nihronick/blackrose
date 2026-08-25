"""
Этап 8: Атомарная выгрузка проверенных гайдов на продакшен (API Backend).
"""
import time
from typing import Dict, List

from .backend_client import BackendClient


def run(passed_guides: List[Dict], channels_data: List[Dict] = None) -> Dict[str, int]:
    """Этап 8: загрузка валидированных гайдов на боевой сервер."""
    print("\n" + "=" * 60)
    print("  🚀 Этап 8: Выкатка на продакшен (Atomic Deploy)")
    print("=" * 60)

    BackendClient.login()

    # 1. Извлекаем уникальные категории и инициализируем их
    categories_map = {}
    for g in passed_guides:
        ckey = g["category_key"]
        ctitle = g.get("category_title_ru") or g.get("category_name", ckey)
        if ckey not in categories_map:
            categories_map[ckey] = {
                "title": ctitle,
                "sort_order": len(categories_map)
            }

    print(f"  [+] Инициализация {len(categories_map)} категорий на сайте...")
    for ckey, cinfo in categories_map.items():
        BackendClient.ingest_guide(
            guide_key=f"cat_init_{ckey}",
            cat_key=ckey,
            cat_title=cinfo["title"],
            title=f"Категория {cinfo['title']}",
            text="Инициализация раздела",
            photos=[],
            videos=[],
            sort_order=cinfo["sort_order"]
        )

    # 2. Очистка неактуальных разделов
    BackendClient.clean_obsolete_categories(set(categories_map.keys()))

    # 3. Заливка гайдов
    print(f"\n  [+] Загрузка {len(passed_guides)} гайдов...")
    deployed = 0
    errors = 0

    for idx, g in enumerate(passed_guides):
        res = BackendClient.ingest_guide(
            guide_key=g["guide_key"],
            cat_key=g["category_key"],
            cat_title=g.get("category_title_ru") or g.get("category_name", g["category_key"]),
            title=g.get("title_ru") or g.get("raw_title", "Без названия"),
            text=g.get("text_ru") or g.get("raw_text", ""),
            photos=g.get("photos", []),
            videos=g.get("videos", []),
            sort_order=g.get("sort_order", idx)
        )

        if "error" in res:
            errors += 1
            print(f"  [{idx+1}/{len(passed_guides)}] ❌ FAIL: {g.get('title_ru')[:40]}")
        else:
            deployed += 1
            media_str = f" ({len(g.get('photos', []))}p/{len(g.get('videos', []))}v)" if g.get('photos') or g.get('videos') else ""
            print(f"  [{idx+1}/{len(passed_guides)}] ✅ OK: {g.get('title_ru')[:45]}{media_str}")

    # 4. Регистрация каналов на автопрослушку WebSocket
    if channels_data:
        print(f"\n  [+] Регистрация каналов на фоновое автообновление (WebSocket)...")
        for ch in channels_data:
            from .config import slugify
            BackendClient.register_sync_channel(
                channel_id=ch["channel_id"],
                channel_name=ch["channel_name"],
                category_key=slugify(ch["channel_name"])
            )

    print(f"\n  🎉 ВЫКАТКА НА ПРОДАКШЕН ЗАВЕРШЕНА:")
    print(f"     ✅ Успешно загружено: {deployed}")
    print(f"     ❌ Ошибок:             {errors}")

    return {"deployed": deployed, "errors": errors}
