import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv('.env')

from database import init_db
from database import _engine as engine
from db_models import Base, ViewLog

async def main():
    print("Initializing DB...")
    await init_db()
    
    from database import _engine
    print("Creating tables...")
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
