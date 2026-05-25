import asyncio
from core.db import get_sessionmaker, init_db, close_pool
from models.db_models import Category, Guide
from sqlalchemy import select

async def main():
    await init_db()
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        cats = (await session.execute(select(Category))).scalars().all()
        print("CATEGORIES IN DB:")
        for c in cats:
            print(f"  Key: {c.key}, Title: {c.title}, SortOrder: {c.sort_order}")
        
        guides = (await session.execute(select(Guide))).scalars().all()
        print("\nGUIDES IN DB:")
        for g in guides:
            print(f"  Key: {g.key}, Title: {g.title}, CategoryKey: {g.category_key}")
    await close_pool()

if __name__ == '__main__':
    import sys
    sys.path.append('.')
    asyncio.run(main())
