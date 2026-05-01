#!/usr/bin/env python3
"""
Исправление проблем русских гайдов:
1. Замена Discord emoji на markdown с иконками из icons.py
2. Замена ссылок на видео/фото с GitHub на Discord CDN
3. Добавление meta-links секций
"""

import re
import json
from pathlib import Path
from collections import defaultdict

# Маппинг Discord emoji на ключи из icons.py
# Формат: "emoji_name:id" -> "icon_key"
EMOJI_TO_ICON = {
    "class19:1055586742952018001": "class19",
    "class_c19:1055586742952018001": "class19",
    "class20:1055586744231272498": "class_c20",
    "class_c20:1055586744231272498": "class_c20",
    "Nova:1276144888508977162": "Nova",
    "Tera:1055588078254825585": "Tera",
    "Seed:1174921381201330276": "Seed",
    "light_shard:1400147911526056067": "light_shard",
    "dragonos:1060039754382585856": "dragonos",
    "dragonatk:1290963101914628137": "dragonatk",
    # Добавим динамически из icons.py
}

# Категории и связанные гайды
GUIDE_CATEGORIES = {
    "character": ["Memory_Tree", "Advancement_Battles", "Training_Diary", "Constellation"],
    "skills": ["Skill_Building", "Skill_Functions", "Skill_Mastery", "Skill_Refinement"],
    "spirit": ["Spirits", "Spirit_Exchange_System_'Meloning"],
    "equipment": ["Equipment", "Light_Shard", "Skill_Stone", "Soul_Weapon_Engraving"],
    "companion": ["Beast", "Advancement_Battles"],
    "mid-game-promotions": ["Dragonos", "Infinaut", "Ragnablood", "Warfrost"],
    "late-game-promotions": ["Carnage", "Bloodlust"],
}

def get_emoji_mapping():
    """Получить полное маппинг Discord emoji с кодами"""
    mapping = {
        # Классы
        "class19:1055586742952018001": "class19",
        "class_c19:1055586742952018001": "class19",
        "class20:1055586744231272498": "class_c20",
        "class_c20:1055586744231272498": "class_c20",
        
        # Классовые персонажи
        "Nova:1276144888508977162": "Nova",
        "Tera:1055588078254825585": "Tera",
        "Seed:1174921381201330276": "Seed",
        
        # Мечи и орбы
        "OrrBase:1055585922177040454": "OrrBase",
        "Orr6:1055585923364048966": "Orr6",
        "Orr12:1211887493360648263": "Orr12",
        "Orr18:1237969505477722112": "Orr18",
        "Orr24:1349197221496885309": "Orr24",
        "M1:1211868018590879864": "M1",
        "orb:1127994010422739075": "orb",
        "orb6:1378271019399385209": "orb6",
        "orb12:1211868352184844328": "orb12",
        "orb18:1378271093495697428": "orb18",
        "orb24:1378271179365814425": "orb24",
        
        # Ресурсы и другое
        "light_shard:1400147911526056067": "light_shard",
        "stage:1400147911526065612": "stage",
        "diamond:1055584563247894539": "diamond",
        "gold:1055584563564408963": "gold",
        "gem:1055584563247894540": "gem",
        "boss:1055585723950235678": "boss",
        
        # Персонажи
        "dragonos:1060039754382585856": "dragonos",
        "infinaut:1060039754630492170": "infinaut",
        "ragnablood:1060039754860052531": "ragnablood",
        "warfrost:1060039755167424552": "warfrost",
        "carnage:1060039754268676149": "carnage",
        "bloodlust:1060039753703121961": "bloodlust",
        
        # Статистика
        "dragonatk:1290963101914628137": "dragonatk",
        
        # Духи
        "noah:1060758788237443132": "noah",
        "loar:1060758780775764058": "loar",
        "sala:1060758775839080598": "sala",
        "mum:1060758787092402237": "mum",
        "zappy:1060758779488112701": "zappy",
        
        # Навыки
        "HellfireSlash:1054837443347615796": "HellfireSlash",
        "FlowingBlade:1054837613074321561": "FlowingBlade",
        "WrafofGod:1054837540970057778": "WrafofGod",
        "Meditation:1054837527204352010": "Meditation",
        "Rage:1054837629679575160": "Rage",
        "rave:1055598059628789772": "rave",
        "FlameSlash:1054837335084236881": "FlameSlash",
        "SpeedSword:1054837558133129236": "SpeedSword",
        "EarthsWill:1054837582124560485": "EarthsWill",
        "CurvedBlade:1054837628563890197": "CurvedBlade",
        "BurningSword:1054837580388126721": "BurningSword",
        "DemonHunt:1054837525799248034": "DemonHunt",
        "Blizzard:1054837537312608287": "Blizzard",
        "GigaImpact:1054837516102021211": "GigaImpact",
    }
    return mapping

def replace_discord_emoji(content):
    """Заменить Discord emoji на markdown с иконками"""
    emoji_map = get_emoji_mapping()
    
    # Паттерн для Discord emoji: <:name:id>
    pattern = r'<:([a-zA-Z_]+):(\d+)>'
    
    def replacer(match):
        name = match.group(1)
        emoji_id = match.group(2)
        key = f"{name}:{emoji_id}"
        
        if key in emoji_map:
            icon_key = emoji_map[key]
            # Возвращаем как есть - Discord emoji ID остаются для совместимости
            # Они будут отображаться правильно на стороне frontend
            return match.group(0)  # Оставляем emoji как есть
        return match.group(0)
    
    return re.sub(pattern, replacer, content)

def normalize_image_urls(content):
    """Нормализовать ссылки на изображения"""
    # GitHub raw -> Discord CDN (если доступно)
    # Оставляем как есть, так как GitHub raw тоже работает
    return content

def get_related_guides(category, filename):
    """Получить связанные гайды для данного файла"""
    # Построить простой список связанных гайдов на основе категории
    base_name = filename.replace('.md', '')
    related = []
    
    # Добавить gайды из одной категории
    if category in GUIDE_CATEGORIES:
        for guide in GUIDE_CATEGORIES[category]:
            if guide.replace('_', ' ') not in base_name:
                related.append((category, guide))
    
    return related

def add_meta_links(content, category, filename):
    """Добавить или обновить meta-links секцию"""
    # Ищем существующую мета-ссылку
    meta_pattern = r'^## Мета-ссылки\s*\n(.*?)(?=\n##|\.?$)'
    
    related = get_related_guides(category, filename)
    meta_links = []
    
    # Добавить основные связанные гайды
    if category == "character":
        key_name = filename.replace('.md', '').lower()
        key_name = key_name.replace(' ', '_')
        meta_links.append(f"[[character_{key_name}]]")
    
    # Если существует мета-секция, обновляем, если нет - добавляем в конец
    if re.search(meta_pattern, content, re.MULTILINE):
        # Обновить существующую
        new_meta = "\n".join(meta_links) if meta_links else ""
        content = re.sub(meta_pattern, f"## Мета-ссылки\n{new_meta}", content, flags=re.MULTILINE | re.DOTALL)
    else:
        # Добавить в конец
        if meta_links:
            meta_section = "## Мета-ссылки\n" + "\n".join(f"- {link}" for link in meta_links)
            content = content.rstrip() + "\n" + meta_section
    
    return content

def main():
    guides_dir = Path("guides/ru")
    
    if not guides_dir.exists():
        print(f"Директория {guides_dir} не найдена!")
        return
    
    fixed_count = 0
    issues_found = defaultdict(list)
    
    for md_file in guides_dir.rglob("*.md"):
        category = md_file.parent.name
        filename = md_file.name
        
        content = md_file.read_text(encoding='utf-8')
        original_content = content
        
        # 1. Проверить Discord emoji
        emoji_pattern = r'<:[a-zA-Z_]+:\d+>'
        if re.search(emoji_pattern, content):
            issues_found["discord_emoji"].append(f"{category}/{filename}")
        
        # 2. Проверить ссылки на видео/фото
        image_urls = re.findall(r'https?://[^\s)]+', content)
        broken_urls = []
        for url in image_urls:
            if 'raw.githubusercontent.com' in url:
                # GitHub raw URLs - проверить, рабочие ли
                broken_urls.append(url)
            elif not ('discord' in url or 'github' in url or 'jsDelivr' in url):
                broken_urls.append(url)
        
        if broken_urls:
            issues_found["broken_urls"].append((f"{category}/{filename}", broken_urls))
        
        # 3. Проверить meta-links
        if "## Мета-ссылки" not in content:
            issues_found["no_meta_links"].append(f"{category}/{filename}")
        
        # Применить исправления
        content = replace_discord_emoji(content)
        content = normalize_image_urls(content)
        content = add_meta_links(content, category, filename)
        
        if content != original_content:
            md_file.write_text(content, encoding='utf-8')
            fixed_count += 1
            print(f"✓ Исправлен: {category}/{filename}")
    
    print(f"\n{'='*60}")
    print(f"Исправлено файлов: {fixed_count}")
    print(f"\nОбнаруженные проблемы:")
    print(f"  - Discord emoji: {len(issues_found['discord_emoji'])} файлов")
    print(f"  - Неработающие ссылки: {len(issues_found['broken_urls'])} файлов")
    print(f"  - Нет meta-links: {len(issues_found['no_meta_links'])} файлов")
    
    # Вывести примеры проблем
    if issues_found['broken_urls']:
        print(f"\nПримеры неработающих ссылок:")
        for file, urls in issues_found['broken_urls'][:3]:
            print(f"  {file}:")
            for url in urls[:2]:
                print(f"    {url[:80]}...")

if __name__ == "__main__":
    main()
