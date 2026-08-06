import pytest
import httpx
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

@pytest.mark.asyncio
async def test_public_guilds_list():
    """
    Test that public endpoint /api/guilds returns 200 with guilds list envelope.
    """
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/guilds")

    assert response.status_code == 200
    data = response.json()
    assert "guilds" in data
    assert isinstance(data["guilds"], list)

@pytest.mark.asyncio
async def test_guild_roster_not_found():
    """
    Test that requesting non-existent guild roster returns 404.
    """
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/guilds/999999/roster")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data

@pytest.mark.asyncio
async def test_my_profile_unauthorized():
    """
    Test that /api/guilds/my/profile requires authentication.
    """
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/guilds/my/profile")

    assert response.status_code in (401, 403)

@pytest.mark.asyncio
async def test_join_guild_unauthorized():
    """
    Test that joining a guild requires authentication.
    """
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/guilds/join", json={"guild_id": 1, "nickname": "Hero"})

    assert response.status_code in (401, 403)
