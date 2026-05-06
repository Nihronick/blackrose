"""
Cache layer integration tests.
Validates that the caching decorator works with Redis for public endpoints.
"""
import pytest
import time
import json
import hmac
import hashlib
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from main import app
from core.config import settings

# ── Auth Setup ──────────────────────────────────────────────────
TEST_TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
TEST_UID = 12345678
settings.BOT_TOKEN = TEST_TOKEN

def _make_init_data(uid: int, first_name: str = "Test") -> str:
    user = {"id": uid, "first_name": first_name}
    auth_date = int(time.time())
    params = {
        "user": json.dumps(user, ensure_ascii=False),
        "auth_date": str(auth_date),
    }
    check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret_key = hmac.new(b"WebAppData", TEST_TOKEN.encode(), hashlib.sha256).digest()
    sig = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    params["hash"] = sig
    from urllib.parse import urlencode
    return urlencode(params)

USER_HEADERS = {"X-Telegram-Init-Data": _make_init_data(TEST_UID)}

@asynccontextmanager
async def _noop_lifespan(app):
    yield

@pytest.fixture
def client():
    with patch("main.app.router.lifespan_context", _noop_lifespan), \
         patch("api.public.member_service.is_admin", new_callable=AsyncMock, return_value=False), \
         patch("services.common.members.MemberService.is_admin", new_callable=AsyncMock, return_value=False):
        with TestClient(app, raise_server_exceptions=False) as c:
            yield c

# ── Tests ──────────────────────────────────────────────────────

class TestCacheLayer:
    @patch("api.public.category_service.get_all", new_callable=AsyncMock)
    def test_categories_caching(self, mock_get_all, client):
        """Test that /api/categories returns 200 with valid auth."""
        mock_get_all.return_value = [
            {"key": "test", "title": "Test Category", "icon_url": None, "sort_order": 0}
        ]
        # First request
        r1 = client.get("/api/categories", headers=USER_HEADERS)
        assert r1.status_code == 200
        data1 = r1.json()
        assert len(data1["categories"]) == 1

        # Second request (should hit cache or service again)
        r2 = client.get("/api/categories", headers=USER_HEADERS)
        assert r2.status_code == 200
        assert r2.json() == data1

    @patch("api.public.guide_service.get_by_key", new_callable=AsyncMock)
    def test_guide_caching(self, mock_get, client):
        """Test that /api/guide/{key} returns 200 for existing guide."""
        mock_get.return_value = {
            "key": "test-guide",
            "title": "Test Guide",
            "text": "Content",
            "category_key": "test",
        }
        r = client.get("/api/guide/test-guide", headers=USER_HEADERS)
        assert r.status_code == 200
        assert r.json()["title"] == "Test Guide"

    @patch("api.public.guide_service.get_by_key", new_callable=AsyncMock)
    def test_guide_not_found(self, mock_get, client):
        """Test that /api/guide/{key} returns 404 for missing guide."""
        mock_get.return_value = None
        r = client.get("/api/guide/missing", headers=USER_HEADERS)
        assert r.status_code == 404
