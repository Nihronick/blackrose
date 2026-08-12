import json
import ssl
import socket
import urllib.request
import urllib.parse
import urllib.error
import asyncio
from core.logging import get_logger

logger = get_logger("blackrose.telegram_api")

class IPv4HTTPSConnection(urllib.request.HTTPSConnection):
    def connect(self):
        err = None
        for res in socket.getaddrinfo(self.host, self.port, socket.AF_INET, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                self.sock = socket.socket(af, socktype, proto)
                if self.timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
                    self.sock.settimeout(self.timeout)
                self.sock.connect(sa)
                if self._tunnel_host:
                    self._tunnel()
                if self.context:
                    self.sock = self.context.wrap_socket(
                        self.sock, server_hostname=self.host
                    )
                return
            except socket.error as e:
                err = e
                if self.sock is not None:
                    self.sock.close()
        if err is not None:
            raise err
        raise socket.error("IPv4 resolution failed")

class IPv4HTTPSHandler(urllib.request.HTTPSHandler):
    def __init__(self, context=None):
        super().__init__(context=context)

    def https_open(self, req):
        return self.do_open(IPv4HTTPSConnection, req)

def _sync_telegram_request(token: str, method: str, payload: dict | None = None, params: dict | None = None, timeout: float = 15.0) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    if params:
        query = urllib.parse.urlencode(params)
        url = f"{url}?{query}"
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BlackRoseBot/1.0"
    }
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    handler = IPv4HTTPSHandler(context=ctx)
    opener = urllib.request.build_opener(handler)
    
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with opener.open(req, timeout=timeout) as resp:
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
