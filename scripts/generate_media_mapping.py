#!/usr/bin/env python3
"""
Подробный маппинг всех медиа-файлов с рекомендованными локальными путями
"""

import re
from pathlib import Path
from urllib.parse import urlparse
from collections import defaultdict

def generate_local_filename(url, guide_key, media_index):
    """Сгенерировать локальное имя файла"""
    
    # Определить расширение
    parsed = urlparse(url)
    path = parsed.path.lower()
    
    if path.endswith('.gif'):
        ext = 'gif'
    elif path.endswith(('.png', '.jpg', '.jpeg')):
        ext = 'png'
    elif path.endswith('.webp'):
        ext = 'webp'
    elif path.endswith(('.mp4', '.webm', '.mov')):
        ext = path.split('.')[-1].split('?')[0]
    else:
        ext = 'unknown'
    
    # Норнализовать guide_key
    guide_name = guide_key.replace('/', '_').replace(' ', '_').lower()
    guide_name = re.sub(r'[^\w_]', '_', guide_name)
    guide_name = re.sub(r'_+', '_', guide_name).strip('_')
    
    # Определить тип
    if ext == 'gif':
        file_type = 'animations'
        filename = f"{guide_name}_animation_{media_index:02d}.{ext}"
    elif ext in ['mp4', 'webm', 'mov']:
        file_type = 'videos'
        filename = f"{guide_name}_video_{media_index:02d}.{ext}"
    else:
        file_type = 'images'
        filename = f"{guide_name}_{media_index:02d}.{ext}"
    
    return f"media/guides/{file_type}/{filename}", filename

def generate_mapping():
    """Сгенерировать полный маппинг"""
    
    media_map = {}  # url -> local_path
    media_by_guide = defaultdict(list)  # guide -> list of (url, local_path)
    
    guides_dir = Path("guides/ru")
    
    for md_file in sorted(guides_dir.rglob("*.md")):
        category = md_file.parent.name
        filename = md_file.name
        guide_key = f"{category}_{filename.replace('.md', '')}"
        
        content = md_file.read_text(encoding='utf-8')
        urls = re.findall(r'https://(?:media\.discordapp\.net|cdn\.discordapp\.com|cdn\.jsdelivr\.net)[^\s)]+', content)
        
        for idx, url in enumerate(urls, 1):
            local_path, filename = generate_local_filename(url, guide_key, idx)
            media_map[url] = local_path
            media_by_guide[f"{category}/{md_file.name}"].append((url, local_path, filename))
    
    return media_map, media_by_guide

def print_mapping():
    """Вывести маппинг в красивом формате"""
    
    media_map, media_by_guide = generate_mapping()
    
    print("=" * 100)
    print("ПОЛНЫЙ МАППИНГ МЕДИА ФАЙЛОВ (URL → Локальный путь)")
    print("=" * 100)
    print()
    
    # Структурированный вывод по категориям
    categories = defaultdict(list)
    for guide_key in sorted(media_by_guide.keys()):
        cat = guide_key.split('/')[0]
        if media_by_guide[guide_key]:
            categories[cat].append((guide_key, media_by_guide[guide_key]))
    
    for cat in sorted(categories.keys()):
        print(f"\n📁 {cat.upper()}")
        print("─" * 100)
        
        for guide_key, items in categories[cat]:
            short_guide = guide_key.split('/')[-1]
            print(f"\n  📄 {short_guide}")
            
            for url, local_path, filename in items:
                # Сократить URL для облегчения чтения
                short_url = url[:70] + "..." if len(url) > 70 else url
                print(f"    📥 {short_url}")
                print(f"    💾 → {local_path}")
                print()

def save_mapping_csv():
    """Сохранить маппинг в CSV для использования в скрипте замены"""
    
    media_map, _ = generate_mapping()
    
    csv_content = "url,local_path\n"
    for url in sorted(media_map.keys()):
        local_path = media_map[url]
        # Экранировать кавычки
        url_escaped = url.replace('"', '""')
        csv_content += f'"{url_escaped}","{local_path}"\n'
    
    Path("scripts/media_mapping.csv").write_text(csv_content, encoding='utf-8')
    print(f"\n✅ Маппинг сохранён в scripts/media_mapping.csv ({len(media_map)} файлов)")

if __name__ == "__main__":
    print_mapping()
    save_mapping_csv()
