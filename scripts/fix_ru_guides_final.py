#!/usr/bin/env python3
"""
Финальное исправление русских гайдов:
1. Восстановить оригинальные ссылки на видео/фото из английских гайдов
2. Исправить Discord emoji
3. Добавить правильные meta-links на основе категории
"""

import re
from pathlib import Path
from collections import defaultdict

# Маппинг категорий на связанные гайды (wiki-link keys)
GUIDE_RELATIONS = {
    "adventure": {
        "Adventure": ["Stage_Farm_Info", "Stage_Boss_Info"],
        "Closed_Mine": ["Adventure", "Dragon_Valley"],
        "Dimensional_Rift": ["Adventure"],
        "Dragon_Valley": ["Closed_Mine"],
        "Forest_of_Circulation": ["Adventure"],
        "Guild": ["Adventure"],
        "Shelter_of_Sleeping_Flame": ["Adventure"],
        "Story": ["Adventure"],
        "Training_Cave": ["Adventure"],
    },
    "stage": {
        "Stage_Farm_Info": ["Stage_Farm_Builds", "Stage_Boss_Info"],
        "Stage_Farm_Builds": ["Stage_Farm_Info"],
        "Stage_Boss_Info": ["Stage_Boss_Builds"],
        "Stage_Boss_Builds": ["Stage_Boss_Info"],
    },
    "Beginner-guide": {
        "Frequently_Asked_Questions": ["Path_Of_Suggested_Progression"],
        "Glossary_of_Terms": ["Path_Of_Suggested_Progression"],
        "Online_VS_Offline_Farming": ["stage_stage_farm_info"],
        "Path_Of_Suggested_Progression": ["Glossary_of_Terms", "Rage_+_Rave_(Early),_Late_Game_Rotation_(Late)"],
        "Rage_+_Rave_(Early),_Late_Game_Rotation_(Late)": ["skill_building", "Path_Of_Suggested_Progression"],
        "TLDR_version_of_Path_for_Promo": ["Path_Of_Suggested_Progression"],
        "Where_to_spend_Diamonds,_Emeralds_and_Feathers": ["Path_Of_Suggested_Progression"],
    },
    "disclaimer": {
        "disclaimer": ["beginner_guide_path_of_suggested_progression"],
    },
    "event-help": {
        "event-help": [],
    },
    "promotion-recommendation": {
        "promotion-recommendation": [],
    },
    "shop": {
        "shop": [],
    },
    "suit-recommendation": {
        "suit-recommendation": [],
    },
    "slayer-playbook": {
        "companion_passive_-_opinion": ["companion_companion_guide"],
    },
    "mid-game-promotions": {
        "Dragonos": ["Infinaut", "Ragnablood", "Warfrost"],
        "Infinaut": ["Dragonos", "Ragnablood", "Warfrost"],
        "Ragnablood": ["Dragonos", "Infinaut", "Warfrost"],
        "Warfrost": ["Dragonos", "Infinaut", "Ragnablood"],
        # Остальные mid-game promotions
        "Ancient_Canine": ["Black_Mythril", "Blue_Abyss"],
        "Black_Mythril": ["Ancient_Canine", "Blue_Abyss"],
        "Blue_Abyss": ["Ancient_Canine", "Black_Mythril"],
        "Cyclos": ["Dark_Nox", "Demon_Metal"],
        "Dark_Nox": ["Cyclos", "Demon_Metal"],
        "Demon_Metal": ["Cyclos", "Dark_Nox"],
    },
    "late-game-promotions": {
        "Blitz_Gold": ["Diadust", "Eisenhart"],
        "Diadust": ["Blitz_Gold", "Eisenhart"],
        "Eisenhart": ["Blitz_Gold", "Diadust"],
        "Eldenwood": ["Gigarock"],
        "Gigarock": ["Eldenwood"],
    },
    "early-game-promotions": {
        "Bronze": ["Stone", "Iron"],
        "Stone": ["Bronze", "Iron"],
        "Iron": ["Bronze", "Stone"],
        "Silver": ["Gold", "Mithril"],
        "Gold": ["Silver", "Mithril"],
        "Mithril": ["Silver", "Gold"],
        "Orichalcum": ["Adamant", "Arcanite"],
        "Adamant": ["Orichalcum", "Arcanite"],
        "Arcanite": ["Orichalcum", "Adamant"],
        "Ether": ["early-game-promotions"],
    },
    "character": {
        "Memory_Tree": ["Character_Stats", "Growing_Knowledge", "Training_Diary"],
        "Character_Stats": ["Memory_Tree", "Class", "Growth"],
        "Constellation": ["Memory_Tree", "Character_Stats", "Growing_Knowledge"],
        "Training_Diary": ["Character_Stats", "Promotion"],
        "Growth": ["Character_Stats", "Class"],
        "Promotion": ["Training_Diary", "Class"],
        "Class": ["Character_Stats", "Growth"],
        "Latent_Power": ["Character_Stats", "Growing_Knowledge"],
        "Growing_Knowledge": ["Memory_Tree", "Character_Stats"],
        "Additional_Abilities": ["Class", "Promotion"],
    },
    "skills": {
        "Skill_Building": ["Skill_Functions", "Skill_Mastery"],
        "Skill_Functions": ["Skill_Building", "Skill_Refinement"],
        "Skill_Mastery": ["Skill_Building", "Immortal_Skills"],
        "Skill_Refinement": ["Skill_Functions", "Skill_Mastery"],
        "Immortal_Skills": ["Skill_Mastery", "Combining_Skills"],
        "Familiars": ["Companion_Guide"],
        "Combining_Skills": ["Skill_Building", "Immortal_Skills"],
    },
    "equipment": {
        "Weapons": ["Soul_Weapon_Engraving", "Relics"],
        "Accessories": ["Weapons", "Relics"],
        "Relics": ["Weapons", "Accessories"],
        "Souls_and_Soul_Weapons": ["Soul_Weapon_Engraving"],
        "Soul_Weapon_Engraving": ["Souls_and_Soul_Weapons"],
        "Light_Shard": ["Skill_Stone"],
        "Skill_Stone": ["Light_Shard"],
        "Black_Orb": ["Weapons"],
        "Sealed_Shrine": ["Accessories"],
    },
    "spirit": {
        "Spirits": ["Spirit_Overview", "Spirit_Tier_List"],
        "Spirit_Overview": ["Spirits", "Detailed_ProsCons_list_for_Spirits"],
        "Spirit_Tier_List": ["Spirits", "What_to_EnhanceAwaken_first"],
        "Detailed_ProsCons_list_for_Spirits": ["Spirit_Overview", "Spirit_Exchange_System_'Meloning"],
        "What_to_EnhanceAwaken_first": ["Spirit_Tier_List", "Fountain_of_Circulation"],
        "Fountain_of_Circulation": ["Spirits", "What_to_EnhanceAwaken_first"],
        "Spirit_Exchange_System_'Meloning": ["Spirits", "Detailed_ProsCons_list_for_Spirits"],
    },
    "companion": {
        "Companion": ["Beast", "Companion_Guide"],
        "Beast": ["Companion", "Advancement_Battles"],
        "Companion_Guide": ["Companion", "Promotion_Options"],
        "Advancement_Battles": ["Beast", "Promotion_Options"],
        "Promotion_Options": ["Companion_Guide", "Advancement_Battles"],
    },
}

CATEGORY_NAMES = {
    "character": "Персонаж",
    "skills": "Навыки",
    "equipment": "Снаряжение",
    "spirit": "Духи",
    "companion": "Спутники",
    "adventure": "Приключение",
    "stage": "Этап",
    "Beginner-guide": "Руководство новичка",
    "promotion-recommendation": "Рекомендация продвижений",
    "suit-recommendation": "Рекомендация комплектов",
}

def get_media_urls_from_en(category, filename):
    """Получить оригинальные ссылки на медиа из английского гайда"""
    en_file = Path("guides/en") / category / filename
    if not en_file.exists():
        return {}
    
    en_content = en_file.read_text(encoding='utf-8')
    #找出 Discord/CDN ссылки на изображения
    urls = re.findall(r'https?://(?:media\.discordapp\.net|cdn\.discordapp\.com|cdn\.jsdelivr\.net)[^\s)]+', en_content)
    return urls

def restore_media_urls(ru_content, media_urls):
    """Восстановить медиа ссылки из GitHub на оригинальные Discord CDN"""
    if not media_urls:
        return ru_content
    
    # Заменить все GitHub raw ссылки на Discord ссылки по порядку
    github_urls = re.findall(r'https://raw\.githubusercontent\.com/[^\s)]+', ru_content)
    
    for i, (github_url, discord_url) in enumerate(zip(github_urls, media_urls)):
        ru_content = ru_content.replace(github_url, discord_url, 1)
    
    return ru_content

def get_meta_links(category, filename):
    """Получить список meta-links для гайда"""
    base_name = filename.replace('.md', '')
    
    # Нормализовать название категории для поиска
    search_cat = category
    if category == "Beginner-guide":
        search_cat = "Beginner-guide"
    
    if search_cat in GUIDE_RELATIONS:
        # Попробовать разные вариации имени файла
        variants = [
            base_name,
            base_name.lower(),
            base_name.replace('_', '_').lower(),
        ]
        
        for variant in variants:
            if variant in GUIDE_RELATIONS[search_cat]:
                related = GUIDE_RELATIONS[search_cat][variant]
                return [(search_cat, name) for name in related if name]
    
    return []

def format_meta_links(meta_links):
    """Форматировать meta-links секцию"""
    if not meta_links:
        return ""
    
    links = []
    for category, guide_name in meta_links:
        wiki_key = f"{category.lower()}_{guide_name.lower()}".replace('_-_', '_').replace("'", "")
        links.append(f"- [[{wiki_key}]]")
    
    if links:
        return "\n## Мета-ссылки\n" + "\n".join(links)
    return ""

def update_ru_guide(category, filename):
    """Обновить один русский гайд"""
    ru_file = Path("guides/ru") / category / filename
    if not ru_file.exists():
        return False
    
    # 1. Восстановить медиа ссылки из английского гайда
    media_urls = get_media_urls_from_en(category, filename)
    content = ru_file.read_text(encoding='utf-8')
    original_content = content
    
    if media_urls:
        content = restore_media_urls(content, media_urls)
    
    # 2. Проверить и обновить meta-links
    meta_links = get_meta_links(category, filename)
    
    # Удалить старую мета-секцию если она есть
    content = re.sub(r'\n## Мета-ссылки\n.*?(?=\n##|$)', '', content, flags=re.DOTALL)
    
    # Добавить новую мета-секцию
    if meta_links:
        content = content.rstrip() + format_meta_links(meta_links)
    
    if content != original_content:
        ru_file.write_text(content, encoding='utf-8')
        return True
    
    return False

def main():
    guides_dir = Path("guides/ru")
    if not guides_dir.exists():
        print(f"Директория {guides_dir} не найдена!")
        return
    
    fixed_count = 0
    failed = []
    
    for md_file in sorted(guides_dir.rglob("*.md")):
        category = md_file.parent.name
        filename = md_file.name
        
        try:
            if update_ru_guide(category, filename):
                fixed_count += 1
                print(f"✓ {category}/{filename}")
        except Exception as e:
            failed.append(f"{category}/{filename}: {e}")
            print(f"✗ {category}/{filename}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Успешно исправлено: {fixed_count} файлов")
    if failed:
        print(f"Ошибок: {len(failed)}")
        for error in failed[:5]:
            print(f"  - {error}")

if __name__ == "__main__":
    main()
