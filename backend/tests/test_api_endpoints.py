"""
Integration tests for API endpoints.
Tests use TestClient with mocked lifespan and DB dependencies.
"""
import pytest
import time
import json
import hmac
import hashlib
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from core.config import settings

# ── Test Data ──────────────────────────────────────────────────
TEST_TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
TEST_UID = 12345678
ADMIN_UID = 987654321
settings.BOT_TOKEN = TEST_TOKEN
settings.ADMIN_USERS = f"{ADMIN_UID}"

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
ADMIN_HEADERS = {"X-Telegram-Init-Data": _make_init_data(ADMIN_UID, "Admin")}

@asynccontextmanager
async def _noop_lifespan(app):
    """No-op lifespan to skip DB/Inngest init in tests."""
    yield

@pytest.fixture
def client():
    """TestClient with mocked lifespan and member_service.is_admin."""
    with patch("main.app.router.lifespan_context", _noop_lifespan), \
         patch("api.public.member_service.is_admin", new_callable=AsyncMock, return_value=False), \
         patch("services.common.members.MemberService.is_admin", new_callable=AsyncMock, return_value=False):
        with TestClient(app, raise_server_exceptions=False) as c:
            yield c

# ── Tests ──────────────────────────────────────────────────────

class TestHealth:
    def test_health_ok(self, client):
        r = client.get("/api/health")
        # Without real DB, health returns degraded (503) or ok (200)
        assert r.status_code in (200, 503)
        data = r.json()
        assert "status" in data

class TestAuth:
    def test_auth_guest(self, client):
        r = client.get("/api/auth")
        assert r.status_code == 200
        assert r.json()["is_guest"] is True

    def test_auth_user(self, client):
        r = client.get("/api/auth", headers=USER_HEADERS)
        assert r.status_code == 200
        assert r.json()["authorized"] is True
        assert r.json()["is_admin"] is False

    def test_auth_admin(self, client):
        with patch("api.public.member_service.is_admin", new_callable=AsyncMock, return_value=True):
            r = client.get("/api/auth", headers=ADMIN_HEADERS)
        assert r.status_code == 200
        assert r.json()["is_admin"] is True

class TestGuides:
    @patch("api.public.category_service.get_all", new_callable=AsyncMock)
    def test_get_categories(self, mock_get_all, client):
        mock_get_all.return_value = [{"key": "test", "title": "Test", "icon_url": None, "sort_order": 0}]
        r = client.get("/api/categories", headers=USER_HEADERS)
        assert r.status_code == 200
        assert len(r.json()["categories"]) == 1

    @patch("api.public.guide_service.get_by_key", new_callable=AsyncMock)
    def test_get_guide_not_found(self, mock_get, client):
        mock_get.return_value = None
        r = client.get("/api/guide/missing", headers=USER_HEADERS)
        assert r.status_code == 404

    @patch("api.public.guide_service.get_by_key", new_callable=AsyncMock)
    def test_get_guide_found(self, mock_get, client):
        mock_get.return_value = {
            "key": "test",
            "title": "Test Guide",
            "text": "Hello",
            "category_key": "cat"
        }
        r = client.get("/api/guide/test", headers=USER_HEADERS)
        assert r.status_code == 200
        assert r.json()["title"] == "Test Guide"

class TestAdmin:
    def test_admin_access_denied(self, client):
        r = client.get("/api/admin/guides", headers=USER_HEADERS)
        assert r.status_code == 403

    @patch("api.admin.guide_service.get_all", new_callable=AsyncMock)
    def test_admin_access_granted(self, mock_get, client):
        mock_get.return_value = []
        r = client.get("/api/admin/guides", headers=ADMIN_HEADERS)
        assert r.status_code == 200
