import json
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
    
    headers = {"Content-Type": "application/json"}
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
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
