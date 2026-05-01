#!/usr/bin/env python3
"""
ПОЛНЫЙ ПРОЦЕСС: Обработка гайдов BlackRose для Neon БД
Все 4 этапа с правильной UTF-8 кодировкой
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime

# ════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).parent
GUIDES_DIR = PROJECT_ROOT / "guides"
OUTPUT_DIR = PROJECT_ROOT / "output_neon"
OUTPUT_DIR.mkdir(exist_ok=True)

# Явно устанавливаем UTF-8
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8')

# ════════════════════════════════════════════════════════
# УТИЛИТЫ
# ════════════════════════════════════════════════════════

def safe_write_json(file_path: Path, data: Dict) -> bool:
    """Безопасно пишет JSON с UTF-8"""
    try:
        content = json.dumps(data, ensure_ascii=False, indent=2)
        file_path.write_text(content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"✗ Ошибка при записи {file_path}: {e}")
        return False


def escape_sql_string(s: str) -> str:
    """Экранирует строку для SQL"""
    s = s.replace("\\", "\\\\")
    s = s.replace("'", "''")
    return s


def extract_icon_refs(content: str) -> List[str]:
    """Извлекает {{icon_name}} из контента"""
    return list(set(re.findall(r'\{\{(\w+)\}\}', content)))


def extract_media_urls(content: str) -> List[str]:
    """Извлекает медиа-ссылки"""
    urls = set()
    
    # Discord CDN
    urls.update(re.findall(r'https?://(?:cdn|media)\.discord(?:app)?\.(?:com|net)/[^\s\)\"\']*', content))
    
    # Direct media
    urls.update(re.findall(r'https?://[^\s\)\"\']*\.(?:png|jpg|jpeg|gif|webp|mp4|webm|mov|mkv)', content, re.I))
    
    # Previews
    urls.update(re.findall(r'https?://(?:i\.ytimg|imgur|tenor)\.com[^\s\)\"\']*', content))
    
    return sorted(list(urls))


def md_to_text(content: str) -> str:
    """Конвертирует Markdown в plain text"""
    text = content
    text = re.sub(r'#+\s+', '', text)
    text = re.sub(r'\*\*|__|\*|_|~~', '', text)
    text = re.sub(r'`+.*?`+', '', text, flags=re.DOTALL)
    text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)
    text = re.sub(r'[-*]\s+', '• ', text)
    text = re.sub(r'<[^>]*>', '', text)
    text = re.sub(r'\n\n+', '\n', text)
    return text.strip()


# ════════════════════════════════════════════════════════
# ЭТАП 0-1: GLOSSARY
# ════════════════════════════════════════════════════════

def create_glossary() -> Dict:
    """Создаёт glossary.json"""
    
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
    
    icons_map = {key: f"icon_{key}" for key in no_translate[:50]}  # Примеры
    
    glossary = {
        "version": "1.0",
        "generated": datetime.now().isoformat(),
        "terms": {
            "skill": "навык",
            "promotion": "промоут",
            "spirit": "дух",
            "companion": "спутник",
            "class": "класс"
        },
        "abbreviations": {
            "DH": "Демонхант (DH)",
            "WB": "Боевой урон (WB)",
            "LB": "Грозовое тело (LB)",
            "HP": "Здоровье (HP)",
            "ATK": "Атака (ATK)",
            "CRIT": "Крит урон (CRIT)"
        },
        "no_translate": sorted(no_translate),
        "icons_count": len(icons_map),
        "categories": {
            "SKILLS": len([x for x in no_translate if x[0].isupper()]),
            "SPIRITS": len([x for x in no_translate if not x[0].isupper()]),
            "PROMOTIONS": 24,
            "CLASSES": 7
        }
    }
    
    return glossary


# ════════════════════════════════════════════════════════
# ЭТАП 2: СКАНИРОВАНИЕ ГАЙДОВ
# ════════════════════════════════════════════════════════

def scan_guides() -> List[Dict]:
    """Сканирует все гайды (EN + RU)"""
    guides = []
    
    for lang in ["en", "ru"]:
        lang_dir = GUIDES_DIR / lang
        if not lang_dir.exists():
            continue
        
        for category_dir in sorted(lang_dir.iterdir()):
            if not category_dir.is_dir():
                continue
            
            for md_file in sorted(category_dir.glob("*.md")):
                try:
                    content_md = md_file.read_text(encoding='utf-8')
                    
                    guide = {
                        "lang": lang,
                        "category": category_dir.name,
                        "guide_name": md_file.stem,
                        "content_md": content_md,
                        "content_text": md_to_text(content_md),
                        "icons_used": extract_icon_refs(content_md),
                        "media_links": extract_media_urls(content_md)
                    }
                    
                    guides.append(guide)
                    
                except Exception as e:
                    print(f"  ⚠ Ошибка {md_file.name}: {str(e)[:40]}")
    
    return guides


# ════════════════════════════════════════════════════════
# ЭТАП 4: ГЕНЕРАЦИЯ SQL
# ════════════════════════════════════════════════════════

def gen_sql_create_table() -> str:
    """SQL для создания таблицы"""
    return """CREATE TABLE IF NOT EXISTS guides (
    id SERIAL PRIMARY KEY,
    lang VARCHAR(10) NOT NULL DEFAULT 'en',
    category VARCHAR(255) NOT NULL,
    guide_name VARCHAR(255) NOT NULL UNIQUE,
    content_md TEXT NOT NULL,
    content_text TEXT NOT NULL,
    icons_used TEXT[] DEFAULT ARRAY[]::TEXT[],
    media_links TEXT[] DEFAULT ARRAY[]::TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_guides_lang ON guides(lang);
CREATE INDEX idx_guides_category ON guides(lang, category);
CREATE INDEX idx_guides_name ON guides(guide_name);
CREATE INDEX idx_guides_icons ON guides USING GIN(icons_used);
CREATE INDEX idx_guides_media ON guides USING GIN(media_links);
"""


def gen_sql_inserts(guides: List[Dict]) -> str:
    """SQL INSERT statements"""
    inserts = []
    
    for guide in guides:
        lang = guide['lang']
        cat = escape_sql_string(guide['category'])
        name = escape_sql_string(guide['guide_name'])
        md = escape_sql_string(guide['content_md'][:999999])
        text = escape_sql_string(guide['content_text'][:999999])
        
        icons = ', '.join([f"'{escape_sql_string(i)}'" for i in guide['icons_used']])
        icons_arr = f"ARRAY[{icons}]" if icons else "ARRAY[]"
        
        media = ', '.join([f"'{escape_sql_string(m)}'" for m in guide['media_links']])
        media_arr = f"ARRAY[{media}]" if media else "ARRAY[]"
        
        insert = f"""INSERT INTO guides (lang, category, guide_name, content_md, content_text, icons_used, media_links)
VALUES ('{lang}', '{cat}', '{name}', E'{md}', E'{text}', {icons_arr}::TEXT[], {media_arr}::TEXT[])
ON CONFLICT (guide_name) DO UPDATE SET updated_at = NOW();"""
        
        inserts.append(insert)
    
    return "\n\n".join(inserts)


# ════════════════════════════════════════════════════════
# ГЛАВНАЯ ФУНКЦИЯ
# ════════════════════════════════════════════════════════

def main():
    print("\n" + "="*70)
    print(" 🔧 ПОЛНАЯ ОБРАБОТКА ГАЙДОВ BLACKROSE ДЛЯ NEON")
    print("="*70)
    
    # ЭТАП 0-1: Glossary
    print("\n🔹 ЭТАП 0-1: Создание glossary.json...")
    glossary = create_glossary()
    glossary_file = OUTPUT_DIR / "glossary.json"
    
    if safe_write_json(glossary_file, glossary):
        print(f"   ✓ {glossary_file}")
        print(f"     - No-translate слов: {len(glossary['no_translate'])}")
    
    # ЭТАП 2: Сканирование
    print("\n🔹 ЭТАП 2-3: Сканирование и обработка гайдов...")
    guides = scan_guides()
    
    # Статистика
    en_count = len([g for g in guides if g['lang'] == 'en'])
    ru_count = len([g for g in guides if g['lang'] == 'ru'])
    
    all_icons = set()
    all_media = set()
    for g in guides:
        all_icons.update(g['icons_used'])
        all_media.update(g['media_links'])
    
    print(f"   ✓ Гайдов: {len(guides)} (EN={en_count}, RU={ru_count})")
    print(f"   ✓ Уникальных иконок: {len(all_icons)}")
    print(f"   ✓ Уникальных медиа: {len(all_media)}")
    
    # ЭТАП 4: SQL
    print("\n🔹 ЭТАП 4: Генерация import.sql...")
    
    sql_header = f"""-- BlackRose Guides Import for Neon
-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
-- Guides: {len(guides)} (EN={en_count}, RU={ru_count})

SET timezone = 'UTC';

"""
    
    create_table_sql = gen_sql_create_table()
    insert_sql = gen_sql_inserts(guides)
    
    full_sql = sql_header + create_table_sql + "\n\n-- ═══ INSERT STATEMENTS ═══\n\n" + insert_sql
    
    sql_file = OUTPUT_DIR / "import.sql"
    sql_file.write_text(full_sql, encoding='utf-8')
    
    print(f"   ✓ {sql_file}")
    print(f"     - Размер: {sql_file.stat().st_size / 1024:.1f} KB")
    print(f"     - INSERT statements: {len(guides)}")
    
    # Сводка
    summary = {
        "total_guides": len(guides),
        "by_language": {"en": en_count, "ru": ru_count},
        "unique_icons": len(all_icons),
        "unique_media": len(all_media),
        "sql_file_size_bytes": sql_file.stat().st_size,
        "created": datetime.now().isoformat()
    }
    
    summary_file = OUTPUT_DIR / "summary.json"
    safe_write_json(summary_file, summary)
    print(f"   ✓ {summary_file}")
    
    # Финальный вывод
    print("\n" + "="*70)
    print(" ✨ ГОТОВО К ИМПОРТУ! ✨")
    print("="*70)
    print(f"""
📂 ФАЙЛЫ В output_neon/:
   • glossary.json → Справочник терминов
   • import.sql → SQL скрипт (готов к Neon)
   • summary.json → Статистика

📊 СТАТИСТИКА:
   • Всего гайдов: {len(guides)}
   • Языки: EN={en_count}, RU={ru_count}
   • Уникальных иконок: {len(all_icons)}
   • Уникальных медиа: {len(all_media)}

🚀 ДЛЯ ИМПОРТА В NEON:
   1. Откроить https://console.neon.tech
   2. Project > SQL Editor
   3. Скопировать содержимое output_neon/import.sql
   4. Вставить и выполнить
   5. Проверить: SELECT COUNT(*) FROM guides;
""")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
