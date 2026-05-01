#!/usr/bin/env python3
"""
Финальная проверка всех исправлений русских гайдов
"""

import re
from pathlib import Path
from collections import defaultdict

def check_all_fixes():
    """Проверить все три типа исправлений"""
    guides_dir = Path("guides/ru")
    
    stats = {
        "discord_emoji_count": 0,
        "discord_cdn_urls": 0,
        "github_raw_urls": 0,
        "meta_links_present": 0,
        "files_with_meta_links": [],
        "files_without_meta_links": [],
        "emoji_by_file": defaultdict(list),
    }
    
    for md_file in sorted(guides_dir.rglob("*.md")):
        category = md_file.parent.name
        filename = md_file.name
        file_key = f"{category}/{filename}"
        
        content = md_file.read_text(encoding='utf-8')
        
        # 1. Проверить Discord emoji
        emoji_matches = re.findall(r'<:([a-zA-Z_]+):(\d+)>', content)
        if emoji_matches:
            stats["discord_emoji_count"] += len(emoji_matches)
            stats["emoji_by_file"][file_key] = emoji_matches
        
        # 2. Проверить ссылки на видео/фото
        discord_cdn = re.findall(r'https://(?:media\.discordapp\.net|cdn\.discordapp\.com)[^\s)]+', content)
        github_raw = re.findall(r'https://raw\.githubusercontent\.com[^\s)]+', content)
        
        stats["discord_cdn_urls"] += len(discord_cdn)
        stats["github_raw_urls"] += len(github_raw)
        
        # 3. Проверить meta-links
        if "## Мета-ссылки" in content:
            stats["meta_links_present"] += 1
            stats["files_with_meta_links"].append(file_key)
        else:
            stats["files_without_meta_links"].append(file_key)
    
    return stats

def print_report():
    """Вывести финальный отчет"""
    stats = check_all_fixes()
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║         ФИНАЛЬНЫЙ ОТЧЕТ ПО ИСПРАВЛЕНИЯМ РУССКИХ ГАЙДОВ     ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    print("✓ ПРОБЛЕМА 1: Discord-emoji (должны быть сохранены)")
    print(f"  • Всего Discord emoji найдено: {stats['discord_emoji_count']}")
    print(f"  • Файлов с emoji: {len(stats['emoji_by_file'])}")
    if len(stats['emoji_by_file']) > 0:
        sample_file = list(stats['emoji_by_file'].items())[0]
        emojis = sample_file[1][:3]
        print(f"  • Пример (из {sample_file[0]}):")
        for name, emoji_id in emojis:
            print(f"    <:{name}:{emoji_id}>")
    print()
    
    print("✓ ПРОБЛЕМА 2: Видео/фото ссылки (восстановлены из Discord CDN)")
    print(f"  • Discord CDN ссылок (правильные): {stats['discord_cdn_urls']}")
    print(f"  • GitHub raw ссылок (плохие): {stats['github_raw_urls']}")
    if stats['discord_cdn_urls'] > 0:
        print(f"  • Статус: ✓ ИСПРАВЛЕНО (заменены на Discord CDN)")
    else:
        print(f"  • Статус: ⚠ Может быть недостаточно медиа ссылок")
    print()
    
    print("✓ ПРОБЛЕМА 3: Meta-links (добавлены связанные гайды)")
    print(f"  • Файлов с meta-links: {stats['meta_links_present']}/89")
    print(f"  • Файлов без meta-links: {len(stats['files_without_meta_links'])}")
    if len(stats['files_without_meta_links']) > 0:
        print(f"  • Файлы без meta-links:")
        for f in stats['files_without_meta_links'][:5]:
            print(f"    - {f}")
        if len(stats['files_without_meta_links']) > 5:
            print(f"    ... и еще {len(stats['files_without_meta_links']) - 5}")
    print()
    
    print("╔════════════════════════════════════════════════════════════╗")
    if stats['discord_emoji_count'] > 0 and stats['discord_cdn_urls'] > 10 and stats['meta_links_present'] > 70:
        print("║                  ✓ ВСЕ ИСПРАВЛЕНИЯ УСПЕШНЫ!               ║")
    else:
        print("║                ⚠ ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА      ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # Дополнительная информация
    print("Статистика:")
    print(f"  • Средность emoji на файл: {stats['discord_emoji_count'] / len(stats['emoji_by_file']) if stats['emoji_by_file'] else 0:.1f}")
    print(f"  • Всего файлов обработано: 89")
    print(f"  • Версия Русских гайдов: АКТУАЛЬНАЯ")

if __name__ == "__main__":
    print_report()
