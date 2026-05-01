#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 1 RU SYNC: Синхронизация guides/ru со структурой guides/en
Копирует EN файлы в RU как базу для перевода
"""

import os
import sys
from pathlib import Path

# Кодировка
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent
GUIDES_DIR = PROJECT_ROOT / "guides"

def sync_ru_guides():
    """Синхронизирует guides/ru структурой guides/en"""
    
    print("=" * 80)
    print("PHASE 1 RU SYNC: СИНХРОНИЗАЦИЯ guides/ru СО СТРУКТУРОЙ guides/en")
    print("=" * 80)
    
    en_dir = GUIDES_DIR / "en"
    ru_dir = GUIDES_DIR / "ru"
    
    if not en_dir.exists():
        print("✗ guides/en/ не найда")
        return
    
    copied = 0
    updated = 0
    skipped = 0
    
    # Итерируем по категориям EN
    for category_dir in sorted(en_dir.iterdir()):
        if not category_dir.is_dir():
            continue
        
        category = category_dir.name
        
        # Создаём директорию в RU
        ru_cat_dir = ru_dir / category
        ru_cat_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📁 {category}/")
        
        # Итерируем по файлам
        for md_file in sorted(category_dir.glob("*.md")):
            ru_file = ru_cat_dir / md_file.name
            
            # Если файл уже есть в RU, пропускаем
            if ru_file.exists():
                # Проверяем размер - если маленький, возможно это заголовок [ТРЕБУЕТСЯ ПЕРЕВОД]
                content = ru_file.read_text(encoding='utf-8')
                if content.startswith('[ТРЕБУЕТСЯ ПЕРЕВОД]') or len(content) < 100:
                    # Компиируем новый контент
                    en_content = md_file.read_text(encoding='utf-8')
                    ru_file.write_text(en_content, encoding='utf-8')
                    print(f"  🔄 {md_file.name}")
                    updated += 1
                else:
                    # Уже переведено, пропускаем
                    print(f"  ✓ {md_file.name} (уже существует)")
                    skipped += 1
            else:
                # Копируем EN в RU
                en_content = md_file.read_text(encoding='utf-8')
                ru_file.write_text(en_content, encoding='utf-8')
                print(f"  ✓ {md_file.name}")
                copied += 1
    
    # Итоги
    print("\n" + "=" * 80)
    print("✅ ИТОГИ СИНХРОНИЗАЦИИ RU")
    print("=" * 80)
    
    total = copied + updated + skipped
    print(f"\nВсего файлов: {total}")
    print(f"✓ Скопировано: {copied}")
    print(f"🔄 Обновлено: {updated}")
    print(f"⚪ Пропущено: {skipped}")
    
    print(f"\n✓ Структура guides/ru синхронизирована со guides/en")
    print(f"\nСЛЕДУЮЩЩЙ ШАГ:")
    print(f"  1. Проверить guides/ru/ содержит все файлы")
    print(f"  2. Выполнить перевод контента на русский язык")
    print(f"  3. Phase 2: Скачивание и обработка медиа")

if __name__ == "__main__":
    sync_ru_guides()
