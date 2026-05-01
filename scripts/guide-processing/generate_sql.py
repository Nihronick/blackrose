#!/usr/bin/env python3
"""
ЭТАП 4: Генерация import.sql для PostgreSQL/Neon
Создаёт таблицу guides и SQL INSERT statements
"""

import json
import os
import re
from pathlib import Path
from typing import List, Dict
from datetime import datetime

# ═══════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).parent
GUIDES_DIR = PROJECT_ROOT / "guides"
OUTPUT_DIR = PROJECT_ROOT / "output_neon"

def escape_sql_string(s: str) -> str:
    """Экранирует строку для SQL"""
    # Заменяем одинарные кавычки на две кавычки
    s = s.replace("'", "''")
    # Удаляем потенциально опасные символы
    s = s.replace("\\", "\\\\")
    return s


def extract_media_links(content: str) -> List[str]:
    """Извлекает media URLs"""
    media_urls = []
    
    # Discord CDN
    discord_pattern = r'(https?://(?:cdn|media)\.discord(?:app)?\.(?:com|net)/[^\s\)"\']*)(?:\.[a-z]{2,4})?'
    media_urls.extend(re.findall(discord_pattern, content))
    
    # Direct media
    media_pattern = r'(https?://[^\s\)\"\']*\.(?:png|jpg|jpeg|gif|webp|mp4|webm|mov|mkv))'
    media_urls.extend(re.findall(media_pattern, content, re.IGNORECASE))
    
    # Previews
    preview_pattern = r'(https?://(?:i\.ytimg|imgur|tenor)\.com[^\s\)\"\']*)'
    media_urls.extend(re.findall(preview_pattern, content))
    
    return list(set(media_urls))


def normalize_link_label(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def alias_variants(alias: str) -> set[str]:
    variants: set[str] = set()
    if not alias:
        return variants

    variants.add(alias)

    for prefix in ("the_", "a_", "an_"):
        if alias.startswith(prefix):
            variants.add(alias[len(prefix) :])

    if alias.endswith("ies") and len(alias) > 4:
        variants.add(alias[:-3] + "y")
    if alias.endswith("es") and len(alias) > 3:
        variants.add(alias[:-2])
    if alias.endswith("s") and len(alias) > 2:
        variants.add(alias[:-1])

    return {v.strip("_") for v in variants if v.strip("_")}


def resolve_key(label: str, alias_to_key: dict[str, str]) -> str | None:
    base = normalize_link_label(label)
    for candidate in alias_variants(base):
        key = alias_to_key.get(candidate)
        if key:
            return key
    return None


def build_guide_key_lookup() -> tuple[dict[Path, str], dict[str, str]]:
    path_to_key: dict[Path, str] = {}
    alias_to_key: dict[str, str] = {}

    for lang in ["en", "ru"]:
        lang_dir = GUIDES_DIR / lang
        if not lang_dir.exists():
            continue

        for category_dir in sorted(lang_dir.iterdir()):
            if not category_dir.is_dir():
                continue

            for guide_file in sorted(category_dir.glob("*.md")):
                key = f"{category_dir.name}_{guide_file.stem}".lower()
                key = re.sub(r"[^a-z0-9]+", "_", key)
                key = re.sub(r"_+", "_", key).strip("_")
                resolved = guide_file.resolve()
                path_to_key[resolved] = key
                for alias in {
                    normalize_link_label(guide_file.stem.replace("_", " ")),
                    normalize_link_label(guide_file.stem.replace("-", " ")),
                }:
                    for variant in alias_variants(alias):
                        alias_to_key.setdefault(variant, key)

    return path_to_key, alias_to_key


def rewrite_internal_links(
    content: str,
    current_file: Path,
    path_to_key: dict[Path, str],
    alias_to_key: dict[str, str],
) -> tuple[str, list[str]]:
    meta_links: list[str] = []

    def remember(key: str) -> None:
        if key and key not in meta_links:
            meta_links.append(key)

    def replace_wikilink(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        label = (match.group(2) or "").strip()
        remember(key)
        return match.group(0) if not label else f"[[{key}|{label}]]"

    content = re.sub(r"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]", replace_wikilink, content)

    def replace_markdown_link(match: re.Match[str]) -> str:
        label = match.group(1).strip()
        target = match.group(2).strip()

        if target.startswith(("http://", "https://")):
            key = resolve_key(label, alias_to_key)
            if key:
                remember(key)
                return f"[[{key}|{label}]]"
            return match.group(0)

        if target.endswith(".md"):
            resolved = (current_file.parent / target).resolve()
            key = path_to_key.get(resolved)
            if key:
                remember(key)
                return f"[[{key}|{label}]]"

        return match.group(0)

    content = re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", replace_markdown_link, content)
    return content, meta_links


def extract_icon_references(content: str) -> List[str]:
    """Извлекает {{icon_name}} references"""
    pattern = r'\{\{(\w+)\}\}'
    return re.findall(pattern, content)


def convert_md_to_plain_text(content: str) -> str:
    """Примитивное конвертирование Markdown в plain text"""
    # Убираем Markdown разметку
    text = content
    text = re.sub(
        r"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]",
        lambda m: m.group(2) or m.group(1),
        text,
    )
    # Заголовки
    text = re.sub(r'#+\s+', '', text)
    # Жирный и курсив
    text = re.sub(r'\*\*|__|\*|_|~~', '', text)
    # Коды
    text = re.sub(r'`{1,3}.*?`{1,3}', '', text, flags=re.DOTALL)
    # Ссылки
    text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)
    # Списки
    text = re.sub(r'[-*]\s+', '• ', text)
    # Горизонтальные линии
    text = re.sub(r'(---|\*\*\*|___)', '─' * 10, text)
    # Квадратные скобки в видео/медиа плеерах
    text = re.sub(r'<[^>]*>', '', text)
    # Убираем избыточные пустые строки
    text = re.sub(r'\n\n+', '\n', text)
    
    return text.strip()


def scan_all_guides() -> List[Dict]:
    """Сканирует и обрабатывает все гайды"""
    guides_data = []
    path_to_key, alias_to_key = build_guide_key_lookup()
    
    for lang in ["en", "ru"]:
        lang_dir = GUIDES_DIR / lang
        if not lang_dir.exists():
            continue
        
        for category_dir in sorted(lang_dir.iterdir()):
            if not category_dir.is_dir():
                continue
            
            for guide_file in sorted(category_dir.glob("*.md")):
                try:
                    content_md = guide_file.read_text(encoding="utf-8")
                    content_md, meta_links = rewrite_internal_links(
                        content_md, guide_file, path_to_key, alias_to_key
                    )
                    
                    guide_data = {
                        "id": None,  # Auto-increment
                        "lang": lang,
                        "category": category_dir.name,
                        "guide_name": guide_file.stem,
                        "content_md": content_md,
                        "content_text": convert_md_to_plain_text(content_md),
                        "icons_used": extract_icon_references(content_md),
                        "media_links": extract_media_links(content_md),
                        "meta_links": meta_links,
                        "file_path": str(guide_file.relative_to(PROJECT_ROOT))
                    }
                    
                    guides_data.append(guide_data)
                    print(f"✓ {lang}/{category_dir.name}/{guide_file.stem}")
                    
                except Exception as e:
                    print(f"⚠ Ошибка при обработке {guide_file}: {e}")
    
    return guides_data


def generate_create_table_sql() -> str:
    """Генерирует SQL для создания таблицы"""
    return """
-- ═══════════════════════════════════════════════════════
-- Таблица для хранения гайдов BlackRose
-- ═══════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS guides (
    id SERIAL PRIMARY KEY,
    lang VARCHAR(10) NOT NULL DEFAULT 'en',
    category VARCHAR(255) NOT NULL,
    guide_name VARCHAR(255) NOT NULL UNIQUE,
    content_md TEXT NOT NULL,
    content_text TEXT NOT NULL,
    icons_used TEXT[] DEFAULT ARRAY[]::TEXT[],
    media_links TEXT[] DEFAULT ARRAY[]::TEXT[],
    meta_links JSONB DEFAULT '[]'::JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_guides_lang ON guides(lang);
CREATE INDEX IF NOT EXISTS idx_guides_category ON guides(lang, category);
CREATE INDEX IF NOT EXISTS idx_guides_name ON guides(guide_name);
CREATE INDEX IF NOT EXISTS idx_guides_icons ON guides USING GIN(icons_used);
CREATE INDEX IF NOT EXISTS idx_guides_media ON guides USING GIN(media_links);
CREATE INDEX IF NOT EXISTS idx_guides_meta ON guides USING GIN(meta_links);

-- Комментарии таблицы
COMMENT ON TABLE guides IS 'Гайды BlackRose MiniApp';
COMMENT ON COLUMN guides.lang IS 'Язык: en или ru';
COMMENT ON COLUMN guides.category IS 'Категория гайда (adventure, character, skills, ...)';
COMMENT ON COLUMN guides.guide_name IS 'Имя гайда (уникально)';
COMMENT ON COLUMN guides.content_md IS 'Контент в Markdown формате';
COMMENT ON COLUMN guides.content_text IS 'Контент в plain text (для поиска)';
COMMENT ON COLUMN guides.icons_used IS 'Массив использованных иконок {{name}}';
COMMENT ON COLUMN guides.media_links IS 'Массив медиа-ссылок (Discord CDN, images, videos)';
COMMENT ON COLUMN guides.meta_links IS 'JSON-массив внутренних ссылок и информации';

"""


def generate_insert_statements(guides_data: List[Dict]) -> str:
    """Генерирует INSERT statements для всех гайдов"""
    insert_statements = []
    
    for i, guide in enumerate(guides_data, 1):
        # Экранируем строки для SQL
        category = escape_sql_string(guide["category"])
        guide_name = escape_sql_string(guide["guide_name"])
        content_md = escape_sql_string(guide["content_md"][:1000000])  # Лимит 1MB
        content_text = escape_sql_string(guide["content_text"][:1000000])
        
        # Иконки как TEXT[] array
        icons_array = "ARRAY['" + "','".join([escape_sql_string(i) for i in guide["icons_used"]]) + "']::TEXT[]" if guide["icons_used"] else "ARRAY[]::TEXT[]"
        
        # Медиа как TEXT[] array
        media_array = "ARRAY['" + "','".join([escape_sql_string(m) for m in guide["media_links"]]) + "']::TEXT[]" if guide["media_links"] else "ARRAY[]::TEXT[]"
        meta_links_json = json.dumps(guide.get("meta_links", []), ensure_ascii=False)
        
        sql = f"""INSERT INTO guides (lang, category, guide_name, content_md, content_text, icons_used, media_links, meta_links)
VALUES ('{guide['lang']}', '{category}', '{guide_name}', E'{content_md}', E'{content_text}', {icons_array}, {media_array}, '{escape_sql_string(meta_links_json)}'::jsonb)
ON CONFLICT (guide_name) DO UPDATE SET 
    content_md = EXCLUDED.content_md,
    content_text = EXCLUDED.content_text,
    icons_used = EXCLUDED.icons_used,
    media_links = EXCLUDED.media_links,
    meta_links = EXCLUDED.meta_links,
    updated_at = NOW();"""
        
        insert_statements.append(sql)
    
    return "\n\n".join(insert_statements)


def main():
    print("🔹 ЭТАП 4: ГЕНЕРАЦИЯ import.sql ДЛЯ NEON")
    print("=" * 60)
    
    print("\n📂 Сканирование всех гайдов...")
    guides_data = scan_all_guides()
    
    print(f"\n✓ Обработано: {len(guides_data)} гайдов")
    
    # Создаём SQL файл
    print("\n📝 Генерация SQL скрипта...")
    
    # Заголовок
    header = f"""-- BlackRose Guides Import Script
-- Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Гайдов: {len(guides_data)}
-- Языков: {len(set(g['lang'] for g in guides_data))}
-- 
-- ИНСТРУКЦИЯ:
-- 1. Скопируй содержимое этого файла
-- 2. Открой Neon Dashboard → SQL Editor
-- 3. Вставь и выполни все команды
-- 4. Проверь результат: SELECT COUNT(*) FROM guides;

SET "timezone" TO 'UTC';

"""
    
    # CREATE TABLE
    create_table = generate_create_table_sql()
    
    # INSERT statements
    print("   Генерирую INSERT statements...")
    inserts = generate_insert_statements(guides_data)
    
    # Итоговый скрипт
    full_sql = header + create_table + "\n\n-- ═══════════════════════════════════════════════════════\n-- INSERT STATEMENTS\n-- ═══════════════════════════════════════════════════════\n\n" + inserts
    
    # Сохраняем
    output_file = OUTPUT_DIR / "import.sql"
    output_file.write_text(full_sql, encoding="utf-8")
    
    print(f"\n✓ Сохранено: {output_file}")
    print(f"  Размер: {output_file.stat().st_size / 1024:.1f} KB")
    
    # Создаём сводку
    summary = {
        "total_guides": len(guides_data),
        "by_language": {},
        "by_category": {},
        "total_icons": len(set(icon for g in guides_data for icon in g["icons_used"])),
        "total_media": len(set(m for g in guides_data for m in g["media_links"])),
        "created_at": datetime.now().isoformat()
    }
    
    for guide in guides_data:
        lang = guide["lang"]
        category = guide["category"]
        
        if lang not in summary["by_language"]:
            summary["by_language"][lang] = 0
        summary["by_language"][lang] += 1
        
        if category not in summary["by_category"]:
            summary["by_category"][category] = {"en": 0, "ru": 0}
        summary["by_category"][category][lang] += 1
    
    summary_file = OUTPUT_DIR / "import_summary.json"
    summary_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    
    print(f"\n📊 ПОЛНАЯ СТАТИСТИКА:")
    print(f"   Всего гайдов: {summary['total_guides']}")
    print(f"   Языки: {summary['by_language']}")
    print(f"   Категорий: {len(summary['by_category'])}")
    print(f"   Уникальных иконок: {summary['total_icons']}")
    print(f"   Уникальных медиа: {summary['total_media']}")
    
    print(f"\n   ✓ Сводка: {summary_file}")
    
    # ИНСТРУКЦИЯ для Neon
    instruction = f"""
# 🚀 ИНСТРУКЦИЯ ПО ИМПОРТУ В NEON

## 1️⃣ ПОДГОТОВКА
- Файл: `import.sql` ({output_file.stat().st_size / 1024:.1f} KB)
- Гайдов: {len(guides_data)}
- Статус: {len([g for g in guides_data if g['lang'] == 'en'])} EN + {len([g for g in guides_data if g['lang'] == 'ru'])} RU

## 2️⃣ ВАРИАНТ 1: Neon Dashboard → SQL Editor (рекомендуется)
```bash
1. Открой https://console.neon.tech
2. Project > SQL Editor
3. Скопируй содержимое import.sql
4. Вставь в редактор
5. Нажми "Execute"
```

## 3️⃣ ВАРИАНТ 2: Через psql (локально)
```bash
psql "postgresql://user:password@ep-xxx.neon.tech/database?sslmode=require" -f import.sql
```

## 4️⃣ ПРОВЕРКА РЕЗУЛЬТАТА
```sql
SELECT COUNT(*) AS total_guides FROM guides;
SELECT COUNT(*) FILTER (WHERE lang='en') AS en_guides, 
       COUNT(*) FILTER (WHERE lang='ru') AS ru_guides FROM guides;
SELECT category, COUNT(*) FROM guides GROUP BY category ORDER BY category;
```

## 5️⃣ ПОИСК ПО ИКОНКАМ
```sql
SELECT guide_name, category FROM guides 
WHERE 'Meditation' = ANY(icons_used) 
LIMIT 10;
```

## 6️⃣ ПОИСК ПО МЕДИА
```sql
SELECT guide_name, category, array_length(media_links, 1) as media_count 
FROM guides 
WHERE array_length(media_links, 1) > 0 
ORDER BY media_count DESC;
```

---
✨ Готово! База данных заполнена.
"""
    
    instruction_file = OUTPUT_DIR / "IMPORT_INSTRUCTION.md"
    instruction_file.write_text(instruction)
    
    print(f"   ✓ Инструкция: {instruction_file}")
    
    print("\n✅ ЭТАП 4 ЗАВЕРШЕН!")


if __name__ == "__main__":
    main()
