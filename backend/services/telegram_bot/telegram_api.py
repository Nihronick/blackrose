import json
import ssl
import urllib.request
import urllib.parse
import urllib.error
import asyncio
from core.logging import get_logger

logger = get_logger("blackrose.telegram_api")

def _sync_telegram_request(token: str, method: str, payload: dict | None = None, params: dict | None = None, timeout: float = 15.0) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    if params:
        query = urllib.parse.urlencode(params)
        url = f"{url}?{query}"
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 BlackRoseBot/1.0"
    }
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            content = resp.read().decode("utf-8")
            return json.loads(content)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        logger.warning(f"Telegram API HTTP error {e.code} for {method}: {body}")
        try:
            return json.loads(body)
        except Exception:
            return {"ok": False, "error": f"HTTP {e.code}", "body": body}
    except Exception as e:
        logger.warning(f"Telegram API request failed for {method}: {e}")
        return {"ok": False, "error": str(e)}

async def send_telegram_request(token: str, method: str, payload: dict | None = None, params: dict | None = None, timeout: float = 15.0) -> dict:
    return await asyncio.to_thread(_sync_telegram_request, token, method, payload, params, timeout)
