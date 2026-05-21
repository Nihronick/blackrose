import pytest
from unittest.mock import AsyncMock, patch
from contextlib import asynccontextmanager
from fastapi.testclient import TestClient
from main import app
from core.config import settings

@asynccontextmanager
async def _noop_lifespan(app):
    yield

@pytest.fixture
def client():
    with patch("main.app.router.lifespan_context", _noop_lifespan):
        with TestClient(app, raise_server_exceptions=False) as c:
            yield c

def test_webhook_ingest_missing_token(client):
    payload = {
        "guide_key": "test-guide",
        "category_key": "test-category",
        "title": "Test Title",
        "text": "Hello World"
    }
    r = client.post("/api/webhook/ingest", json=payload)
    assert r.status_code == 422  # Missing header validation error

def test_webhook_ingest_invalid_token(client):
    settings.INGEST_TOKEN = "correct_token"
    payload = {
        "guide_key": "test-guide",
        "category_key": "test-category",
        "title": "Test Title",
        "text": "Hello World"
    }
    r = client.post(
        "/api/webhook/ingest",
        json=payload,
        headers={"X-Ingest-Token": "wrong_token"}
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid ingest token"

@patch("api.webhook_ingest.guide_service.upsert", new_callable=AsyncMock)
@patch("api.webhook_ingest.cache_service.invalidate_all", new_callable=AsyncMock)
@patch("api.webhook_ingest.cache_service.invalidate_guide", new_callable=AsyncMock)
def test_webhook_ingest_success(
    mock_invalidate_guide,
    mock_invalidate_all,
    mock_upsert,
    client
):
    settings.INGEST_TOKEN = "correct_token"
    mock_upsert.return_value = True  # Simulated new guide created

    payload = {
        "guide_key": "test-guide",
        "category_key": "test-category",
        "title": "Test Title",
        "text": "Hello World",
        "sort_order": 5
    }

    r = client.post(
        "/api/webhook/ingest",
        json=payload,
        headers={"X-Ingest-Token": "correct_token"}
    )

    assert r.status_code == 200
    assert r.json() == {"ok": True, "created": True}

    # Verify services called correctly
    mock_upsert.assert_called_once_with(
        key="test-guide",
        data={
            "category_key": "test-category",
            "title": "Test Title",
            "icon_url": None,
            "text": "Hello World",
            "photo": [],
            "video": [],
            "document": [],
            "sort_order": 5
        },
        changed_by="webhook_ai_ingest"
    )
    mock_invalidate_all.assert_called_once()
    mock_invalidate_guide.assert_called_once_with("test-guide")
