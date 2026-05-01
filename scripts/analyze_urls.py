#!/usr/bin/env python3
"""
Детальный анализ неработающих ссылок в русских гайдах
"""

import re
import requests
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse
import time

def check_url_status(url, timeout=3):
    """Проверить доступность ссылки"""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code in [200, 301, 302]
    except:
        return False

def analyze_urls_in_guides():
    """Анализировать все ссылки в гайдах"""
    guides_dir = Path("guides/ru")
    
    url_stats = defaultdict(list)
    domain_stats = {}
    
    for md_file in guides_dir.rglob("*.md"):
        category = md_file.parent.name
        filename = md_file.name
        
        content = md_file.read_text(encoding='utf-8')
        urls = re.findall(r'https?://[^\s)]+', content)
        
        for url in urls:
            # Выжать домен
            parsed = urlparse(url)
            domain = parsed.netloc
            
            if domain not in domain_stats:
                domain_stats[domain] = {"count": 0, "working": 0}
            
            domain_stats[domain]["count"] += 1
            
            url_stats[domain].append({
                "file": f"{category}/{filename}",
                "url": url[:100],
            })
    
    print("Статистика ссылок по доменам:")
    print(f"{'='*60}")
    for domain, stats in sorted(domain_stats.items(), key=lambda x: -x[1]["count"]):
        print(f"{domain:40} | {stats['count']:3} ссылок")
    
    print(f"\nПримеры неработающих ссылок:")
    print(f"{'='*60}")
    
    # Проверить несколько ссылок на каждом домене
    for domain, urls_list in list(url_stats.items())[:3]:
        print(f"\n{domain}:")
        for item in urls_list[:2]:
            print(f"  {item['file']}")
            print(f"    {item['url']}")

def check_specific_urls():
    """Проверить конкретные типы ссылок"""
    test_urls = [
        "https://raw.githubusercontent.com/Nihronick/blackrose/main/assets/images/slayerpedia/image/constellation__1466470158058127493.png",
        "https://cdn.discordapp.com/attachments/1430546126129598504/1466470158058127493/image.png",
        "https://media.discordapp.net/attachments/1430546126129598504/1466470158058127493/image.png",
    ]
    
    print("Проверка доступные ссылок:")
    print(f"{'='*60}")
    
    for url in test_urls:
        try:
            # Простая проверка HEAD
            resp = requests.head(url, timeout=3, allow_redirects=True)
            status = f"✓ {resp.status_code}"
        except Exception as e:
            status = f"✗ {str(e)[:40]}"
        
        domain = urlparse(url).netloc
        print(f"{domain:40} | {status}")
        time.sleep(0.5)

if __name__ == "__main__":
    analyze_urls_in_guides()
    print("\n\nПроверка примеров ссылок:")
    check_specific_urls()
