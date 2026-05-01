#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 1 CLEANUP v2: 
1. Удаляет ВСЕ лишние гайды (которых нет в slayerpedia)
2. Удаляет целые лишние категории
3. Удаляет категорию new_from_discord (нет в slayerpedia)
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict
import shutil

# Кодировка для Windows
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent
SLAYERPEDIA_DIR = PROJECT_ROOT / "slayerpedia"
GUIDES_DIR = PROJECT_ROOT / "guides"

# ════════════════════════════════════════════════════════
# ПОЛУЧЕНИЕ СТРУКТУР
# ════════════════════════════════════════════════════════

def get_slayerpedia_structure():
    """Структура slayerpedia - источник истины"""
    structure = {}
    
    for category_dir in sorted(SLAYERPEDIA_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        
        category = category_dir.name
        guide_names = set()
        
        for txt_file in category_dir.glob("*.txt"):
            guide_names.add(txt_file.stem)
        
        if guide_names:
            structure[category] = sorted(guide_names)
    
    return structure

def get_guides_files(lang):
    """Получает ВСЕ файлы из guides/{lang} с полными путями"""
    lang_dir = GUIDES_DIR / lang
    files_dict = defaultdict(list)
    
    if not lang_dir.exists():
        return files_dict
    
    for category_dir in lang_dir.iterdir():
        if not category_dir.is_dir():
            continue
        
        category = category_dir.name
        
        for md_file in category_dir.glob("*.md"):
            files_dict[category].append({
                "name": md_file.stem,
                "path": md_file,
                "display_name": md_file.stem.replace('_', ' ')
            })
    
    return dict(files_dict)

# ════════════════════════════════════════════════════════
# ОЧИСТКА 
# ════════════════════════════════════════════════════════

def cleanup_guides():
    """Удаляет ВСЕ lишние гайды и категории"""
    
    print("=" * 70)
    print("PHASE 1 CLEANUP v2: УДАЛЕНИЕ ЛИШНИХ ГАЙДОВ И КАТЕГОРИЙ")
    print("=" * 70)
    
    slayerpedia = get_slayerpedia_structure()
    valid_categories = set(slayerpedia.keys())
    
    print(f"\n📚 Валидные категории из slayerpedia ({len(valid_categories)}):")
    for cat in sorted(valid_categories):
        print(f"   ✓ {cat}")
    
    # ===== ОЧИСТКА EN =====
    print("\n" + "=" * 70)
    print("🗑️  ОЧИСТКА guides/en/")
    print("=" * 70)
    
    guides_en = get_guides_files("en")
    deleted_en = []
    
    for category in list(guides_en.keys()):
        if category not in valid_categories:
            # Удаляем целую категорию
            category_path = GUIDES_DIR / "en" / category
            print(f"\n🗑️  Удаляю категорию: en/{category}/")
            shutil.rmtree(category_path)
            
            for guide in guides_en[category]:
                deleted_en.append(f"en/{category}/{guide['display_name']}")
                print(f"   - {guide['display_name']}")
        
        else:
            # Проверяем гайды в категории
            valid_guides = set(slayerpedia[category])
            
            for guide in guides_en[category]:
                guide_name = guide['display_name']
                if guide_name not in valid_guides:
                    # Удаляем лишний гайд
                    print(f"🗑️  Удаляю гайд: en/{category}/{guide_name}")
                    guide['path'].unlink()
                    deleted_en.append(f"en/{category}/{guide_name}")
    
    # ===== ОЧИСТКА RU =====
    print("\n" + "=" * 70)
    print("🗑️  ОЧИСТКА guides/ru/")
    print("=" * 70)
    
    guides_ru = get_guides_files("ru")
    deleted_ru = []
    
    for category in list(guides_ru.keys()):
        if category not in valid_categories:
            # Удаляем целую категорию
            category_path = GUIDES_DIR / "ru" / category
            print(f"\n🗑️  Удаляю категорию: ru/{category}/")
            if category_path.exists():
                shutil.rmtree(category_path)
            
            for guide in guides_ru[category]:
                deleted_ru.append(f"ru/{category}/{guide['display_name']}")
                print(f"   - {guide['display_name']}")
        
        else:
            # Проверяем гайды в категории
            valid_guides = set(slayerpedia[category])
            
            for guide in guides_ru[category]:
                guide_name = guide['display_name']
                if guide_name not in valid_guides:
                    # Удаляем лишний гайд
                    print(f"🗑️  Удаляю гайд: ru/{category}/{guide_name}")
                    guide['path'].unlink()
                    deleted_ru.append(f"ru/{category}/{guide_name}")
    
    # ===== ФИНАЛЬНАЯ ПРОВЕРКА =====
    print("\n" + "=" * 70)
    print("✅ ПРОВЕРКА ПОСЛЕ ОЧИСТКИ")
    print("=" * 70)
    
    # Пересканируем
    new_guides_en = get_guides_files("en")
    new_guides_ru = get_guides_files("ru")
    
    total_en = sum(len(v) for v in new_guides_en.values())
    total_ru = sum(len(v) for v in new_guides_ru.values())
    
    print(f"\nGuides EN: {total_en} гайдов ({len(new_guides_en)} категорий)")
    print(f"Guides RU: {total_ru} гайдов ({len(new_guides_ru)} категорий)")
    print(f"\nУдалено EN: {len(deleted_en)}")
    print(f"Удалено RU: {len(deleted_ru)}")
    
    # Проверка на несовпадения en vs slayerpedia
    print("\n" + "=" * 70)
    print("🔍 ПРОВЕРКА СООТВЕТСТВИЯ guides/en <-> slayerpedia")
    print("=" * 70)
    
    mismatches = []
    for category in new_guides_en:
        en_guides = set(g['display_name'] for g in new_guides_en[category])
        slayer_guides = set(slayerpedia.get(category, []))
        
        if en_guides != slayer_guides:
            missing = slayer_guides - en_guides
            extra = en_guides - slayer_guides
            
            if missing:
                for guide in sorted(missing):
                    mismatches.append(f"  ❌ MISSING: {category}/{guide}")
            if extra:
                for guide in sorted(extra):
                    mismatches.append(f"  ⚠️  EXTRA: {category}/{guide}")
    
    if mismatches:
        print("\n⚠️  Обнаружены несовпадения:")
        for msg in mismatches[:15]:
            print(msg)
        if len(mismatches) > 15:
            print(f"  ... и ещё {len(mismatches) - 15}")
    else:
        print("\n✅ Полное соответствие guides/en <-> slayerpedia!")
    
    # Проверка переводов RU
    print("\n" + "=" * 70)
    print("🌍 ПРОВЕРКА СТАТУСА ПЕРЕВОДОВ RU")
    print("=" * 70)
    
    translated = 0
    not_translated = []
    
    for category in new_guides_en:
        en_guides = set(g['display_name'] for g in new_guides_en[category])
        ru_guides = set(g['display_name'] for g in new_guides_ru.get(category, []))
        
        for guide in sorted(en_guides):
            if guide in ru_guides:
                translated += 1
            else:
                not_translated.append(f"{category}/{guide}")
    
    total = sum(len(v) for v in new_guides_en.values())
    pct = int(translated / total * 100) if total > 0 else 0
    
    print(f"\n✅ Переведено: {translated}/{total} ({pct}%)")
    
    if not_translated:
        print(f"\n❌ Не переведено ({len(not_translated)}):")
        for guide in not_translated[:10]:
            print(f"   - {guide}")
        if len(not_translated) > 10:
            print(f"   ... и ещё {len(not_translated) - 10}")
    
    # Сохраняем отчёт о очистке
    report = {
        "action": "CLEANUP",
        "deleted_en": len(deleted_en),
        "deleted_ru": len(deleted_ru),
        "files_deleted": sorted(deleted_en + deleted_ru),
        "final_state": {
            "guides_en": total_en,
            "guides_ru": total_ru,
            "categories_en": len(new_guides_en),
            "categories_ru": len(new_guides_ru)
        },
        "validation": {
            "matches_slayerpedia": len(mismatches) == 0,
            "mismatches": mismatches,
            "ru_translation_percent": pct,
            "ru_not_translated": not_translated
        }
    }
    
    output_path = PROJECT_ROOT / "output_media" / "cleanup_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Отчёт сохранён: output_media/cleanup_report.json")
    
    return report

if __name__ == "__main__":
    cleanup_guides()
