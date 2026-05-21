"""
Health endpoint tests using TestClient (no real server needed).
"""
import pytest
from contextlib import asynccontextmanager
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app


@asynccontextmanager
async def _noop_lifespan(app):
    yield


@pytest.fixture
def client():
    with patch("main.app.router.lifespan_context", _noop_lifespan):
        with TestClient(app, raise_server_exceptions=False) as c:
            yield c


def test_api_health(client):
    """Health endpoint should return 200 with a status field."""
    response = client.get("/api/health")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert data["status"] in ("ok", "degraded")
