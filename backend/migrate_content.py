"""
Run once to migrate all guide content from guides.py to PostgreSQL.
Usage: DATABASE_URL=postgresql://... python migrate_content.py
"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))


async def main():
    from database import init_db, upsert_category, upsert_guide, close_pool
    from icons import get_icon

    # Import original data
    from guides_original import MAIN_CATEGORIES, SUBMENUS, CONTENT

    await init_db()

    print("Migrating categories...")
    for i, (key, cat) in enumerate(MAIN_CATEGORIES.items()):
        icon = cat.get("icon", "")
        await upsert_category(key, cat["title"], icon, i)
        print(f"  ✓ {key}")

    print("\nMigrating guides...")
    for cat_key, items in SUBMENUS.items():
        for sort_order, item in enumerate(items):
            guide_key, title, icon_url = item[0], item[1], item[2]
            content = CONTENT.get(guide_key, {})

            text = content.get("text", "")
            photo = content.get("photo") or []
            video = content.get("video") or []
            document = content.get("document") or []

            # Normalize to lists
            if isinstance(video, str):
                video = [video] if video else []
            if isinstance(document, str):
                document = [document] if document else []

            await upsert_guide(
                key=guide_key,
                category_key=cat_key,
                title=title,
                icon_url=icon_url,
                text=text,
                photo=photo,
                video=video,
                document=document,
                sort_order=sort_order,
            )
            print(f"  ✓ {guide_key}: {title}")

    print("\n✅ Migration complete!")
    await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
