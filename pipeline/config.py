"""
Общая конфигурация пайплайна: переменные окружения, константы, утилиты.
"""
import os
import sys
import re
import ssl
import json
import time
import hashlib
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.stdout.reconfigure(encoding="utf-8")

# ═══════════════════════════════════════════════════════════════
# 📁  ПУТИ
# ═══════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
STRUCTURED_DIR = DATA_DIR / "structured"
TRANSLATED_DIR = DATA_DIR / "translated"
MEDIA_CACHE_FILE = DATA_DIR / "media_cache.json"
VALIDATION_REPORT_FILE = DATA_DIR / "validation_report.json"

# Создание директорий
for d in [RAW_DIR, STRUCTURED_DIR, TRANSLATED_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# ⚙️  ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ
# ═══════════════════════════════════════════════════════════════

def load_env():
    """Загрузка переменных из .env файлов."""
    for env_path in [PROJECT_ROOT / ".env", PROJECT_ROOT / "backend" / ".env"]:
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("\"'")
                        if k not in os.environ:
                            os.environ[k] = v

load_env()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip().strip("\"'")
GUILD_ID = os.getenv("GUILD_ID", "1052865879609724968")
BACKEND_URL = os.getenv("BACKEND_URL", "https://nihronick-blackrose-backend.hf.space").rstrip("/")
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "BlackRose2026SecureAdminKey!")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "").strip().strip("\"'")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip().strip("\"'")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip().strip("\"'")
HF_TOKEN = os.getenv("HF_TOKEN", "").strip().strip("\"'")

# ═══════════════════════════════════════════════════════════════
# 🔒  SSL
# ═══════════════════════════════════════════════════════════════

ssl_ctx = ssl.create_default_context()
# ssl_ctx.check_hostname = False
# ssl_ctx.verify_mode = ssl.CERT_NONE

# ═══════════════════════════════════════════════════════════════
# 🔧  УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════

# Каналы-исключения (мусор, видео-архивы, чаты)
SKIP_CHANNEL_NAMES = frozenset([
    "feedback", "discussion", "off-topic", "memes", "bot-commands",
    "change-log", "changelog", "slayer-playbook", "slayerpedia-index",
    "bannibal-experiment", "disclaimer", "video-archive", "video"
])

_TRANSLIT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
}

def slugify(text: str) -> str:
    """Генерация чистого ASCII URL-слага из любого заголовка."""
    import unicodedata
    s = unicodedata.normalize('NFKD', str(text)).lower().strip()
    res = ""
    for ch in s:
        if ch in _TRANSLIT:
            res += _TRANSLIT[ch]
        elif ch.isalnum() or ch in '-_':
            res += ch
        elif ch.isspace():
            res += '-'
    res = re.sub(r'-+', '-', res).strip('-')
    return res[:60] or "general"


def http_request(url: str, *, data: Optional[bytes] = None, headers: Optional[Dict[str, str]] = None,
                 method: str = "GET", timeout: int = 20) -> Tuple[int, Any]:
    """Универсальный HTTP-запрос с обработкой ошибок."""
    headers = headers or {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as e:
        try:
            err_data = json.loads(e.read().decode("utf-8"))
        except Exception:
            err_data = str(e)
        return e.code, err_data
    except Exception as e:
        return 500, {"error": str(e)}
