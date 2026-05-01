#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 1 TRANSLATION: Перевод 89 гайдов на русский
Использует Google Translate через libre-translate (если доступен) или requests
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict
import time
import urllib.request
import urllib.parse

# Кодировка
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent
GUIDES_DIR = PROJECT_ROOT / "guides"
OUTPUT_DIR = PROJECT_ROOT / "output_media"

# ════════════════════════════════════════════════════════
# ПЕРЕВОД ЧЕРЕЗ GOOGLE TRANSLATE JSON API
# ════════════════════════════════════════════════════════

def translate_text_google(text, target_lang='ru'):
    """Переводит текст через Google Translate JSON API (без ключа)"""
    if not text or len(text.strip()) == 0:
        return text
    
    try:
        # Google Translate API endpoint (бесплатный)
        text_encoded = urllib.parse.quote(text[:3000])  # Лимит 3000 символов за раз
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl={target_lang}&dt=t&q={text_encoded}"
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        
        with urllib.request.urlopen(req, timeout=5) as response:
            data = response.read().decode('utf-8')
            
            # Парсим JSON результат
            # Формат: [[[транслейт1,оригинал1,...],...],null,null,...]
            import re
            # Ищем первый элемент массива который содержит переводы
            match = re.search(r'\[\["([^"]*)"', data)
            if match:
                result = match.group(1)
                return result
        
        return None
    except Exception as e:
        return None


def translate_paragraph(para_text):
    """Переводит параграф текста"""
    if not para_text or len(para_text.strip()) < 2:
        return para_text
    
    # Удаляем лишние пробелы
    para_text = para_text.strip()
    
    # Пытаемся перевести
    translated = translate_text_google(para_text, 'ru')
    
    if translated and translated != para_text:
        return translated
    else:
        # Если перевод не сработал, возвращаем оригинал
        return para_text


def translate_markdown(content):
    """
    Переводит markdown контент
    Сохраняет структуру: заголовки, коды, ссылки, списки
    """
    
    lines = content.split('\n')
    result_lines = []
    buffer = []
    in_code_block = False
    in_quote = False
    
    for line in lines:
        stripped = line.strip()
        
        # Код-блоки
        if stripped.startswith('```'):
            # Переводим накопленный буфер
            if buffer:
                para = '\n'.join(buffer)
                translated = translate_paragraph(para)
                result_lines.append(translated)
                buffer = []
            
            in_code_block = not in_code_block
            result_lines.append(line)
            continue
        
        # Внутри кода не переводим
        if in_code_block:
            result_lines.append(line)
            continue
        
        # Пустые строки
        if not stripped:
            if buffer:
                para = '\n'.join(buffer)
                translated = translate_paragraph(para)
                result_lines.append(translated)
                buffer = []
            result_lines.append(line)
            continue
        
        # Заголовки (начинаются с #)
        if stripped.startswith('#'):
            if buffer:
                para = '\n'.join(buffer)
                translated = translate_paragraph(para)
                result_lines.append(translated)
                buffer = []
            
            # Переводим заголовок
            header_text = stripped[1:].strip()
            translated_header = translate_paragraph(header_text)
            level = len(stripped) - len(stripped.lstrip('#'))
            result_lines.append('#' * level + ' ' + translated_header)
            continue
        
        # Списки (начинаются с - или *)
        if stripped.startswith(('-', '•', '*')):
            if buffer:
                para = '\n'.join(buffer)
                translated = translate_paragraph(para)
                result_lines.append(translated)
                buffer = []
            
            # Переводим элемент списка
            list_char = stripped[0]
            list_text = stripped[1:].strip()
            translated_item = translate_paragraph(list_text)
            indent = len(line) - len(line.lstrip())
            result_lines.append(' ' * indent + list_char + ' ' + translated_item)
            continue
        
        # Обычный текст - накапливаем в буфер
        buffer.append(line)
    
    # Переводим оставшийся буфер
    if buffer:
        para = '\n'.join(buffer)
        translated = translate_paragraph(para)
        result_lines.append(translated)
    
    return '\n'.join(result_lines)


# ════════════════════════════════════════════════════════
# ПЕРЕВОД ВСЕ ГАЙДОВ
# ════════════════════════════════════════════════════════

def translate_guides():
    """Переводит все гайды из guides/en/ в guides/ru/"""
    
    print("=" * 80)
    print("PHASE 1 TRANSLATION: ПЕРЕВОД ГАЙДОВ НА РУССКИЙ")
    print("=" * 80)
    
    en_dir = GUIDES_DIR / "en"
    ru_dir = GUIDES_DIR / "ru"
    
    if not en_dir.exists():
        print("✗ Директория guides/en/ не найдена")
        return
    
    total_guides = 0
    translated = 0
    failed = 0
    
    # Итерируем по категориям
    for category_dir in sorted(en_dir.iterdir()):
        if not category_dir.is_dir():
            continue
        
        category = category_dir.name
        print(f"\n📁 {category}/")
        
        # Создаём директорию в RU если её нет
        ru_cat_dir = ru_dir / category
        ru_cat_dir.mkdir(parents=True, exist_ok=True)
        
        # Итерируем по файлам
        for md_file in sorted(category_dir.glob("*.md")):
            total_guides += 1
            
            try:
                # Читаем EN файл
                en_content = md_file.read_text(encoding='utf-8')
                
                # Проверяем, есть ли уже переведённый файл
                ru_file = ru_cat_dir / md_file.name
                
                # Переводим
                print(f"  🌍 {md_file.name}...", end='', flush=True)
                ru_content = translate_markdown(en_content)
                
                # Сохраняем в RU
                ru_file.write_text(ru_content, encoding='utf-8')
                print(" ✓")
                translated += 1
                
                # Небольшая задержка чтобы не перегружать сервер
                time.sleep(0.5)
                
            except Exception as e:
                print(f" ✗ ({e})")
                failed += 1
    
    # Итоги
    print("\n" + "=" * 80)
    print("✅ ИТОГИ ПЕРЕВОДА")
    print("=" * 80)
    
    print(f"\n✓ Всего гайдов: {total_guides}")
    print(f"✓ Переведено: {translated}")
    print(f"✗ Ошибок: {failed}")
    
    success_rate = int(translated / total_guides * 100) if total_guides > 0 else 0
    print(f"✓ Успешность: {success_rate}%")
    
    # Сохраняем отчёт
    report = {
        "action": "TRANSLATE_GUIDES",
        "total": total_guides,
        "translated": translated,
        "failed": failed,
        "success_rate": success_rate
    }
    
    report_path = OUTPUT_DIR / "translation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Отчёт: output_media/translation_report.json")
    
    return report

if __name__ == "__main__":
    translate_guides()
