import pytest
from httpx import AsyncClient
import sys
import os

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    """
    Test that the health endpoint is accessible and returns a 200/503 status.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/health")
    
    # We accept 200 (ok) or 503 (service degraded - common in CI without real DB)
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "version" in data

@pytest.mark.asyncio
async def test_auth_unauthorized():
    """
    Test that protected endpoints return 401/403 without credentials.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Try to access a protected admin endpoint
        response = await ac.get("/api/admin/guides")
    
    assert response.status_code in (401, 403)

@pytest.mark.asyncio
async def test_invalid_jwt():
    """
    Test that invalid JWT tokens are rejected.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = await ac.get("/api/admin/guides", headers=headers)
    
    assert response.status_code == 401
    assert "detail" in response.json()

def generate_mock_init_data(token: str):
    """Helper to generate cryptographically valid initData for testing."""
    import hmac
    import hashlib
    import json
    import time
    from urllib.parse import urlencode

    user_data = {"id": 12345, "first_name": "Test", "last_name": "User", "username": "testuser"}
    params = {
        "auth_date": str(int(time.time())),
        "query_id": "AAH9_xxxx",
        "user": json.dumps(user_data, separators=(',', ':'))
    }
    
    # Build check string (alphabetical order)
    sorted_params = sorted(params.items())
    check_string = "\n".join([f"{k}={v}" for k, v in sorted_params])
    
    # Calculate hash using the official algorithm
    secret_key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    data_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    
    params["hash"] = data_hash
    return urlencode(params)

@pytest.mark.asyncio
async def test_telegram_auth_success(monkeypatch):
    """
    Test successful TMA authentication with valid HMAC signature.
    """
    fake_token = "123456789:ABCDEFG"
    # Mock BOT_TOKEN in dependencies
    import dependencies
    monkeypatch.setattr(dependencies, "BOT_TOKEN", fake_token)
    
    init_data = generate_mock_init_data(fake_token)
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        headers = {"X-Telegram-Init-Data": init_data}
        response = await ac.get("/api/auth/me", headers=headers)
    
    # Should be 200 OK since the HMAC is valid
    assert response.status_code == 200
    assert response.json()["id"] == 12345
