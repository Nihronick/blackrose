#!/usr/bin/env python3
"""
Import Russian guides from guides/ru into the database.
Usage: python scripts/import_ru_guides.py [--dry-run] [--category CATEGORY]
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from database import init_db, upsert_guide, set_guide_tags, close_pool, get_guide, get_category
from models import _validate_key
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

LANG_PREFIX = "ru_"

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
    "new_from_discord": "misc",
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


def namespace_key(key: str) -> str:
    return key if key.startswith(LANG_PREFIX) else f"{LANG_PREFIX}{key}"


def namespace_links(text: str) -> str:
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
        if not key.startswith(LANG_PREFIX):
            key = f"{LANG_PREFIX}{key}"
        suffix = f"|{label}" if label is not None else ""
        return f"[[{key}{suffix}]]"

    return re.sub(r"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]", replace_link, text)


async def import_ru_guides(dry_run: bool = False, filter_category: Optional[str] = None) -> dict:
    """Import Russian guides from guides/ru into database."""
    await init_db()
    
    ru_dir = Path("guides/ru")
    if not ru_dir.exists():
        print(f"[ERR] Directory not found: {ru_dir}")
        await close_pool()
        return {"error": "Directory not found"}
    
    stats = {
        "total": 0,
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0,
    }
    
    # Iterate through category directories
    for category_dir in sorted(ru_dir.iterdir()):
        if not category_dir.is_dir():
            continue
        
        dir_name = category_dir.name
        
        # Skip if filtering by category
        if filter_category and filter_category not in dir_name:
            continue
        
        cat_key = namespace_key(CATEGORY_MAP.get(dir_name, dir_name.replace("-", "_")))
        
        # Verify category exists
        existing_cat = await get_category(cat_key)
        if not existing_cat:
            print(f"[WARN] Category not found in DB: {cat_key} (directory: {dir_name})")
            stats["skipped"] += 1
            continue
        
        print(f"\n[PROCESS] Category: {dir_name} -> {cat_key}")
        
        # Iterate through markdown files
        for md_file in sorted(category_dir.glob("*.md")):
            stats["total"] += 1
            guide_key = namespace_key(normalize_key(dir_name, md_file.name))
            
            try:
                content = md_file.read_text(encoding='utf-8')
                content = namespace_links(content)
                
                # Extract title from filename
                title = md_file.stem.replace("_", " ").replace("-", " ")
                
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
                    await set_guide_tags(guide_key, [cat_key])
                    
                    if existing:
                        stats["updated"] += 1
                        print(f"  [UPDATE] {guide_key}")
                    else:
                        stats["created"] += 1
                        print(f"  [CREATE] {guide_key}")
                else:
                    if existing:
                        print(f"  [DRY-UPDATE] {guide_key}")
                        stats["updated"] += 1
                    else:
                        print(f"  [DRY-CREATE] {guide_key}")
                        stats["created"] += 1
                        
            except Exception as e:
                stats["errors"] += 1
                print(f"  [ERROR] {md_file.name}: {e}")
    
    await close_pool()
    return stats


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Import Russian guides into database")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--category", type=str, help="Filter by category name")
    args = parser.parse_args()
    
    print("[IMPORT] Starting Russian guides import...")
    print(f"   Dry run: {args.dry_run}")
    if args.category:
        print(f"   Filter category: {args.category}")
    
    stats = await import_ru_guides(dry_run=args.dry_run, filter_category=args.category)
    
    print("\n" + "="*60)
    print("[SUMMARY] Import Summary:")
    print(f"   Total processed: {stats['total']}")
    print(f"   Created: {stats['created']}")
    print(f"   Updated: {stats['updated']}")
    print(f"   Skipped: {stats['skipped']}")
    print(f"   Errors: {stats['errors']}")
    print("="*60)
    
    if stats.get("error"):
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
