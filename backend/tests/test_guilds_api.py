import pytest
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

@asynccontextmanager
async def _noop_lifespan(app):
    """No-op lifespan to skip DB/Inngest init in tests."""
    yield

@pytest.fixture
def client():
    with patch("main.app.router.lifespan_context", _noop_lifespan):
        with TestClient(app, raise_server_exceptions=False) as c:
            yield c

def test_public_guilds_list(client):
    """
    Test that public endpoint /api/guilds returns 200 with guilds list envelope.
    """
    mock_guilds = [{"id": 1, "name": "BlackRose Main", "member_count": 10, "max_members": 20}]
    with patch("api.guilds.guild_service.get_all_guilds", new_callable=AsyncMock, return_value=mock_guilds):
        response = client.get("/api/guilds")

    assert response.status_code == 200
    data = response.json()
    assert "guilds" in data
    assert len(data["guilds"]) == 1
    assert data["guilds"][0]["name"] == "BlackRose Main"

def test_guild_roster_not_found(client):
    """
    Test that requesting non-existent guild roster returns 404.
    """
    with patch("api.guilds.guild_service.get_guild_roster", new_callable=AsyncMock, return_value=None):
        response = client.get("/api/guilds/999999/roster")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data

def test_my_profile_unauthorized(client):
    """
    Test that /api/guilds/my/profile requires authentication.
    """
    response = client.get("/api/guilds/my/profile")
    assert response.status_code in (401, 403)

def test_join_guild_unauthorized(client):
    """
    Test that joining a guild requires authentication.
    """
    response = client.post("/api/guilds/join", json={"guild_id": 1, "nickname": "Hero"})
    assert response.status_code in (401, 403)
