#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 1 EXTENDED: ВАЛИДАЦИЯ guides/ по слайерпедии
1. Проверка соответствия slayerpedia <-> guides/
2. Удаление лишних/поломанных гайдов
3. Проверка полноты синхронизации RU переводов
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
OUTPUT_DIR = PROJECT_ROOT / "output_media"

# ════════════════════════════════════════════════════════
# СКАНИРОВАНИЕ slayerpedia (источник истины)
# ════════════════════════════════════════════════════════

def get_slayerpedia_structure():
    """Получает структуру slayerpedia - источник истины"""
    structure = {}
    
    for category_dir in sorted(SLAYERPEDIA_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        
        category = category_dir.name
        guide_names = set()
        
        for txt_file in category_dir.glob("*.txt"):
            guide_names.add(txt_file.stem)  # имя без расширения
        
        if guide_names:
            structure[category] = sorted(guide_names)
    
    return structure

# ════════════════════════════════════════════════════════
# АНАЛИЗ guides/ 
# ════════════════════════════════════════════════════════

def get_guides_structure(lang):
    """Получает структуру guides/{lang}/"""
    en_dir = GUIDES_DIR / lang
    structure = {}
    
    if not en_dir.exists():
        return structure
    
    for category_dir in sorted(en_dir.iterdir()):
        if not category_dir.is_dir():
            continue
        
        category = category_dir.name
        guide_names = set()
        
        for md_file in category_dir.glob("*.md"):
            # Преобразуем имя: Category_Name.md -> Category Name
            guide_name = md_file.stem.replace('_', ' ')
            guide_names.add(guide_name)
        
        if guide_names:
            structure[category] = sorted(guide_names)
    
    return structure

# ════════════════════════════════════════════════════════
# ВАЛИДАЦИЯ И СИНХРОНИЗАЦИЯ
# ════════════════════════════════════════════════════════

def validate_and_cleanup():
    """
    1. Проверяет соответствие guides <-> slayerpedia
    2. Удаляет лишние гайды
    3. Проверяет полноту RU перевода
    """
    
    print("=" * 70)
    print("PHASE 1 EXTENDED: ВАЛИДАЦИЯ guides/ ПО slayerpedia")
    print("=" * 70)
    
    # Получаем структуру слайерпедии (источник истины)
    slayerpedia_struct = get_slayerpedia_structure()
    total_slayerpedia = sum(len(v) for v in slayerpedia_struct.values())
    
    print(f"\n📚 Слайерпедия (источник истины):")
    print(f"   Категории: {len(slayerpedia_struct)}")
    print(f"   Гайдов всего: {total_slayerpedia}")
    
    # Получаем структуру guides/en и guides/ru
    guides_en = get_guides_structure("en")
    guides_ru = get_guides_structure("ru")
    
    total_en = sum(len(v) for v in guides_en.values())
    total_ru = sum(len(v) for v in guides_ru.values())
    
    print(f"\n📝 Guides EN (ДО синхронизации): {total_en} гайдов")
    print(f"📝 Guides RU (ДО синхронизации): {total_ru} гайдов")
    
    # Анализ несовпадений
    print("\n" + "=" * 70)
    print("🔍 АНАЛИЗ НЕСОВПАДЕНИЙ")
    print("=" * 70)
    
    issues = {
        "extra_en": [],      # Гайды в EN которых нет в slayerpedia
        "extra_ru": [],      # Гайды в RU которых нет в EN
        "missing_en": [],    # Гайды из slayerpedia которых нет в EN
        "missing_ru": [],    # Гайды из EN которых нет в RU (не переведены)
        "extra_categories": []  # Категории в guides которых нет в слайерпедии
    }
    
    # Проверяем каждую категорию из slayerpedia
    for category, slayer_guides in slayerpedia_struct.items():
        en_guides = set(guides_en.get(category, []))
        ru_guides = set(guides_ru.get(category, []))
        slayer_set = set(slayer_guides)
        
        # Доп гайды в EN
        extra = en_guides - slayer_set
        if extra:
            for guide in sorted(extra):
                issues["extra_en"].append(f"{category}/{guide}")
        
        # Недостающие гайды в EN
        missing = slayer_set - en_guides
        if missing:
            for guide in sorted(missing):
                issues["missing_en"].append(f"{category}/{guide}")
        
        # Недостающие гайды в RU (не переведены)
        missing_ru_for_cats = en_guides - ru_guides
        if missing_ru_for_cats:
            for guide in sorted(missing_ru_for_cats):
                issues["missing_ru"].append(f"{category}/{guide}")
    
    # Проверяем доп категории в guides
    extra_cats_en = set(guides_en.keys()) - set(slayerpedia_struct.keys())
    extra_cats_ru = set(guides_ru.keys()) - set(slayerpedia_struct.keys())
    if extra_cats_en or extra_cats_ru:
        issues["extra_categories"].extend(sorted(extra_cats_en | extra_cats_ru))
    
    # Вывод проблем
    if issues["extra_en"]:
        print(f"\n⚠️  ЛИШНИЕ гайды в guides/en/ ({len(issues['extra_en'])} шт):")
        for guide in issues["extra_en"][:10]:
            print(f"   - {guide}")
        if len(issues["extra_en"]) > 10:
            print(f"   ... и ещё {len(issues['extra_en']) - 10}")
    
    if issues["missing_en"]:
        print(f"\n⚠️  НЕДОСТАЮЩИЕ гайды в guides/en/ ({len(issues['missing_en'])} шт):")
        for guide in issues["missing_en"][:10]:
            print(f"   - {guide}")
        if len(issues["missing_en"]) > 10:
            print(f"   ... и ещё {len(issues['missing_en']) - 10}")
    
    if issues["missing_ru"]:
        print(f"\n⚠️  НЕ ПЕРЕВЕДЕНЫ на RU ({len(issues['missing_ru'])} шт):")
        for guide in issues["missing_ru"][:10]:
            print(f"   - {guide}")
        if len(issues["missing_ru"]) > 10:
            print(f"   ... и ещё {len(issues['missing_ru']) - 10}")
    
    if issues["extra_categories"]:
        print(f"\n⚠️  ЛИШНИЕ категории в guides/:")
        for cat in issues["extra_categories"]:
            print(f"   - {cat}")
    
    # Очистка лишних гайдов
    print("\n" + "=" * 70)
    print("🗑️  УДАЛЕНИЕ ЛИШНИХ ГАЙДОВ")
    print("=" * 70)
    
    deleted = []
    
    # Удаляем лишние EN гайды
    if issues["extra_en"]:
        print(f"\n✓ Удаляю {len(issues['extra_en'])} лишних гайдов из guides/en/...")
        for guide_path in issues["extra_en"]:
            category, guide_name = guide_path.split('/')
            md_file = GUIDES_DIR / "en" / category / f"{guide_name.replace(' ', '_')}.md"
            if md_file.exists():
                md_file.unlink()
                deleted.append(f"en/{guide_path}")
                print(f"  🗑️  {guide_path}")
    
    # Удаляем лишние RU гайды
    if issues["extra_ru"]:
        print(f"\n✓ Удаляю {len(issues['extra_ru'])} лишних гайдов из guides/ru/...")
        for guide_path in issues["extra_ru"]:
            category, guide_name = guide_path.split('/')
            md_file = GUIDES_DIR / "ru" / category / f"{guide_name.replace(' ', '_')}.md"
            if md_file.exists():
                md_file.unlink()
                deleted.append(f"ru/{guide_path}")
                print(f"  🗑️  {guide_path}")
    
    # Создаём пустые структуры для missing_en (чтобы пользователь знал что нужно добавить)
    if issues["missing_en"]:
        print(f"\n⚠️  ТРЕБУЕТСЯ ДОБАВИТЬ {len(issues['missing_en'])} гайдов в guides/en/:")
        for guide_path in issues["missing_en"][:5]:
            print(f"   - {guide_path}")
        if len(issues["missing_en"]) > 5:
            print(f"   ... и ещё {len(issues['missing_en']) - 5}")
    
    # ===== ПРОВЕРКА RU ПЕРЕВОДОВ =====
    print("\n" + "=" * 70)
    print("🌍 ПРОВЕРКА ПОЛНОТЫ РУССКИХ ПЕРЕВОДОВ")
    print("=" * 70)
    
    ru_status = {
        "translated": 0,
        "not_translated": [],
        "extra_ru": []
    }
    
    for category, en_guides in guides_en.items():
        ru_guides = set(guides_ru.get(category, []))
        
        for guide_name in en_guides:
            if guide_name in ru_guides:
                ru_status["translated"] += 1
            else:
                ru_status["not_translated"].append(f"{category}/{guide_name}")
    
    # Ищем RU гайды без EN
    for category, ru_guides in guides_ru.items():
        en_guides = set(guides_en.get(category, []))
        for guide_name in ru_guides:
            if guide_name not in en_guides:
                ru_status["extra_ru"].append(f"{category}/{guide_name}")
    
    print(f"\n✅ Переведено на RU: {ru_status['translated']}")
    print(f"❌ Не переведено: {len(ru_status['not_translated'])}")
    
    if ru_status["not_translated"]:
        print(f"\n   Недостающие переводы:")
        for guide in ru_status["not_translated"][:10]:
            print(f"   - {guide}")
        if len(ru_status["not_translated"]) > 10:
            print(f"   ... и ещё {len(ru_status['not_translated']) - 10}")
    
    # Итоги
    print("\n" + "=" * 70)
    print("📊 ИТОГИ ВАЛИДАЦИИ")
    print("=" * 70)
    
    print(f"\n✓ Удалено лишних гайдов: {len(deleted)}")
    print(f"✓ Соответствие слайерпедии: {len(issues['extra_en']) == 0 and len(issues['missing_en']) == 0}")
    print(f"✓ Переводы RU: {ru_status['translated']}/{sum(len(v) for v in guides_en.values())} " +
          f"({int(ru_status['translated']/sum(len(v) for v in guides_en.values())*100)}%)")
    
    if not any([issues["extra_en"], issues["missing_en"], ru_status["not_translated"]]):
        print("\n✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
    
    # Сохраняем отчёт
    report = {
        "validation_status": "PASSED" if not any([issues["extra_en"], issues["missing_en"], ru_status["not_translated"]]) else "NEEDS_ATTENTION",
        "slayerpedia_guides": total_slayerpedia,
        "guides_en": total_en,
        "guides_ru": total_ru,
        "deleted": len(deleted),
        "issues": issues,
        "ru_translation_status": ru_status
    }
    
    report_path = OUTPUT_DIR / "validation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Отчёт сохранён в output_media/validation_report.json")
    
    return report

if __name__ == "__main__":
    validate_and_cleanup()
