import asyncio
import os
import sys
import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Добавляем путь к бэкенду, чтобы импортировать настройки
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

async def check_db():
    print("🔍 Checking Database connection...")
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL is not set!")
        return False
    
    try:
        engine = create_async_engine(db_url)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ Database is UP")
        return True
    except Exception as e:
        print(f"❌ Database is DOWN: {e}")
        return False

async def check_api():
    print("\n🔍 Checking API health...")
    port = os.getenv("PORT", "8000")
    url = f"http://localhost:{port}/api/health"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                print(f"✅ API is UP ({response.json()})")
                return True
            else:
                print(f"⚠️ API returned {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ API is unreachable: {e}")
        return False

async def main():
    print("=== BlackRose System Integrity Check ===\n")
    db_ok = await check_db()
    api_ok = await check_api()
    
    print("\n" + "="*40)
    if db_ok and api_ok:
        print("🚀 ALL SYSTEMS GO!")
        sys.exit(0)
    else:
        print("🔴 SYSTEM IS UNHEALTHY")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
