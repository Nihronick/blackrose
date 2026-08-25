"""
Этап 4: Нормализация Markdown-разметки, очистка Discord-тегов и заголовков.
"""
import re
import json
from typing import Dict, List

from .config import STRUCTURED_DIR


def _normalize_discord_markdown(text: str) -> str:
    """Очистка специфичных Discord-тегов и нормализация разметки."""
    if not text:
        return ""

    # 1. Удаление подзаголовков Discord -#
    text = re.sub(r'^-#\s+', '### ', text, flags=re.MULTILINE)

    # 2. Очистка сырых упоминаний пользователей и ролей Discord
    text = re.sub(r'<@!?\d+>', '@Slayer', text)
    text = re.sub(r'<@&\d+>', '@Role', text)

    # 3. Удаление невидимых unicode-символов (Zero-width space, BOM)
    text = text.replace('\u200b', '').replace('\ufeff', '').replace('\u200e', '').replace('\u200f', '')

    # 4. Сворачивание 3+ пустых строк в максимум 2
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 5. Нормализация списков (гарантия отступа перед списком)
    text = re.sub(r'([^\n])\n(-|\*|\d+\.)\s+', r'\1\n\n\2 ', text)

    return text.strip()


def run(guides: List[Dict]) -> List[Dict]:
    """Этап 4: парсинг и нормализация текста всех гайдов."""
    print("\n" + "=" * 60)
    print("  📝 Этап 4: Парсинг и нормализация разметки Markdown")
    print("=" * 60)

    for g in guides:
        g["raw_text"] = _normalize_discord_markdown(g.get("raw_text", ""))
        # Очистка заголовка от лишних пробелов и спецсимволов
        g["raw_title"] = g.get("raw_title", "").strip().strip("# *-_`~")

    # Сохраняем результат
    out_path = STRUCTURED_DIR / "parsed_guides.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(guides, f, ensure_ascii=False, indent=1)

    print(f"  ✅ Этап 4 завершен: {len(guides)} гайдов нормализовано")
    return guides
