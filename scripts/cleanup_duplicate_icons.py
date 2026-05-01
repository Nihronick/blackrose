#!/usr/bin/env python3
"""
Cleanup Script: Удаляет дубликаты иконок из backend/icons.py

Список иконок которые удаляются (это дубликаты):
- hp_reg_stone (дубликат hp_stone)
- M1 (дубликат sword_m1)
- Tera (дубликат class_terra)
- Nova (дубликат class_nova)
- Seed (дубликат class_sid)
- OrrBase (дубликат sword_opp)
- orb (дубликат sword_orb)
"""

import os
import re

# Файл который нужно редактировать
ICONS_FILE = "backend/icons.py"

# Иконки которые нужно удалить (дубликаты)
ICONS_TO_DELETE = [
    "hp_reg_stone",
    "M1",
    "Tera",
    "Nova",
    "Seed",
    "OrrBase",
    "orb",
]

def remove_icon(content, icon_key):
    """Удалить иконку из содержимого файла"""
    # Ищем строку типа:
    # "hp_reg_stone": _url("class_etc/hp_reg_stone.png"),
    # или просто
    # "hp_reg_stone": ...,
    
    pattern = rf'^\s*"?{re.escape(icon_key)}"?\s*:\s*[^,]*,\n'
    new_content = re.sub(pattern, '', content, flags=re.MULTILINE)
    
    return new_content

def main():
    print(f"📝 Читаю {ICONS_FILE}...")
    
    # Читаем файл
    with open(ICONS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_size = len(content)
    
    # Удаляем каждую иконку
    for icon_key in ICONS_TO_DELETE:
        print(f"  ❌ Удаляю: {icon_key}")
        content = remove_icon(content, icon_key)
    
    # Удаляем пустые строки которые остались после удаления
    lines = content.split('\n')
    cleaned_lines = []
    for i, line in enumerate(lines):
        # Пропускаем пустые строки только если рядом тоже пустые
        if line.strip() == '':
            if not (i > 0 and lines[i-1].strip() == '' and i < len(lines) - 1 and lines[i+1].strip() == ''):
                cleaned_lines.append(line)
        else:
            cleaned_lines.append(line)
    
    content = '\n'.join(cleaned_lines)
    
    # Пишем обратно
    with open(ICONS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_size = len(content)
    deleted_size = original_size - new_size
    
    print(f"\n✅ Успешно!")
    print(f"   Удалено: {len(ICONS_TO_DELETE)} иконок")
    print(f"   Размер файла: {original_size} → {new_size} байт ({deleted_size:+d})")
    print(f"   Файл сохранён: {ICONS_FILE}")

if __name__ == "__main__":
    main()
