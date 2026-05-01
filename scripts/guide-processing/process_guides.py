#!/usr/bin/env python3
"""
ЭТАП 0-4: Обработка гайдов для Neon BD
1. Анализ icons.py → glossary.json
2. Сканирование гайдов (EN + RU)
3. Подготовка метаданных
4. Генерация import.sql
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import sys

# ═══════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).parent
GUIDES_DIR = PROJECT_ROOT / "guides"
OUTPUT_DIR = PROJECT_ROOT / "output_neon"
OUTPUT_DIR.mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════
# ФУНКЦИИ АН АНАЛИЗА ICONS.PY
# ═══════════════════════════════════════════════════════

def extract_no_translate():
    """Извлекает no_translate лист из icons.py"""
    no_translate = set()
    
    # SKILLS категория
    skills = [
        "Agile", "Blizzard", "BurningSword", "CurvedBlade", "DancingWaves",
        "DemonHunt", "EarthsWill", "FireBlast", "FireSword", "FlameSlash",
        "FlameWave", "FlowingBlade", "Fulgurous", "GigaImpact", "GigaStrike",
        "GroundsBlessing", "HellfireSlash", "HotBlast", "IceShower", "IceTime",
        "IronWill", "LifeMana", "LightningStroke", "LightningBody", "ManasBlessing",
        "Mantra", "Meditation", "PillarOfFire", "PowerImpact", "PowerStrike",
        "Rage", "Rave", "RedLightning", "SpeedSword", "StrongCurrent",
        "Supersonic", "ThunderboltSlash", "ThunderSlash", "WarriorBurn", "WaterSlash",
        "WindSword", "WrathOfGods", "FireSlash", "IceStone", "LightningSlash"
    ]
    
    # SPIRIT категория (духи и фамильяры)
    spirits = [
        "noah", "loar", "sala", "mum", "bo", "radon", "zappy", "kart", "herh", "todd", "luga", "ark",
        "hi", "je", "ku", "a", "leon", "mus", "na", "pe", "po", "ru", "sha", "ti"
    ]
    
    # PROMOTION категория
    promotions = [
        "adamant", "ether", "black_mithril", "demonite", "dragonos", "blood", "frost",
        "nox", "abyss", "infinat", "cyclone", "ancient", "gigalor", "arcanite", "stone",
        "silver", "orichalcum", "gold", "iron", "bronze", "diadust", "eisenhart", "Eldenwood", "mithrill"
    ]
    
    # CLASSES категория
    classes = ["Tera", "Nova", "Seed", "C17", "C18", "C19", "C20"]
    
    for skill in skills:
        no_translate.add(skill)
    for spirit in spirits:
        no_translate.add(spirit)
    for promo in promotions:
        no_translate.add(promo)
    for cls in classes:
        no_translate.add(cls)
    
    return sorted(list(no_translate))


def extract_icons_mapping():
    """Извлекает маппинг иконок"""
    icons_map = {}
    
    # Основные ключи из icons.py
    class_etc_keys = [
        "class_c17", "class_c18", "class_c19", "class_terra", "class_nova", "class_sid",
        "mythic1", "OrrBase", "Orr6", "Orr12", "Orr18", "Orr24", "M1",
        "orb", "orb6", "orb12", "orb18", "orb24", "sword_m1", "sword_opp", "sword_orb",
        "sword_awaken", "sword_absolutev1", "sword_absolutev2", "sword_immortal",
        "memory_tree", "eq", "all", "msg", "luna", "ellie", "miho", "zeke",
        "soul_sword", "acc", "ds", "atk", "crit", "crit2", "hp", "hpr",
        "diamond", "gold", "gem", "earth", "fire", "water", "wind", "farm",
        "pero_viol", "pero_berez", "boss", "BR", "cock", "cum", "dig", "raid", "relic"
    ]
    
    skills_keys = [
        "Agile", "Blizzard", "BurningSword", "CurvedBlade", "DancingWaves", "DemonHunt",
        "EarthsWill", "FireBlast", "FireSword", "FlameSlash", "FlameWave", "FlowingBlade",
        "Fulgurous", "GigaImpact", "GigaStrike", "GroundsBlessing", "HellfireSlash",
        "HotBlast", "IceShower", "IceTime", "IronWill", "LifeMana", "LightningStroke",
        "LightningBody", "ManasBlessing", "Mantra", "Meditation", "PillarOfFire",
        "PowerImpact", "PowerStrike", "Rage", "Rave", "RedLightning", "SpeedSword",
        "StrongCurrent", "Supersonic", "ThunderboltSlash", "ThunderSlash", "WarriorBurn",
        "WaterSlash", "WindSword", "WrathOfGods", "FireSlash", "IceStone", "LightningSlash"
    ]
    
    spirit_keys = [
        "noah", "loar", "sala", "mum", "bo", "radon", "zappy", "kart", "herh", "todd", "luga", "ark",
        "hi", "je", "ku", "a", "leon", "mus", "na", "pe", "po", "ru", "sha", "ti"
    ]
    
    for key in class_etc_keys + skills_keys + spirit_keys:
        icons_map[key] = f"{{{{icon_{key}}}}}"
    
    return icons_map


def scan_guides() -> Dict[str, List[Tuple[str, Path]]]:
    """Сканирует гайды EN и RU, возвращает {lang: [(category, path), ...]}"""
    guides = {}
    
    for lang in ["en", "ru"]:
        lang_dir = GUIDES_DIR / lang
        if not lang_dir.exists():
            continue
        
        guides[lang] = []
        for category_dir in sorted(lang_dir.iterdir()):
            if not category_dir.is_dir():
                continue
            
            for guide_file in sorted(category_dir.glob("*.md")):
                guides[lang].append((category_dir.name, guide_file))
    
    return guides


def extract_media_links(content: str) -> Set[str]:
    """Извлекает all media URLs из контенты"""
    media_urls = set()
    
    # Discord CDN
    discord_pattern = r'(https?://(?:cdn|media)\.discord(?:app)?\.(?:com|net)/[^\s\)"\']*)(?:\.[a-z]{2,4})?'
    media_urls.update(re.findall(discord_pattern, content))
    
    # Direct media extensions
    media_pattern = r'(https?://[^\s\)\"\']*\.(?:png|jpg|jpeg|gif|webp|mp4|webm|mov|mkv))'
    media_urls.update(re.findall(media_pattern, content, re.IGNORECASE))
    
    # Image previews
    preview_pattern = r'(https?://(?:i\.ytimg|imgur|tenor)\.com[^\s\)\"\']*)'
    media_urls.update(re.findall(preview_pattern, content))
    
    # Markdown images
    markdown_img = r'\!\[([^\]]*)\]\(([^\)]*(?:png|jpg|jpeg|gif|webp|mp4|webm|mov))\)'
    media_urls.update([match[1] for match in re.findall(markdown_img, content, re.IGNORECASE)])
    
    return media_urls


def normalize_link_label(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def alias_variants(alias: str) -> set[str]:
    variants: set[str] = set()
    if not alias:
        return variants

    variants.add(alias)

    for prefix in ("the_", "a_", "an_"):
        if alias.startswith(prefix):
            variants.add(alias[len(prefix) :])

    if alias.endswith("ies") and len(alias) > 4:
        variants.add(alias[:-3] + "y")
    if alias.endswith("es") and len(alias) > 3:
        variants.add(alias[:-2])
    if alias.endswith("s") and len(alias) > 2:
        variants.add(alias[:-1])

    return {v.strip("_") for v in variants if v.strip("_")}


def resolve_key(label: str, alias_to_key: dict[str, str]) -> str | None:
    base = normalize_link_label(label)
    for candidate in alias_variants(base):
        key = alias_to_key.get(candidate)
        if key:
            return key
    return None


def build_guide_key_lookup() -> tuple[dict[Path, str], dict[str, str]]:
    path_to_key: dict[Path, str] = {}
    alias_to_key: dict[str, str] = {}

    for lang in ["en", "ru"]:
        lang_dir = GUIDES_DIR / lang
        if not lang_dir.exists():
            continue

        for category_dir in sorted(lang_dir.iterdir()):
            if not category_dir.is_dir():
                continue

            for guide_file in sorted(category_dir.glob("*.md")):
                key = f"{category_dir.name}_{guide_file.stem}".lower()
                key = re.sub(r"[^a-z0-9]+", "_", key)
                key = re.sub(r"_+", "_", key).strip("_")
                resolved = guide_file.resolve()
                path_to_key[resolved] = key
                for alias in {
                    normalize_link_label(guide_file.stem.replace("_", " ")),
                    normalize_link_label(guide_file.stem.replace("-", " ")),
                }:
                    for variant in alias_variants(alias):
                        alias_to_key.setdefault(variant, key)

    return path_to_key, alias_to_key


def rewrite_internal_links(
    content: str, current_file: Path, path_to_key: dict[Path, str], alias_to_key: dict[str, str]
) -> tuple[str, list[str]]:
    meta_links: list[str] = []

    def remember(key: str) -> None:
        if key and key not in meta_links:
            meta_links.append(key)

    def replace_wikilink(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        label = (match.group(2) or "").strip()
        remember(key)
        return match.group(0) if not label else f"[[{key}|{label}]]"

    content = re.sub(r"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]", replace_wikilink, content)

    def replace_markdown_link(match: re.Match[str]) -> str:
        label = match.group(1).strip()
        target = match.group(2).strip()

        if target.startswith(("http://", "https://")):
            key = resolve_key(label, alias_to_key)
            if key:
                remember(key)
                return f"[[{key}|{label}]]"
            return match.group(0)

        if target.endswith(".md"):
            resolved = (current_file.parent / target).resolve()
            key = path_to_key.get(resolved)
            if key:
                remember(key)
                return f"[[{key}|{label}]]"

        return match.group(0)

    content = re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", replace_markdown_link, content)
    return content, meta_links


def extract_icon_references(content: str) -> List[str]:
    """Извлекает все {{icon_name}} из контента"""
    pattern = r'\{\{(\w+)\}\}'
    return re.findall(pattern, content)


def process_guide_file(
    file_path: Path,
    lang: str,
    category: str,
    path_to_key: dict[Path, str],
    alias_to_key: dict[str, str],
) -> Dict:
    """Обрабатывает один гайд файл"""
    content_md = file_path.read_text(encoding="utf-8")
    content_md, meta_links = rewrite_internal_links(
        content_md, file_path, path_to_key, alias_to_key
    )
    guide_name = file_path.stem
    
    # Конвертируем Markdown в plain text (примитивно)
    content_text = re.sub(
        r'\[\[([^\]|]+)(?:\|([^\]]*))?\]\]',
        lambda m: m.group(2) or m.group(1),
        content_md,
    )
    content_text = re.sub(r'[#*_[\]`~\-\+\|]', '', content_text)
    content_text = re.sub(r'\n\n+', '\n', content_text).strip()
    
    # Извлекаем метаданные
    icons_used = extract_icon_references(content_md)
    media_links = list(extract_media_links(content_md))
    
    return {
        "lang": lang,
        "category": category,
        "guide_name": guide_name,
        "content_md": content_md,
        "content_text": content_text,
        "icons_used": icons_used,
        "media_links": media_links,
        "meta_links": meta_links
    }


def generate_glossary(no_translate: List[str]) -> Dict:
    """Генерирует glossary.json"""
    icons_mapping = extract_icons_mapping()
    
    glossary = {
        "terms": {
            "skill": "навык",
            "promotion": "промоут",
            "spirit": "дух",
            "companion": "спутник",
            "sword": "меч",
            "class": "класс"
        },
        "abbreviations": {
            "DH": "Демонхант (DH)",
            "WB": "Боевой урон (WB)",
            "LB": "Грозовое тело (LB)",
            "HP": "Здоровье (HP)",
            "ATK": "Атака (ATK)",
            "CRIT": "Крит урон (CRIT)",
            "ACC": "Точность (ACC)",
            "DS": "Смертельный удар (DS)"
        },
        "icons": icons_mapping,
        "no_translate": no_translate,
        "categories": {
            "SKILLS": sorted(extract_no_translate()),  # Все навыки отсюда
            "SPIRITS": ["noah", "loar", "sala", "mum", "bo", "radon", "zappy", "kart", "herh", "todd", "luga", "ark"],
            "PROMOTIONS": ["adamant", "ether", "black_mithril", "demonite", "dragonos", "blood", "frost", "nox", "abyss", "infinat", "cyclone"],
            "CLASSES": ["Tera", "Nova", "Seed"]
        }
    }
    
    return glossary


# ═══════════════════════════════════════════════════════
# ОСНОВНАЯ ОБРАБОТКА
# ═══════════════════════════════════════════════════════

def main():
    print("🔹 ЭТАП 0: АНАЛИЗ icons.py...")
    no_translate = extract_no_translate()
    print(f"   ✓ Извлечено {len(no_translate)} терминов no_translate")
    print(f"   Примеры: {', '.join(no_translate[:10])}")
    
    print("\n🔹 ЭТАП 1: СОЗДАНИЕ glossary.json...")
    glossary = generate_glossary(no_translate)
    glossary_path = OUTPUT_DIR / "glossary.json"
    glossary_path.write_text(json.dumps(glossary, ensure_ascii=False, indent=2))
    print(f"   ✓ Сохранено: {glossary_path}")
    print(f"   - Иконок в маппинге: {len(glossary['icons'])}")
    print(f"   - Сокращений: {len(glossary['abbreviations'])}")
    
    print("\n🔹 ЭТАП 2: СКАНИРОВАНИЕ ГАЙДОВ...")
    guides = scan_guides()
    path_to_key, alias_to_key = build_guide_key_lookup()
    
    all_guides_data = []
    for lang in sorted(guides.keys()):
        print(f"\n   📍 {lang.upper()}:")
        for category, file_path in guides[lang]:
            guide_data = process_guide_file(
                file_path, lang, category, path_to_key, alias_to_key
            )
            all_guides_data.append(guide_data)
            print(f"      ✓ {category}/{file_path.stem} - {len(guide_data['icons_used'])} иконок, {len(guide_data['media_links'])} медиа")
    
    print(f"\n   📊 ИТОГО: {len(all_guides_data)} гайдов обработано")
    
    # Статистика
    print("\n🔹 ЭТАП 3: СТАТИСТИКА...")
    total_icons_used = set()
    total_media = set()
    
    for guide in all_guides_data:
        total_icons_used.update(guide["icons_used"])
        total_media.update(guide["media_links"])
    
    print(f"   - Уникальных иконок использовано: {len(total_icons_used)}")
    print(f"   - Уникальных медиа-ссылок: {len(total_media)}")
    print(f"   - Языков: {len(guides)}")
    
    # Сохраняем данные для ЭТАПА 4
    guides_data_path = OUTPUT_DIR / "guides_processed.json"
    guides_data_path.write_text(json.dumps(all_guides_data, ensure_ascii=False, indent=2))
    print(f"   ✓ Сохранены метаданные: {guides_data_path}")
    
    # Медиа отчёт
    media_report = {
        "total_unique": len(total_media),
        "media_links": sorted(list(total_media)),
        "by_type": {
            "discord_cdn": len([m for m in total_media if "discord" in m]),
            "images": len([m for m in total_media if re.search(r'\.(png|jpg|jpeg|gif|webp)$', m, re.I)]),
            "videos": len([m for m in total_media if re.search(r'\.(mp4|webm|mov)$', m, re.I)]),
            "previews": len([m for m in total_media if any(h in m for h in ["ytimg", "imgur", "tenor"])])
        }
    }
    
    media_report_path = OUTPUT_DIR / "media_report.json"
    media_report_path.write_text(json.dumps(media_report, ensure_ascii=False, indent=2))
    print(f"   ✓ Медиа отчёт: {media_report_path}")
    
    print("\n✅ ЭТАПЫ 0-3 ЗАВЕРШЕНЫ!")
    print(f"📂 Выходная папка: {OUTPUT_DIR}\n")
    
    return all_guides_data, glossary, media_report


if __name__ == "__main__":
    main()
