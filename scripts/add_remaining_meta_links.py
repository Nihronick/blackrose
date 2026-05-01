#!/usr/bin/env python3
"""
Добавить meta-links к оставшимся 5 файлам
"""

from pathlib import Path
import re

files_to_fix = {
    "event-help/event-help.md": "## Мета-ссылки\n- [[beginner_guide_path_of_suggested_progression]]\n- [[promotion_recommendation_promotion_recommendation]]",
    "shop/shop.md": "## Мета-ссылки\n- [[event_help_event_help]]\n- [[equipment_weapons]]",
    "suit-recommendation/suit-recommendation.md": "## Мета-ссылки\n- [[equipment_weapons]]\n- [[equipment_accessories]]",
    "promotion-recommendation/promotion-recommendation.md": "## Мета-ссылки\n- [[beginner_guide_path_of_suggested_progression]]\n- [[event_help_event_help]]",
}

for file_path, meta_section in files_to_fix.items():
    ru_file = Path("guides/ru") / file_path
    if ru_file.exists():
        content = ru_file.read_text(encoding='utf-8')
        
        # Удалить старую мета-секцию если есть
        content = re.sub(r'\n## Мета-ссылки\n.*?(?=\n##|$)', '', content, flags=re.DOTALL)
        
        # Добавить новую
        content = content.rstrip() + "\n" + meta_section
        
        ru_file.write_text(content, encoding='utf-8')
        print(f"✓ {file_path}")

print(f"\nУспешно добавлены meta-links к 4 файлам")
