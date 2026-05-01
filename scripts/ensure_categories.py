#!/usr/bin/env python3
"""
Initialize essential guide categories.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from database import init_db, upsert_category, get_category, close_pool
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "backend" / ".env")


CATEGORIES = [
    ("adventure", "Приключения", None, 5),
    ("beginners_guide", "Гайд для начинающих", None, 10),
    ("character", "Персонаж", None, 15),
    ("companion", "Спутник", None, 18),
    ("disclaimer", "Дисклеймер", None, 19),
    ("early_game_promotions", "Ранние промоции", None, 20),
    ("equipment", "Оборудование", None, 25),
    ("shop", "Магазин", None, 27),
    ("skills", "Навыки", None, 28),
    ("stage", "Сцена", None, 29),
    ("mid_game_promotions", "Средние промоции", None, 30),
    ("late_game_promotions", "Поздние промоции", None, 40),
    ("spirits", "Духи", None, 50),
    ("promotion_recommendation", "Рекомендация промоции", None, 60),
    ("event_help", "Помощь события", None, 70),
    ("suit_recommendation", "Рекомендация костюма", None, 80),
    ("slayer_playbook", "Слайерская тактика", None, 90),
    ("misc", "Разное", None, 100),
]


def namespaced_categories() -> list[tuple[str, str, str | None, int]]:
    ru_categories: list[tuple[str, str, str | None, int]] = []
    for key, title, icon_url, sort_order in CATEGORIES:
        ru_categories.append((f"ru_{key}", title, icon_url, sort_order))
    return CATEGORIES + ru_categories


async def ensure_categories():
    """Ensure all essential categories exist in DB."""
    await init_db()
    
    created = 0
    skipped = 0
    
    for key, title, icon_url, sort_order in namespaced_categories():
        existing = await get_category(key)
        if existing:
            print(f"[SKIP] Category already exists: {key}")
            skipped += 1
            continue
        
        await upsert_category(key, title, icon_url, sort_order)
        print(f"[CREATE] Category: {key} ({title})")
        created += 1
    
    await close_pool()
    
    print(f"\n[SUMMARY] Created: {created}, Skipped: {skipped}")


if __name__ == "__main__":
    asyncio.run(ensure_categories())
