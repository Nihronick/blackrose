#!/usr/bin/env python3
"""
Full guide database refresh: imports all guides from guides/en and guides/ru.
Usage: python scripts/refresh_guides_db.py [--en-only] [--ru-only]
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from database import init_db, upsert_guide, set_guide_tags, close_pool, get_guide, get_category
from utils import normalize_icon_syntax
from models import _validate_key
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

RU_PREFIX = "ru_"

# Category mappings
CATEGORY_MAP = {
    "beginner-guide": "beginners_guide",
    "Beginner-guide": "beginners_guide",
    "character": "character",
    "spirit": "spirits",
    "companion": "companion",
    "equipment": "equipment",
    "early-game-promotions": "early_game_promotions",
    "mid-game-promotions": "mid_game_promotions",
    "late-game-promotions": "late_game_promotions",
    "event-help": "event_help",
    "shop": "shop",
    "skills": "skills",
    "stage": "stage",
    "slayer-playbook": "slayer_playbook",
    "suit-recommendation": "suit_recommendation",
    "promotion-recommendation": "promotion_recommendation",
    "disclaimer": "disclaimer",
    "new_from_discord": "misc",
    "adventure": "adventure",
}


def normalize_key(category_dir: str, filename: str) -> str:
    """Generate a normalized key from category and filename."""
    key = f"{category_dir}_{filename.replace('.md', '')}".lower().replace("-", "_")
    try:
        _validate_key(key)
        return key
    except Exception:
        # If key is too long, try to shorten it
        return key[:64]


def namespace_key(key: str, language: str) -> str:
    if language == "ru":
        return key if key.startswith(RU_PREFIX) else f"{RU_PREFIX}{key}"
    return key[len(RU_PREFIX):] if key.startswith(RU_PREFIX) else key


def namespace_links(text: str, language: str) -> str:
    import re

    def replace_link(match):
        key_part = match.group(1).strip()
        label_part = match.group(2)
        if "|" in key_part:
            key, label = key_part.split("|", 1)
        else:
            key = key_part
            label = label_part
        key = key.strip().replace("-", "_")
        if language == "ru" and not key.startswith(RU_PREFIX):
            key = f"{RU_PREFIX}{key}"
        elif language != "ru" and key.startswith(RU_PREFIX):
            key = key[len(RU_PREFIX):]
        suffix = f"|{label}" if label is not None else ""
        return f"[[{key}{suffix}]]"

    return re.sub(r"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]", replace_link, text)


def extract_title_from_content(content: str, fallback_title: str) -> str:
    """Extract title from markdown content. First non-empty line is used as title."""
    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        # Skip empty lines and markdown headers/formatting
        if line and not line.startswith('#') and not line.startswith('*') and not line.startswith('-'):
            # Clean up inline formatting
            title = line.replace('**', '').replace('_', '').strip()
            if title and len(title) > 0:
                return title
    return fallback_title


async def import_guides_from_dir(
    guides_dir: Path,
    language: str,
    dry_run: bool = False
) -> dict:
    """Import guides from specified directory (en or ru)."""
    
    if not guides_dir.exists():
        print(f"[ERR] Directory not found: {guides_dir}")
        return {"error": "Directory not found"}
    
    stats = {
        "total": 0,
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0,
    }
    
    lang_label = "EN" if language == "en" else "RU"
    print(f"\n{'='*60}")
    print(f"[{lang_label}] Importing guides from {guides_dir}")
    print(f"{'='*60}")
    
    # Iterate through category directories
    for category_dir in sorted(guides_dir.iterdir()):
        if not category_dir.is_dir():
            continue
        
        dir_name = category_dir.name
        cat_key = namespace_key(CATEGORY_MAP.get(dir_name, dir_name.replace("-", "_")), language)
        
        # Verify category exists
        existing_cat = await get_category(cat_key)
        if not existing_cat:
            print(f"[WARN] Category not found in DB: {cat_key} (directory: {dir_name})")
            stats["skipped"] += len(list(category_dir.glob("*.md")))
            continue
        
        print(f"\n[{lang_label}] {dir_name} -> {cat_key}")
        
        # Iterate through markdown files
        for md_file in sorted(category_dir.glob("*.md")):
            stats["total"] += 1
            guide_key = namespace_key(normalize_key(dir_name, md_file.name), language)
            
            try:
                content = md_file.read_text(encoding='utf-8')
                
                # Normalize icon syntax
                content = normalize_icon_syntax(content)
                content = namespace_links(content, language)
                
                # Extract title from content for Russian guides, fallback to filename
                fallback_title = md_file.stem.replace("_", " ").replace("-", " ")
                if language == "ru":
                    title = extract_title_from_content(content, fallback_title)
                else:
                    title = fallback_title
                
                # Check if guide already exists
                existing = await get_guide(guide_key)
                
                if not dry_run:
                    await upsert_guide(
                        key=guide_key,
                        category_key=cat_key,
                        title=title,
                        icon_url=None,
                        text=content,
                        photo=[],
                        video=[],
                        document=[],
                        sort_order=0,
                        changed_by=0  # System import
                    )
                    
                    # Set basic tags
                    await set_guide_tags(guide_key, [cat_key, language])
                    
                    if existing:
                        stats["updated"] += 1
                        print(f"  ✏️  {guide_key}")
                    else:
                        stats["created"] += 1
                        print(f"  ✨ {guide_key}")
                else:
                    if existing:
                        print(f"  [DRY] UPDATE: {guide_key}")
                        stats["updated"] += 1
                    else:
                        print(f"  [DRY] CREATE: {guide_key}")
                        stats["created"] += 1
                        
            except Exception as e:
                stats["errors"] += 1
                print(f"  ❌ {md_file.name}: {e}")
    
    return stats


async def refresh_guides(
    dry_run: bool = False,
    en_only: bool = False,
    ru_only: bool = False
) -> dict:
    """Refresh all guides in database."""
    await init_db()
    
    total_stats = {
        "en": {"total": 0, "created": 0, "updated": 0, "skipped": 0, "errors": 0},
        "ru": {"total": 0, "created": 0, "updated": 0, "skipped": 0, "errors": 0},
    }
    
    # Import EN guides
    if not ru_only:
        en_dir = Path("guides/en")
        en_stats = await import_guides_from_dir(en_dir, "en", dry_run)
        total_stats["en"] = en_stats
    
    # Import RU guides
    if not en_only:
        ru_dir = Path("guides/ru")
        ru_stats = await import_guides_from_dir(ru_dir, "ru", dry_run)
        total_stats["ru"] = ru_stats
    
    await close_pool()
    return total_stats


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Refresh all guides in database")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--en-only", action="store_true", help="Import only English guides")
    parser.add_argument("--ru-only", action="store_true", help="Import only Russian guides")
    args = parser.parse_args()
    
    if args.en_only and args.ru_only:
        print("[ERR] Cannot use --en-only and --ru-only together")
        sys.exit(1)
    
    print("[REFRESH] Starting database refresh...")
    print(f"   Dry run: {args.dry_run}")
    if args.en_only:
        print("   Language: EN only")
    elif args.ru_only:
        print("   Language: RU only")
    else:
        print("   Language: EN + RU")
    
    stats = await refresh_guides(
        dry_run=args.dry_run,
        en_only=args.en_only,
        ru_only=args.ru_only
    )
    
    print("\n" + "="*60)
    print("[SUMMARY] Database Refresh Summary")
    print("="*60)
    
    for lang, data in stats.items():
        if data.get("error"):
            print(f"\n[{lang.upper()}] ERROR: {data['error']}")
            continue
        
        if data["total"] == 0:
            continue
        
        print(f"\n[{lang.upper()}]")
        print(f"   Total: {data['total']}")
        print(f"   Created: {data['created']}")
        print(f"   Updated: {data['updated']}")
        print(f"   Skipped: {data['skipped']}")
        print(f"   Errors: {data['errors']}")
    
    grand_total = sum(d.get("total", 0) for d in stats.values() if d.get("total"))
    grand_created = sum(d.get("created", 0) for d in stats.values())
    grand_updated = sum(d.get("updated", 0) for d in stats.values())
    
    print("\n" + "="*60)
    print(f"[TOTAL] {grand_total} guides | {grand_created} created | {grand_updated} updated")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
