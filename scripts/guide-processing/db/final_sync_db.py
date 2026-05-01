import asyncio
import os
import re
import sys
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[3]

# Add backend to path
sys.path.append(str(ROOT / "backend"))

from database import init_db, upsert_guide, set_guide_tags, close_pool
from dotenv import load_dotenv

load_dotenv(ROOT / "backend" / ".env")

EN_DIR = ROOT / "guides" / "en"
RU_DIR = ROOT / "guides" / "ru"

DIR_TO_CAT = {
    "beginner-guide": "beginners_guide",
    "character": "character",
    "spirit": "spirits",
    "companion": "companion",
    "equipment": "equipment",
    "new_from_discord": "misc",
}

def normalize_key(category_dir, filename):
    return f"{category_dir}_{filename.replace('.md', '')}".lower().replace("-", "_")

async def sync_guides():
    await init_db()
    
    guides_data = {} # key -> data
    
    # 1. PROCESS ENGLISH (as base)
    print("Processing English guides...")
    for p in EN_DIR.rglob("*.md"):
        content = p.read_text(encoding='utf-8')
        category_dir = p.parent.name
        cat_key = DIR_TO_CAT.get(category_dir, category_dir.replace("-", "_"))
        gkey = normalize_key(category_dir, p.name)
        
        # Simple metadata extraction
        title = p.stem.replace("_", " ").replace("-", " ")
        
        guides_data[gkey] = {
            "category_key": cat_key,
            "title": title,
            "text": content,
            "tags": [cat_key] # Basic tag
        }

    # 2. PROCESS RUSSIAN (to overwrite)
    print("Processing Russian guides (overwriting)...")
    for p in RU_DIR.rglob("*.md"):
        content = p.read_text(encoding='utf-8')
        category_dir = p.parent.name
        gkey = normalize_key(category_dir, p.name)
        
        # If RU version is too small and EN exists, maybe skip?
        # No, user wants updates. But let's check size.
        if len(content) < 50 and gkey in guides_data:
            print(f"  RU guide {gkey} is too short, keeping English base.")
            continue
            
        cat_key = DIR_TO_CAT.get(category_dir, category_dir.replace("-", "_"))
        title = p.stem.replace("_", " ").replace("-", " ")
        
        guides_data[gkey] = {
            "category_key": cat_key,
            "title": title,
            "text": content,
            "tags": [cat_key]
        }

    # 3. UPSERT TO DATABASE
    print(f"Syncing {len(guides_data)} guides to database...")
    for gkey, data in guides_data.items():
        try:
            await upsert_guide(
                key=gkey,
                category_key=data["category_key"],
                title=data["title"],
                icon_url=None,
                text=data["text"],
                photo=[],
                video=[],
                document=[],
                sort_order=0,
                changed_by=0
            )
            # Set tags
            await set_guide_tags(gkey, data["tags"])
        except Exception as e:
            print(f"Error syncing {gkey}: {e}")

    await close_pool()
    print("Database sync complete.")

if __name__ == "__main__":
    asyncio.run(sync_guides())
