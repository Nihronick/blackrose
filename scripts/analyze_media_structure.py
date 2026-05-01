#!/usr/bin/env python3
"""
Анализ всех медиа-ссылок в русских гайдах и предложение структуры папок
"""

import re
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse, unquote

def extract_media_urls(guides_dir="guides/ru"):
    """Извлечь все медиа ссылки из гайдов"""
    media_by_type = defaultdict(list)
    media_by_guide = defaultdict(list)
    
    for md_file in sorted(Path(guides_dir).rglob("*.md")):
        category = md_file.parent.name
        filename = md_file.name
        file_key = f"{category}/{filename}"
        
        content = md_file.read_text(encoding='utf-8')
        
        # Найти все медиа ссылки
        urls = re.findall(r'https://(?:media\.discordapp\.net|cdn\.discordapp\.com|cdn\.jsdelivr\.net)[^\s)]+', content)
        
        for url in urls:
            # Извлечь расширение
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            # Определить тип файла
            if path.endswith('.gif'):
                file_type = 'gif'
            elif path.endswith(('.png', '.jpg', '.jpeg', '.webp')):
                file_type = 'images'
            elif path.endswith(('.mp4', '.webm', '.mov')):
                file_type = 'videos'
            else:
                file_type = 'other'
            
            # Извлечь ID из URL (message ID обычно последний компонент)
            parts = path.split('/')
            file_id = parts[-1].split('?')[0] if parts[-1] else url.split('/')[-1][:20]
            
            media_by_type[file_type].append({
                'url': url,
                'guide': file_key,
                'file_id': file_id,
                'path': path,
            })
            
            media_by_guide[file_key].append({
                'url': url,
                'type': file_type,
            })
    
    return media_by_type, media_by_guide

def print_structure_recommendation():
    """Вывести рекомендуемую структуру папок"""
    
    print("=" * 80)
    print("РЕКОМЕНДУЕМАЯ СТРУКТУРА ПАПОК ДЛЯ МЕДИА")
    print("=" * 80)
    print()
    
    print("📁 assets/")
    print("├── 📁 media/")
    print("│   ├── 📁 guides/              # Медиа из гайдов по категориям")
    print("│   │   ├── 📁 character/       # Персонажи (Constellation, Memory Tree, etc)")
    print("│   │   ├── 📁 skills/         # Навыки")
    print("│   │   ├── 📁 equipment/      # Снаряжение")
    print("│   │   ├── 📁 spirit/         # Духи")
    print("│   │   ├── 📁 companion/      # Спутники")
    print("│   │   ├── 📁 stage/          # Этапы (bosses, farm info)")
    print("│   │   ├── 📁 promotions/     # Протвижения (early, mid, late)")
    print("│   │   ├── 📁 adventure/      # Приключения")
    print("│   │   └── 📁 misc/           # Прочее (shop, event-help, etc)")
    print("│   │")
    print("│   ├── 📁 screenshots/        # Screenshot из гайдов")
    print("│   └── 📁 animations/         # GIF анимации")
    print()
    
    print("СОГЛАШЕНИЕ ПО НАЗВАНИЯМ ФАЙЛОВ:")
    print("-" * 80)
    print()
    
    print("IMAGES (PNG, WebP, JPG):")
    print("  Компактный формат: {guide_key}_{description}_{index}.png")
    print()
    print("  Примеры:")
    print("    • character_constellation_level_01.png")
    print("    • character_constellation_rewards.png")
    print("    • equipment_soul_weapon_detail_01.png")
    print("    • stage_boss_info_chart.png")
    print("    • spirit_tier_list_comparison.png")
    print()
    
    print("ANIMATIONS (GIF):")
    print("  {guide_key}_animation_{description}.gif")
    print()
    print("  Примеры:")
    print("    • character_training_diary_animation.gif")
    print("    • companion_beast_attack_animation.gif")
    print()
    
    print("SCREENSHOTS:")
    print("  {guide_key}_screen_{description}.png")
    print()
    print("  Примеры:")
    print("    • character_latent_power_screen_01.png")
    print("    • equipment_accessories_screen.png")
    print()

def analyze_and_report():
    """Проанализировать и вывести отчет"""
    
    media_by_type, media_by_guide = extract_media_urls()
    
    print("\n" + "=" * 80)
    print("СТАТИСТИКА МЕДИА ФАЙЛОВ")
    print("=" * 80)
    print()
    
    total_media = sum(len(v) for v in media_by_type.values())
    print(f"Всего медиа ссылок: {total_media}")
    print(f"Категории типов: {list(media_by_type.keys())}")
    print()
    
    for file_type, items in sorted(media_by_type.items()):
        print(f"  • {file_type.upper()}: {len(items)} файлов")
    print()
    
    print("ГАЙДЫ С НАИБОЛЬШИМ КОЛИЧЕСТВОМ МЕДИА:")
    print("-" * 80)
    
    sorted_guides = sorted(media_by_guide.items(), key=lambda x: len(x[1]), reverse=True)
    for guide, items in sorted_guides[:15]:
        print(f"  {guide:50} — {len(items):2} медиа файла(ов)")
    print()
    
    # Примеры URL
    print("=" * 80)
    print("ПРИМЕРЫ URL ФАЙЛОВ (ДЛЯ СКАЧИВАНИЯ):")
    print("=" * 80)
    print()
    
    for file_type in ['images', 'gif', 'videos']:
        if file_type in media_by_type and media_by_type[file_type]:
            print(f"\n{file_type.upper()} - Примеры:")
            for item in media_by_type[file_type][:3]:
                print(f"  🔗 {item['url'][:90]}")
                print(f"     └─ Гайд: {item['guide']}")
    print()

if __name__ == "__main__":
    print_structure_recommendation()
    analyze_and_report()
