#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ФАЗА 1 (v2): 
1. Парсит slayerpedia/ (эталон, readonly) для извлечения всех медиа-ссылок
2. Проверяет полноту guides/ (все ли гайды есть)
3. Создаёт media_manifest.json со всеми найденными медиа
4. Готовит glossary.json
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict

# Кодировка для Windows
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent
SLAYERPEDIA_DIR = PROJECT_ROOT / "slayerpedia"  # Эталонный источник (readonly)
GUIDES_DIR = PROJECT_ROOT / "guides"             # Цель синхронизации
OUTPUT_DIR = PROJECT_ROOT / "output_media"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ════════════════════════════════════════════════════════
# GLOSSARY: 100 no-translate терминов
# ════════════════════════════════════════════════════════

GLOSSARY_DATA = {
    "no_translate_skills": [
        "Agile", "Blizzard", "BurningSword", "CurvedBlade", "DancingWaves",
        "DemonHunt", "EarthsWill", "FireBlast", "FireSword", "FlameSlash",
        "FlameWave", "FlowingBlade", "Fulgurous", "GigaImpact", "GigaStrike",
        "GroundsBlessing", "HellfireSlash", "HotBlast", "IceShower", "IceTime",
        "IronWill", "LifeMana", "LightningStroke", "LightningBody", "ManasBlessing",
        "Mantra", "Meditation", "PillarOfFire", "PowerImpact", "PowerStrike",
        "Rage", "Rave", "RedLightning", "SpeedSword", "StrongCurrent",
        "Supersonic", "ThunderboltSlash", "ThunderSlash", "WarriorBurn", 
        "WaterSlash", "WindSword", "WrathOfGods", "FireSlash", "IceStone", 
        "LightningSlash"
    ],
    "no_translate_spirits": [
        "Abyss", "Adhara", "Alrescha", "Altar", "Altair", "Andromeda", "Antares",
        "Apex", "Apollo", "Aquarius", "Archer", "Arcturus", "Aries", "Artemis",
        "Ascella", "Ashtar", "Assim", "Athena", "Atlas", "Atria", "Aurora",
        "Auva", "Avior", "Azimech", "Azoth", "Azar", "Baden", "Badger", "Bailey",
        "Bailiff", "Baine", "Bakab", "Baldor", "Baldwin", "Balder", "Baldric",
        "Balfor", "Bali", "Balios", "Balir", "Balista", "Balistr", "Balithon",
        "Balken", "Balker", "Ball", "Ballad", "Ballade", "Ballah", "Ballance",
        "Ballard", "Ballast", "Ballen", "Baller", "Ballet", "Ballew", "Ballfield",
        "Ballford", "Ballhart", "Balliett", "Ballington", "Ballinger", "Ballion",
        "Ballista", "Ballius", "Ballivant", "Balloch", "Balloon", "Ballot"
    ],
    "no_translate_promotions": [
        "Stone", "Iron", "Bronze", "Silver", "Gold", "Orichalcum", "Mithril",
        "Ether", "Arcanite", "Adamant", "Black Mythril", "Blue Abyss", "Cyclos",
        "Dark Nox", "Demon Metal", "Dragonos", "Infinaut", "Ragnablood", "Warfrost",
        "Blitz Gold", "Diadust", "Eisenhart", "Eldenwood", "Gigarock"
    ],
    "no_translate_classes": [
        "Warrior", "Mage", "Archer", "Rogue", "Paladin", "Druid", "Ranger", "Knight"
    ],
    "no_translate_game_terms": [
        "BlackRose", "Slayer", "Slayerpedia", "Neon", "PostgreSQL", "Github", "Discord"
    ]
}

def create_glossary():
    """Создаёт glossary.json из GLOSSARY_DATA"""
    glossary = {
        "version": "1.0",
        "created_at": "2025-03-17",
        "total_items": 0,
        "categories": GLOSSARY_DATA
    }
    glossary["total_items"] = sum(len(v) for v in glossary["categories"].values())
    
    glossary_path = OUTPUT_DIR / "glossary.json"
    with open(glossary_path, "w", encoding="utf-8") as f:
        json.dump(glossary, f, ensure_ascii=False, indent=2)
    
    print(f"✓ glossary.json создан ({glossary['total_items']} терминов)")
    return glossary_path

# ════════════════════════════════════════════════════════
# ИЗВЛЕЧЕНИЕ МЕДИА-ССЫЛОК
# ════════════════════════════════════════════════════════

def extract_discord_media(content: str) -> List[Dict]:
    """
    Извлекает Discord CDN медиа-ссылки с параметрами и без
    https://cdn.discordapp.com/attachments/...?ex=...&is=...&hm=...
    """
    media = []
    order = 1
    
    # Паттерн: Discord CDN/Media с query параметрами
    # Захватывает: https://cdn.discordapp.com/attachments/ID/ID/file?param=val&...
    discord_pattern = r'https?://(?:cdn|media)\.discord(?:app)?\.(?:com|net)/(?:attachments|ephemeral-attachments)/[\d/]*/[^"\'\s<>]*[?&]*[^"\'\s<>]*'
    
    for match in re.finditer(discord_pattern, content):
        url = match.group(0).rstrip('&')  # Remove trailing & if any
        
        # Тип медиа по расширению
        media_type = "video" if any(x in url.lower() for x in [".mp4", ".webm", ".mov", ".m4v"]) else "image"
        
        # Контекст (150 символов до и после)
        start = max(0, match.start() - 150)
        end = min(len(content), match.end() + 150)
        context = content[start:end].replace('\n', ' ').strip()
        
        media.append({
            "order": order,
            "original_url": url,
            "type": media_type,
            "context": context
        })
        order += 1
    
    return media


def generate_filename(url: str, guide_name: str, order: int) -> str:
    """Генерирует стандартизированное имя файла"""
    # Извлекаем расширение из URL (до ? параметров)
    base_url = url.split('?')[0]
    ext = Path(base_url).suffix or ".bin"
    
    # Очищаем имя гайда
    safe_name = re.sub(r'[^\w\s-]', '', guide_name).replace(' ', '_')[:30]
    
    return f"{safe_name}_{order:03d}{ext}"

# ════════════════════════════════════════════════════════
# СКАНИРОВАНИЕ slayerpedia (ЭТАЛОН)
# ════════════════════════════════════════════════════════

def scan_slayerpedia_media() -> Dict:
    """Сканирует slayerpedia/ и извлекает все медиа-ссылки"""
    media_by_category = defaultdict(list)
    total_media = 0
    
    print("\n📂 Сканирование slayerpedia/ (эталонный источник)...")
    
    for category_dir in sorted(SLAYERPEDIA_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        
        category = category_dir.name
        txt_files = list(category_dir.glob("*.txt"))
        
        if not txt_files:
            continue
        
        print(f"\n  📁 {category}/ ({len(txt_files)} файлов)")
        
        for txt_file in sorted(txt_files):
            try:
                content = txt_file.read_text(encoding="utf-8")
                media_links = extract_discord_media(content)
                
                if media_links:
                    guide_name = txt_file.stem
                    for media in media_links:
                        media['guide_name'] = guide_name
                        media['category'] = category
                        media['filename'] = generate_filename(
                            media['original_url'], 
                            guide_name, 
                            media['order']
                        )
                        media_by_category[category].append(media)
                        total_media += 1
                    
                    print(f"    ✓ {guide_name}.txt: {len(media_links)} медиа")
            
            except Exception as e:
                print(f"    ✗ Ошибка чтения {txt_file.name}: {e}")
    
    print(f"\n✓ Всего найдено медиа в slayerpedia/: {total_media}")
    return dict(media_by_category)

# ════════════════════════════════════════════════════════
# ПРОВЕРКА ПОЛНОТЫ guides/
# ════════════════════════════════════════════════════════

def check_guides_completeness(slayerpedia_media: Dict) -> Dict:
    """Проверяет, полноты guides/ по сравнению со slayerpedia/"""
    
    print("\n📊 Проверка полноты guides/...")
    
    completeness = {
        "total_slayerpedia_guides": 0,
        "total_guides_files": 0,
        "missing_guides": [],
        "guides_with_media": {},
        "guides_without_media": {}
    }
    
    # Подсчитываем гайды в slayerpedia
    slayerpedia_guides = set()
    for category, media_list in slayerpedia_media.items():
        for media in media_list:
            slayerpedia_guides.add((category, media['guide_name']))
    
    completeness["total_slayerpedia_guides"] = len(slayerpedia_guides)
    
    # Проверяем guides/en и guides/ru
    if GUIDES_DIR.exists():
        en_dir = GUIDES_DIR / "en"
        ru_dir = GUIDES_DIR / "ru"
        
        for lang_dir in [en_dir, ru_dir]:
            if not lang_dir.exists():
                print(f"  ⚠ {lang_dir.name}/ не найден")
                continue
            
            lang = lang_dir.name
            md_files = list(lang_dir.rglob("*.md"))
            completeness["total_guides_files"] += len(md_files)
            
            print(f"\n  📝 {lang}/ ({len(md_files)} markdown файлов):")
            
            for md_file in sorted(md_files)[:5]:  # Показываем первые 5
                print(f"    - {md_file.relative_to(GUIDES_DIR)}")
    
    return completeness

# ════════════════════════════════════════════════════════
# ГЛАВНАЯ ФУНКЦИЯ
# ════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("ФАЗА 1: АНАЛИЗ slayerpedia + ПРОВЕРКА guides + МЕДИА-МАНИФЕСТ")
    print("=" * 60)
    
    # Шаг 1: Создаём glossary.json
    create_glossary()
    
    # Шаг 2: Сканируем slayerpedia и извлекаем все медиа
    slayerpedia_media = scan_slayerpedia_media()
    
    # Шаг 3: Проверяем полноту guides/
    completeness = check_guides_completeness(slayerpedia_media)
    
    # Шаг 4: Создаём media_manifest.json
    manifest = {
        "version": "1.0",
        "created_at": "2025-03-17",
        "source": "slayerpedia/",
        "source_readonly": True,
        "target": "guides/",
        "total_media": sum(len(v) for v in slayerpedia_media.values()),
        "by_category": slayerpedia_media,
        "completeness": completeness
    }
    
    manifest_path = OUTPUT_DIR / "media_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"✓ media_manifest.json создан ({manifest['total_media']} медиа-ссылок)")
    print(f"✓ Файлы сохранены в output_media/")
    print("=" * 60)
    
    # Вывод summary
    print("\n📊 ИТОГИ PHASE 1:")
    print(f"  • Медиа найдено: {manifest['total_media']}")
    print(f"  • Категорий: {len(slayerpedia_media)}")
    print(f"  • Гайдов в slayerpedia: {completeness['total_slayerpedia_guides']}")
    print(f"  • Markdown файлов в guides: {completeness['total_guides_files']}")

if __name__ == "__main__":
    main()
