import pytest
from httpx import AsyncClient
from main import app
from services.cache.redis_cache import cache_service

@pytest.mark.asyncio
async def test_categories_caching():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 1. Clear cache
        await cache_service.invalidate_all()
        
        # 2. First request (Cache miss)
        response = await ac.get("/api/categories")
        assert response.status_code == 200
        data1 = response.json()
        
        # 3. Check if stored in redis
        # Key depends on the request URL in the decorator
        # For categories it should be cache:/api/categories:
        cached_data = await cache_service.get("cache:/api/categories:")
        assert cached_data is not None
        assert cached_data == data1
        
        # 4. Second request (Cache hit)
        response = await ac.get("/api/categories")
        assert response.status_code == 200
        assert response.json() == data1

@pytest.mark.asyncio
async def test_guide_caching():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Use a known guide key if possible, or mock guide_service
        guide_key = "test-guide"
        # 1. First request
        response = await ac.get(f"/api/guide/{guide_key}")
        # Even if 404, we check if it tried to cache or handle
        
        # 2. Check cache key
        cache_key = f"cache:/api/guide/{guide_key}:"
        # (Assuming no query params)
