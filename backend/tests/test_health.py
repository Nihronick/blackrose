import httpx
import pytest

@pytest.mark.asyncio
async def test_api_health():
    # We use localhost:8000 inside the container for FastAPI
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "degraded"
