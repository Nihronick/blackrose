#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 1 补完: Добавление недостающих 14 гайдов
1. Копирует из slayerpedia/ в guides/en/ (конвертирует .txt → .md)
2. Переводит содержимое на русский с помощью Google Translate
3. Сохраняет в guides/ru/
"""

import os
import sys
import json
import re
from pathlib import Path
from urllib.parse import quote

# Кодировка
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent
SLAYERPEDIA_DIR = PROJECT_ROOT / "slayerpedia"
GUIDES_DIR = PROJECT_ROOT / "guides"
OUTPUT_DIR = PROJECT_ROOT / "output_media"

# Список недостающих гайдов (category/guide_name)
MISSING_GUIDES = [
    ("Beginner-guide", "Frequently Asked Questions"),
    ("Beginner-guide", "Glossary of Terms"),
    ("Beginner-guide", "Online VS Offline Farming"),
    ("Beginner-guide", "Path Of Suggested Progression"),
    ("Beginner-guide", "Rage + Rave (Early), Late Game Rotation (Late)"),
    ("Beginner-guide", "TLDR version of Path for Promo"),
    ("Beginner-guide", "Where to spend Diamonds, Emeralds and Feathers"),
    ("disclaimer", "disclaimer"),
    ("event-help", "event-help"),
    ("promotion-recommendation", "promotion-recommendation"),
    ("shop", "shop"),
    ("spirit", "Detailed ProsCons list for Spirits"),
    ("spirit", "Spirit Exchange System 'Meloning"),
    ("suit-recommendation", "suit-recommendation"),
]

# ════════════════════════════════════════════════════════
# ПРОСТОЙ ПЕРЕВОД С GOOGLE TRANSLATE API
# ════════════════════════════════════════════════════════

def translate_text(text, target_lang='ru'):
    """Переводит текст с помощью Google Translate (без API ключа через requests)"""
    try:
        import urllib.request
        import json
        
        # Google Translate API (бесплатная версия через браузер)
        url = f"https://translate.googleapis.com/translate_a/element.js?cb=_translate_a"
        
        # Альтернатива: используем встроенный API
        text_encoded = quote(text)
        url_translate = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl={target_lang}&dt=t&q={text_encoded}"
        
        try:
            req = urllib.request.Request(url_translate)
            req.add_header('User-Agent', 'Mozilla/5.0')
            with urllib.request.urlopen(req, timeout=5) as response:
                result = response.read().decode('utf-8')
                # Парсим результат (очень базовый парсинг)
                import re
                matches = re.findall(r'\[\["([^"]+)"', result)
                if matches:
                    return ''.join(matches)
        except Exception as e:
            print(f"    ⚠️  Ошибка перевода: {e}")
            return None
    except Exception as e:
        print(f"    ⚠️  Ошибка импорта: {e}")
        return None

def translate_markdown_content(content):
    """
    Переводит markdown контент параграфами
    Сохраняет форматирование и код
    """
    lines = content.split('\n')
    translated_lines = []
    buffer = []
    in_code_block = False
    
    for line in lines:
        # Проверяем код-блоки
        if line.strip().startswith('```'):
            if buffer:
                # Переводим накопленный текст
                para_text = '\n'.join(buffer)
                translated = translate_text(para_text)
                if translated:
                    translated_lines.append(translated)
                else:
                    translated_lines.append(para_text)
                buffer = []
            
            in_code_block = not in_code_block
            translated_lines.append(line)
        
        elif in_code_block:
            translated_lines.append(line)
        
        elif line.strip() == '':
            # Пустая строка - конец параграфа
            if buffer:
                para_text = '\n'.join(buffer)
                translated = translate_text(para_text)
                if translated:
                    translated_lines.append(translated)
                else:
                    translated_lines.append(para_text)
                buffer = []
            translated_lines.append(line)
        
        else:
            buffer.append(line)
    
    # Переводим последний буфер
    if buffer:
        para_text = '\n'.join(buffer)
        translated = translate_text(para_text)
        if translated:
            translated_lines.append(translated)
        else:
            translated_lines.append(para_text)
    
    return '\n'.join(translated_lines)

# ════════════════════════════════════════════════════════
# КОНВЕРТАЦИЯ И КОПИРОВАНИЕ
# ════════════════════════════════════════════════════════

def txt_to_markdown(txt_content):
    """Конвертирует простой текст в markdown"""
    # Заголовки: # для # в начале строк
    # Списки: - для * или -
    # Жирный текст: **text** для __text__
    
    lines = txt_content.split('\n')
    md_lines = []
    
    for line in lines:
        # Заголовки
        if line.startswith('#'):
            md_lines.append(line)
        elif line.startswith('__'):
            # Конвертируем __text__ в **text**
            line = line.replace('__', '**')
            md_lines.append(line)
        elif line.strip().startswith('*'):
            md_lines.append(line)
        else:
            md_lines.append(line)
    
    return '\n'.join(md_lines)

def create_guides_directories():
    """Создаёт недостающие директории в guides/"""
    for category, _ in MISSING_GUIDES:
        en_cat_dir = GUIDES_DIR / "en" / category
        ru_cat_dir = GUIDES_DIR / "ru" / category
        
        en_cat_dir.mkdir(parents=True, exist_ok=True)
        ru_cat_dir.mkdir(parents=True, exist_ok=True)

def add_missing_guides():
    """Копирует и переводит недостающие гайды"""
    
    print("=" * 80)
    print("PHASE 1 補完: ДОБАВЛЕНИЕ НЕДОСТАЮЩИХ 14 ГАЙДОВ")
    print("=" * 80)
    
    create_guides_directories()
    
    added = []
    failed = []
    
    for category, guide_name in MISSING_GUIDES:
        print(f"\n📖 {category}/{guide_name}")
        
        # Ищем файл в slayerpedia
        slayer_file = SLAYERPEDIA_DIR / category / f"{guide_name}.txt"
        
        if not slayer_file.exists():
            print(f"   ⚠️  Файл не найден в slayerpedia")
            failed.append(f"{category}/{guide_name}")
            continue
        
        try:
            # Читаем исходный файл
            content = slayer_file.read_text(encoding='utf-8')
            
            # Конвертируем в markdown
            md_content = txt_to_markdown(content)
            
            # Сохраняем в EN
            md_filename = guide_name.replace(' ', '_') + '.md'
            en_file = GUIDES_DIR / "en" / category / md_filename
            en_file.write_text(md_content, encoding='utf-8')
            
            print(f"   ✓ Сохранено в guides/en/{category}/{md_filename}")
            
            # Переводим на RU
            print(f"   🌍 Перевод на русский...")
            ru_content = translate_markdown_content(md_content)
            
            # Если перевод не удался, используем оригинал с пометкой
            if not ru_content or ru_content == md_content:
                print(f"   ⚠️  Автоматический перевод не доступен, используется оригинальный текст с пометкой [EN]")
                ru_content = f"[ТРЕБУЕТСЯ ПЕРЕВОД]\n\n{md_content}"
            
            # Сохраняем в RU
            ru_file = GUIDES_DIR / "ru" / category / md_filename
            ru_file.write_text(ru_content, encoding='utf-8')
            
            print(f"   ✓ Сохранено в guides/ru/{category}/{md_filename}")
            added.append(f"{category}/{guide_name}")
            
        except Exception as e:
            print(f"   ✗ Ошибка: {e}")
            failed.append(f"{category}/{guide_name}")
    
    # Итоги
    print("\n" + "=" * 80)
    print("✅ ИТОГИ ДОБАВЛЕНИЯ")
    print("=" * 80)
    
    print(f"\n✓ Добавлено: {len(added)}/14")
    print(f"✗ Ошибок: {len(failed)}/14")
    
    if added:
        print(f"\nУспешно добавлены:")
        for guide in added[:10]:
            print(f"  ✓ {guide}")
        if len(added) > 10:
            print(f"  ... и ещё {len(added) - 10}")
    
    if failed:
        print(f"\nОшибки:")
        for guide in failed:
            print(f"  ✗ {guide}")
    
    # Сохраняем отчёт
    report = {
        "action": "ADD_MISSING_GUIDES",
        "total_added": len(added),
        "total_failed": len(failed),
        "added_guides": added,
        "failed_guides": failed
    }
    
    report_path = OUTPUT_DIR / "add_missing_guides_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Отчёт: output_media/add_missing_guides_report.json")
    
    return report

if __name__ == "__main__":
    add_missing_guides()
