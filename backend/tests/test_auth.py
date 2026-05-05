import hmac
import hashlib
import json
import time
from urllib.parse import urlencode
from core.auth import verify_telegram_init_data, verify_telegram_login_widget
from core.config import settings

def _make_init_data(user: dict, token: str, auth_date: int = None):
    if auth_date is None:
        auth_date = int(time.time())
    params = {
        "user": json.dumps(user, separators=(',', ':')),
        "auth_date": str(auth_date)
    }
    check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret_key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    data_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    params["hash"] = data_hash
    return urlencode(params)

def test_verify_init_data_success():
    user = {"id": 12345, "first_name": "Test"}
    token = settings.BOT_TOKEN
    init_data = _make_init_data(user, token)
    result = verify_telegram_init_data(init_data)
    assert result is not None
    assert result["id"] == 12345

def test_verify_init_data_invalid_hash():
    user = {"id": 12345}
    init_data = _make_init_data(user, "wrong_token")
    assert verify_telegram_init_data(init_data) is None

def test_verify_init_data_expired():
    user = {"id": 12345}
    old_time = int(time.time()) - 90000 # More than 24h
    init_data = _make_init_data(user, settings.BOT_TOKEN, auth_date=old_time)
    assert verify_telegram_init_data(init_data) is None

def test_verify_login_widget_success():
    data = {
        "id": "12345",
        "first_name": "Test",
        "auth_date": str(int(time.time()))
    }
    check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret_key = hashlib.sha256(settings.BOT_TOKEN.encode()).digest()
    expected = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    data["hash"] = expected

    result = verify_telegram_login_widget(data)
    assert result is not None
    assert result["id"] == 12345

def test_verify_login_widget_fail():
    data = {"id": "1", "hash": "wrong"}
    assert verify_telegram_login_widget(data) is None
