import asyncio
import httpx
import sys

async def verify_health(url: str):
    print(f"🔍 Verifying BlackRose Backend Health at {url}...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # 1. API Health
            resp = await client.get(f"{url}/health")
            if resp.status_code == 200:
                print(f"✅ API Health: OK ({resp.json()})")
            else:
                print(f"❌ API Health: Failed (Status {resp.status_code})")
                
            # 2. Inngest Discovery
            resp = await client.get(f"{url}/api/inngest")
            if resp.status_code == 200:
                print(f"✅ Inngest: OK (Discovered functions)")
            else:
                print(f"❌ Inngest: Failed (Status {resp.status_code})")
                
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else "https://nihronick-blackrose-backend.hf.space"
    asyncio.run(verify_health(target_url))
