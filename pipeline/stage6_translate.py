"""
Этап 6: ИИ-перевод заголовков и текста гайдов (NVIDIA NIM Llama 3.3 70B / Gemini / Smart Fallback).
"""
import json
import time
from typing import Dict, List

from .config import TRANSLATED_DIR
from .translator import DynamicAITranslator


def run(guides: List[Dict]) -> List[Dict]:
    """Этап 6: каскадный перевод заголовков и текстов гайдов."""
    print("\n" + "=" * 60)
    print("  🤖 Этап 6: ИИ-перевод и локализация контента")
    print("=" * 60)

    # Кэш переводов названий категорий
    category_title_cache = {}

    for idx, g in enumerate(guides):
        cat_name = g.get("category_name", "")
        if cat_name not in category_title_cache:
            category_title_cache[cat_name] = DynamicAITranslator.translate_title(cat_name)
        g["category_title_ru"] = category_title_cache[cat_name]

        # Перевод заголовка гайда
        raw_title = g.get("raw_title", "")
        g["title_ru"] = DynamicAITranslator.translate_title(raw_title)

        # Перевод текста гайда
        raw_text = g.get("raw_text", "")
        g["text_ru"] = DynamicAITranslator.translate_text(raw_text)

        # Перенос проверенных медиа
        g["photos"] = g.get("raw_photos", [])
        g["videos"] = g.get("raw_videos", [])

        media_str = f" ({len(g['photos'])}p/{len(g['videos'])}v)" if g['photos'] or g['videos'] else ""
        print(f"  [{idx+1}/{len(guides)}] 🌐 «{g['title_ru'][:45]}»{media_str}")
        time.sleep(0.05)

    # Сохраняем результат в Gold Layer
    out_path = TRANSLATED_DIR / "translated_guides.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(guides, f, ensure_ascii=False, indent=1)

    print(f"\n  ✅ Этап 6 завершен: {len(guides)} гайдов успешно переведено")
    return guides
