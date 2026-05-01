#!/usr/bin/env python3
"""
ФАЗА 1: Анализ icons.py + Сканирование гайдов + Экстракция медиа
Создание glossary.json + media_manifest.json
"""

import json
import re
import sys
import os
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime

# Fix encoding for Windows
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent
GUIDES_DIR = PROJECT_ROOT / "guides"
OUTPUT_DIR = PROJECT_ROOT / "output_media"
OUTPUT_DIR.mkdir(exist_ok=True)

# ════════════════════════════════════════════════════════
# ЭТАП 0-1: АНАЛИЗ icons.py И СОЗДАНИЕ GLOSSARY
# ════════════════════════════════════════════════════════

def create_glossary():
    """Создаёт glossary.json из icons.py"""
    
    no_translate = [
        # SKILLS
        "Agile", "Blizzard", "BurningSword", "CurvedBlade", "DancingWaves",
        "DemonHunt", "EarthsWill", "FireBlast", "FireSword", "FlameSlash",
        "FlameWave", "FlowingBlade", "Fulgurous", "GigaImpact", "GigaStrike",
        "GroundsBlessing", "HellfireSlash", "HotBlast", "IceShower", "IceTime",
        "IronWill", "LifeMana", "LightningStroke", "LightningBody", "ManasBlessing",
        "Mantra", "Meditation", "PillarOfFire", "PowerImpact", "PowerStrike",
        "Rage", "Rave", "RedLightning", "SpeedSword", "StrongCurrent",
        "Supersonic", "ThunderboltSlash", "ThunderSlash", "WarriorBurn", "WaterSlash",
        "WindSword", "WrathOfGods", "FireSlash", "IceStone", "LightningSlash",
        # SPIRITS
        "noah", "loar", "sala", "mum", "bo", "radon", "zappy", "kart",
        "herh", "todd", "luga", "ark", "hi", "je", "ku", "a", "leon",
        "mus", "na", "pe", "po", "ru", "sha", "ti",
        # PROMOTIONS
        "adamant", "ether", "black_mithril", "demonite", "dragonos", "blood",
        "frost", "nox", "abyss", "infinat", "cyclone", "ancient", "gigalor",
        "arcanite", "stone", "silver", "orichalcum", "gold", "iron", "bronze",
        "diadust", "eisenhart", "Eldenwood", "mithrill",
        # CLASSES
        "Tera", "Nova", "Seed", "C17", "C18", "C19", "C20"
    ]
    
    glossary = {
        "version": "1.0",
        "generated": datetime.now().isoformat(),
        "no_translate": sorted(no_translate),
        "no_translate_count": len(no_translate)
    }
    
    return glossary


# ════════════════════════════════════════════════════════
# ЭТАП 2: ЭКСТРАКЦИЯ ВСЕХ МЕДИА-ССЫЛОК
# ════════════════════════════════════════════════════════

def extract_media_links(content: str) -> List[Dict]:
    """Извлекает ТОЛЬКО Discord CDN медиа-ссылки (с параметрами и без)"""
    media = []
    order = 1
    
    # Discord attachments с параметрами и без
    # https://cdn.discordapp.com/attachments/... или ...?ex=...&is=...&hm=...
    # https://media.discordapp.net/attachments/...
    discord_pattern = r'https?://(?:cdn|media)\.discord(?:app)?\.(?:com|net)/(?:attachments|ephemeral-attachments)/[\d/]+/[^"\'\s<>]+(?:[?&][^"\'\s<>]*)*'
    
    for match in re.finditer(discord_pattern, content):
        url = match.group(0)
        
        # Определяем тип по расширению
        media_type = "video" if any(x in url.lower() for x in [".mp4", ".webm", ".mov", ".m4v"]) else "image"
        
        # 2-3 строки контекста
        start = max(0, match.start() - 150)
        end = min(len(content), match.end() + 150)
        context = content[start:end].replace('\n', ' ')[:200].strip()
        
        media.append({
            "original_url": url,
            "type": media_type,
            "order": order,
            "context": context
        })
        order += 1
    
    return media


def generate_filename(url: str, guide_name: str, order: int) -> str:
    """Генерирует имя файла из URL"""
    # Получаем расширение
    ext = "mp4" if any(x in url.lower() for x in [".mp4", "video"]) else "png"
    if ".jpg" in url.lower() or "jpg" in url.lower():
        ext = "jpg"
    elif ".webp" in url.lower():
        ext = "webp"
    elif ".gif" in url.lower():
        ext = "gif"
    elif ".webm" in url.lower():
        ext = "webm"
    
    clean_name = re.sub(r'[^\w\-]+', '_', guide_name)[:50]
    return f"{clean_name}_{order}.{ext}"


# ════════════════════════════════════════════════════════
# СКАНИРОВАНИЕ ГАЙДОВ
# ════════════════════════════════════════════════════════

def scan_guides_and_media() -> tuple:
    """Сканирует все гайды и возвращает список с медиа"""
    
    guides_media = []
    all_media = []
    media_id = 1
    
    for lang in ["en", "ru"]:
        lang_dir = GUIDES_DIR / lang
        if not lang_dir.exists():
            continue
        
        for category_dir in sorted(lang_dir.iterdir()):
            if not category_dir.is_dir():
                continue
            
            for md_file in sorted(category_dir.glob("*.md")):
                try:
                    content = md_file.read_text(encoding='utf-8')
                    
                    media_in_guide = extract_media_links(content)
                    
                    guide_entry = {
                        "lang": lang,
                        "category": category_dir.name,
                        "guide_name": md_file.stem,
                        "file_path": str(md_file.relative_to(PROJECT_ROOT)),
                        "media_count": len(media_in_guide),
                        "media": media_in_guide
                    }
                    
                    guides_media.append(guide_entry)
                    
                    # Добавляем в глобальный список
                    for m in media_in_guide:
                        m["media_id"] = media_id
                        m["found_in_guide"] = md_file.stem
                        m["found_in_category"] = category_dir.name
                        m["found_in_lang"] = lang
                        m["filename"] = generate_filename(m["original_url"], md_file.stem, m["order"])
                        all_media.append(m)
                        media_id += 1
                    
                    print(f"✓ {lang}/{category_dir.name}/{md_file.stem} - {len(media_in_guide)} медиа")
                    
                except Exception as e:
                    print(f"⚠ Ошибка {md_file}: {str(e)[:50]}")
    
    return guides_media, all_media


# ════════════════════════════════════════════════════════
# ГЛАВНАЯ ФУНКЦИЯ
# ════════════════════════════════════════════════════════

def main():
    print("\n" + "="*70)
    print(" 🔹 ФАЗА 1: АНАЛИЗ + ЭКСТРАКЦИЯ МЕДИА")
    print("="*70 + "\n")
    
    # ЭТАП 0-1: Glossary
    print("📋 Создание glossary.json...")
    glossary = create_glossary()
    glossary_file = OUTPUT_DIR / "glossary.json"
    glossary_file.write_text(json.dumps(glossary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"✓ {glossary_file} ({len(glossary['no_translate'])} no-translate слов)\n")
    
    # ЭТАП 2: Сканирование медиа
    print("🎬 Сканирование гайдов и экстракция медиа...")
    guides_media, all_media = scan_guides_and_media()
    
    print(f"\n✓ Гайдов: {len(guides_media)}")
    print(f"✓ Всего медиа найдено: {len(all_media)}")
    
    # Статистика
    video_count = len([m for m in all_media if m['type'] == 'video'])
    image_count = len([m for m in all_media if m['type'] == 'image'])
    
    print(f"  - Видео: {video_count}")
    print(f"  - Изображений: {image_count}")
    
    # Сохраняем media_manifest.json
    manifest = {
        "version": "1.0",
        "generated": datetime.now().isoformat(),
        "total_media": len(all_media),
        "by_type": {
            "video": video_count,
            "image": image_count
        },
        "media": all_media
    }
    
    manifest_file = OUTPUT_DIR / "media_manifest.json"
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n✓ {manifest_file} ({len(all_media)} ссылок)\n")
    
    # Краткая статистика по гайдам
    print("📊 Топ гайдов по количеству медиа:")
    top_guides = sorted(guides_media, key=lambda x: x['media_count'], reverse=True)[:10]
    for i, g in enumerate(top_guides, 1):
        print(f"  {i}. {g['guide_name']:.<40} {g['media_count']} медиа")
    
    print("\n" + "="*70)
    print(" ✅ ФАЗА 1 ЗАВЕРШЕНА")
    print("="*70)
    print(f"""
📁 Созданные файлы:
   • glossary.json ({len(glossary['no_translate'])} no-translate слов)
   • media_manifest.json ({len(all_media)} медиа-ссылок)

📊 Итоговая статистика:
   • Гайдов: {len(guides_media)}
   • Медиа: {len(all_media)} ({video_count} видео + {image_count} фото)
   • Средний размер контекста: ~200 символов

⏸️  СТОП ДЛЯ ПОДТВЕРЖДЕНИЯ!

Следующий шаг (ФАЗА 2):
1. Проверь структуру media_manifest.json
2. Покажи примеры первых 5 медиа-ссылок
3. Подтверди перед началом:
   ✓ Скачивание медиа
   ✓ Сжатие видео (FFmpeg)
   ✓ Загрузка на GitHub
""")


if __name__ == "__main__":
    main()
