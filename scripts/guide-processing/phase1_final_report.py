#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 1 FINAL REPORT: Подготовка к Phase 2
Синхронизация guides/ с slayerpedia
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict

# Кодировка
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent
SLAYERPEDIA_DIR = PROJECT_ROOT / "slayerpedia"
GUIDES_DIR = PROJECT_ROOT / "guides"
OUTPUT_DIR = PROJECT_ROOT / "output_media"

def get_all_guides():
    """Получает полный список гайдов"""
    slayer_guides = {}
    guides_en = {}
    guides_ru = {}
    
    # Slayerpedia
    for cat_dir in SLAYERPEDIA_DIR.iterdir():
        if not cat_dir.is_dir():
            continue
        category = cat_dir.name
        guides = {f.stem for f in cat_dir.glob("*.txt")}
        if guides:
            slayer_guides[category] = sorted(guides)
    
    # Guides EN
    en_dir = GUIDES_DIR / "en"
    if en_dir.exists():
        for cat_dir in en_dir.iterdir():
            if not cat_dir.is_dir():
                continue
            category = cat_dir.name
            guides = {f.stem.replace('_', ' ') for f in cat_dir.glob("*.md")}
            if guides:
                guides_en[category] = sorted(guides)
    
    # Guides RU
    ru_dir = GUIDES_DIR / "ru"
    if ru_dir.exists():
        for cat_dir in ru_dir.iterdir():
            if not cat_dir.is_dir():
                continue
            category = cat_dir.name
            guides = {f.stem.replace('_', ' ') for f in cat_dir.glob("*.md")}
            if guides:
                guides_ru[category] = sorted(guides)
    
    return slayer_guides, guides_en, guides_ru

def main():
    print("=" * 80)
    print("PHASE 1 FINAL: СТАТУС СИНХРОНИЗАЦИИ guides/ <-> slayerpedia")
    print("=" * 80)
    
    slayer, en, ru = get_all_guides()
    
    # Статистика
    total_slayer = sum(len(v) for v in slayer.values())
    total_en = sum(len(v) for v in en.values())
    total_ru = sum(len(v) for v in ru.values())
    
    print(f"\n📊 СТАТИСТИКА:")
    print(f"  Slayerpedia: {total_slayer} гайдов в {len(slayer)} категориях")
    print(f"  Guides EN:   {total_en} гайдов в {len(en)} категориях")
    print(f"  Guides RU:   {total_ru} гайдов в {len(ru)} категориях")
    
    # Анализ расхождений
    print(f"\n" + "=" * 80)
    print("🔍 АНАЛИЗ РАСХОЖДЕНИЙ")
    print("=" * 80)
    
    issues = {
        "missing_in_en": [],
        "extra_in_en": [],
        "missing_in_ru": [],
        "matching": 0
    }
    
    for category in sorted(set(list(slayer.keys()) + list(en.keys()))):
        slayer_guides = set(slayer.get(category, []))
        en_guides = set(en.get(category, []))
        ru_guides = set(ru.get(category, []))
        
        # Недостающие в EN
        missing = slayer_guides - en_guides
        if missing:
            for guide in sorted(missing):
                issues["missing_in_en"].append(f"{category}/{guide}")
        
        # Лишние в EN
        extra = en_guides - slayer_guides
        if extra:
            for guide in sorted(extra):
                issues["extra_in_en"].append(f"{category}/{guide}")
        
        # Недостающие в RU
        for guide in sorted(en_guides):
            if guide not in ru_guides:
                issues["missing_in_ru"].append(f"{category}/{guide}")
            else:
                issues["matching"] += 1
    
    if issues["missing_in_en"]:
        print(f"\n❌ НЕДОСТАЮЩИЕ в guides/en/ ({len(issues['missing_in_en'])} шт):")
        for guide in issues["missing_in_en"]:
            print(f"   - {guide}")
    else:
        print(f"\n✅ Guides EN полностью синхронизирована со slayerpedia")
    
    if issues["extra_in_en"]:
        print(f"\n⚠️  ЛИШНИЕ в guides/en/ ({len(issues['extra_in_en'])} шт):")
        for guide in issues["extra_in_en"]:
            print(f"   - {guide}")
    
    if issues["missing_in_ru"]:
        print(f"\n⚠️  НЕ ПЕРЕВЕДЕНЫ на RU ({len(issues['missing_in_ru'])} шт):")
        for guide in issues["missing_in_ru"][:5]:
            print(f"   - {guide}")
        if len(issues["missing_in_ru"]) > 5:
            print(f"   ... и ещё {len(issues['missing_in_ru']) - 5}")
    else:
        print(f"\n✅ ВСЕ гайды переведены на RU!")
    
    # Итоговая проверка
    print(f"\n" + "=" * 80)
    print("✅ ИТОГОВЫЙ СТАТУС")
    print("=" * 80)
    
    ready_for_phase2 = len(issues["missing_in_en"]) == 0 and len(issues["extra_in_en"]) == 0
    
    status_en = '✅ ДА' if ready_for_phase2 else '❌ НЕТ'
    status_ru = '✅ ДА' if len(issues['missing_in_ru']) == 0 else f"❌ НЕТ ({len(issues['missing_in_ru'])} недостаёт)"
    status_phase2 = '✅ ДА' if ready_for_phase2 else '❌ НЕТ - нужна синхронизация'
    
    print(f"\n📋 Guides EN соответствует slayerpedia: {status_en}")
    print(f"📋 Переводы RU полные: {status_ru}")
    print(f"📋 Готово к Phase 2: {status_phase2}")
    
    # Подготовка медиа для phase 2
    print(f"\n" + "=" * 80)
    print("📦 ПОДГОТОВКА PHASE 2: СКАЧИВАНИЕ И ОБРАБОТКА МЕДИА")
    print("=" * 80)
    
    # Загружаем media_manifest
    manifest_path = OUTPUT_DIR / "media_manifest.json"
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        
        total_media = manifest.get("total_media", 0)
        by_type = defaultdict(int)
        
        for category_media in manifest["by_category"].values():
            for media in category_media:
                by_type[media["type"]] += 1
        
        print(f"\n📊 Медиа для обработки:")
        print(f"  Всего: {total_media} ссылок")
        print(f"  Видео: {by_type.get('video', 0)}")
        print(f"  Изображения: {by_type.get('image', 0)}")
        print(f"\n  Эта информация хранится в: output_media/media_manifest.json")
    
    # Сохраняем финальный отчёт
    report = {
        "phase": "1_FINAL",
        "status": "READY" if ready_for_phase2 else "NEEDS_SYNC",
        "statistics": {
            "slayerpedia_total": total_slayer,
            "guides_en_total": total_en,
            "guides_ru_total": total_ru,
            "en_matches_ru": issues["matching"]
        },
        "issues": issues,
        "next_steps": [
            "Phase 2: Скачивание медиа из Discord CDN",
            "Phase 2: FFmpeg компрессия видео (H.264, -crf 28)",
            "Phase 3: Загрузка на GitHub",
            "Phase 4: Замена Discord CDN ссылок на GitHub raw URLs",
            "Phase 5: Генерация SQL для импорта"
        ] if ready_for_phase2 else [
            "Синхронизировать недостающие гайды:",
            f"  - Добавить {len(issues['missing_in_en'])} гайдов в guides/en/",
            f"  - Перевести {len(issues['missing_in_ru'])} гайдов на RU"
        ]
    }
    
    report_path = OUTPUT_DIR / "phase1_final_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Финальный отчёт: output_media/phase1_final_report.json")
    
    return report

if __name__ == "__main__":
    main()
