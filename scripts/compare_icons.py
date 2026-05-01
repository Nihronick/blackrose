#!/usr/bin/env python3
"""
Создаёт HTML страницу для визуального сравнения дублирующихся иконок.
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from icons import ALL_ICONS

def find_duplicate_urls():
    """Найти иконки которые указывают на один и тот же URL"""
    url_to_keys = defaultdict(list)
    
    for key, url in ALL_ICONS.items():
        url_to_keys[url].append(key)
    
    duplicates = {url: keys for url, keys in url_to_keys.items() if len(keys) > 1}
    return duplicates

def generate_html():
    """Генерирует HTML для визуального сравнения"""
    duplicates = find_duplicate_urls()
    
    html = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Сравнение дублирующихся иконок</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f5f5;
            color: #333;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            margin-bottom: 10px;
            color: #222;
        }
        .stats {
            background: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .stats p {
            font-size: 14px;
            color: #666;
        }
        .duplicate-group {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .duplicate-group h3 {
            font-size: 14px;
            color: #666;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }
        .icon-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            align-items: flex-start;
        }
        .icon-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
            padding: 15px;
            background: #fafafa;
            border-radius: 8px;
            min-width: 150px;
            border: 2px solid #e0e0e0;
            transition: all 0.3s;
        }
        .icon-item:hover {
            border-color: #4CAF50;
            background: #f9fff9;
            box-shadow: 0 2px 8px rgba(76, 175, 80, 0.2);
        }
        .icon-preview {
            width: 80px;
            height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: white;
            border-radius: 4px;
            border: 1px solid #ddd;
            overflow: hidden;
        }
        .icon-preview img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }
        .icon-name {
            font-weight: 600;
            font-size: 13px;
            text-align: center;
            word-break: break-word;
            color: #222;
        }
        .icon-url {
            font-size: 11px;
            color: #999;
            text-align: center;
            max-width: 140px;
            word-break: break-all;
            font-family: monospace;
        }
        .url-section {
            margin-bottom: 15px;
            padding: 15px;
            background: #f0f0f0;
            border-radius: 4px;
            font-family: monospace;
            font-size: 12px;
            word-break: break-all;
            color: #555;
            border-left: 4px solid #4CAF50;
        }
        .keys-count {
            display: inline-block;
            background: #ff9800;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Визуальное сравнение иконок</h1>
        <p style="color: #999; margin-bottom: 20px;">Найденные точные дубликаты (один URL - несколько названий)</p>
        
        <div class="stats">
            <p><strong>📊 Всего иконок:</strong> {total_icons}</p>
            <p><strong>⚠️ Групп дубликатов:</strong> {duplicates_count}</p>
            <p><strong>🔗 Повторяющихся ссылок:</strong> {duplicate_urls_count}</p>
        </div>
"""
    
    for i, (url, keys) in enumerate(sorted(duplicates.items()), 1):
        if len(keys) < 2:
            continue
            
        html += f"""        <div class="duplicate-group">
            <h3>Группа #{i} <span class="keys-count">{len(keys)} ключей</span></h3>
            <div class="url-section">{url}</div>
            <div class="icon-container">
"""
        
        for key in sorted(keys):
            icon_url = ALL_ICONS[key]
            html += f"""                <div class="icon-item">
                    <div class="icon-preview">
                        <img src="{icon_url}" alt="{key}" onerror="this.parentElement.textContent='❌ Ошибка загрузки'">
                    </div>
                    <div class="icon-name">{key}</div>
                    <div class="icon-url">{icon_url[:80]}...</div>
                </div>
"""
        
        html += """            </div>
        </div>
"""
    
    html += """    </div>
</body>
</html>
"""
    
    # Заменяем плейсхолдеры
    total = len(ALL_ICONS)
    dup_count = len(duplicates)
    dup_url_count = sum(len(keys) for keys in duplicates.values())
    
    html = html.replace("{total_icons}", str(total))
    html = html.replace("{duplicates_count}", str(dup_count))
    html = html.replace("{duplicate_urls_count}", str(dup_url_count))
    
    return html

if __name__ == "__main__":
    output_file = Path(__file__).parent.parent / "icon_duplicates.html"
    html = generate_html()
    output_file.write_text(html, encoding='utf-8')
    print(f"✅ Создан файл: {output_file}")
    print(f"   Откройте в браузере: file://{output_file}")
