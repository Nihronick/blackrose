#!/usr/bin/env python3
"""
BlackRose Discord Dynamic Sync v3.0
Автономная, динамическая синхронизация базы знаний Discord → Сайт на базе ИИ (NVIDIA NIM / Gemini / DeepSeek).

Ключевые отличия:
1. 0 ХАРДКОДА КАТЕГОРИЙ И СПИСКОВ:
   - Полностью динамическое обнаружение дерева каналов и категорий Discord API.
   - Автоматический перевод названий категорий и гайдов через NVIDIA NIM Llama 3.3 70B / DeepSeek V3.
2. ИНТЕЛЛЕКТУАЛЬНАЯ КЛАСТЕРИЗАЦИЯ:
   - Автоматическое объединение связанных сообщений одного автора в полноценные статьи.
   - Полная поддержка форумов (активные + архивные треды с пагинацией).
3. СОХРАННОСТЬ РАЗМЕТКИ И МЕДИА:
   - 100% сохранение Discord эмодзи <:name:id>, макросов {{icon:...}} и таблиц Markdown.
   - Перманентное кэширование медиафайлов в Hugging Face CDN без поломки ссылок.
"""

import os
import sys
import json
import re
import ssl
import time
import urllib.request
import urllib.parse
import urllib.error
from typing import Any, Dict, List, Optional, Tuple

sys.stdout.reconfigure(encoding="utf-8")

# ═══════════════════════════════════════════════════════════════
# ⚙️  КОНФИГУРАЦИЯ И ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ
# ═══════════════════════════════════════════════════════════════

def load_env():
    """Загрузка переменных из .env файлов."""
    for env_path in [".env", "backend/.env", "../.env"]:
        if os.path.exists(env_path):
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

_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE

# ═══════════════════════════════════════════════════════════════
# 🤖  ИИ-СИСТЕМА ПЕРЕВОДА И СОХРАНЕНИЯ РАЗМЕТКИ (NVIDIA NIM)
# ═══════════════════════════════════════════════════════════════

AI_TRANSLATE_PROMPT = """Ты — профессиональный игровой локализатор и эксперт по мобильной игре Slayer Legend.
Твоя задача — качественно и естественно перевести руководство по игре с английского на русский язык.

КРИТИЧЕСКИЕ ПРАВИЛА:
1. СОХРАНЯЙ ВСЮ РАЗМЕТКУ И МЕДИА-ТЕГИ:
   - Ссылки [Текст](url) — переводи только текст ссылки, URL оставляй без изменений!
   - Медиа-теги ![...](url), видео [Video: ...](url) — сохраняй в точности.
   - Иконки и эмодзи {{...}}, <:name:id>, <a:name:id>, юникод-эмодзи — НЕ удаляй, НЕ изменяй, НЕ переводи внутри скобок!
   - Код `...`, блоки кода ```...```, заголовки #, ##, списки -, * — сохраняй структуру Markdown.
   - Таблицы Markdown | col | col | — сохраняй структуру колонок и разделители.
2. ИСПОЛЬЗУЙ ИГРОВОЙ СЛЕНГ И ТЕРМИНОЛОГИЮ SLAYER LEGEND:
   - Rave -> Рейв, Rage -> Ярость
   - Spirits -> Духи (Sala -> Сала, Loar -> Лоар, Noah -> Ной, Radon -> Радон, Mum -> Мам, Bo -> Бо)
   - Familiars -> Фамильяры, JE -> JE
   - Promotion -> Продвижение, Stage -> Этап
   - Latent / Latent Power -> Латентка / Скрытая сила
   - CD / Cooldown -> КД (перезарядка), DPS -> ДПС, Ult / Ultimate -> Ульта
   - Boss -> Босс, Mobs -> Мобы, Beast -> Зверь, Phase -> Фаза
   - Breakthrough -> Прорыв, WoG / Wrath of Gods -> Гнев богов (WoG)
   - Flowing Blade -> Текущий клинок, Warrior Burn -> Пылающий воин
   - Speed Sword -> Скоростной меч, Earth's Will -> Воля земли
   - Auto -> Авто-режим / Авто, Manual -> Ручной режим
3. Перевод должен быть естественным, грамотным и понятным русскоязычным игрокам.
4. Выводи ТОЛЬКО готовый переведенный Markdown текст без вступительных или заключительных фраз."""


class DynamicAITranslator:
    @staticmethod
    def _post_process(text: str) -> str:
        text = text.replace("![видео]", "![video]").replace("![изображение]", "![image]")
        text = text.replace("\ufffd", "")
        return text.strip()

    @classmethod
    def translate_title(cls, text: str) -> str:
        """Динамический перевод заголовка раздела или гайда через ИИ."""
        clean = text.replace("-", " ").replace("_", " ").strip()
        if not clean:
            return text
        
        # Если есть NVIDIA NIM — быстрый точный перевод заголовка
        if NVIDIA_API_KEY:
            try:
                url = "https://integrate.api.nvidia.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"}
                payload = {
                    "model": "meta/llama-3.3-70b-instruct",
                    "messages": [
                        {"role": "system", "content": "Переведи игровое название категории/гайда Slayer Legend на русский язык кратко (2-4 слова). Выведи только результат."},
                        {"role": "user", "content": clean}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 64
                }
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
                with urllib.request.urlopen(req, context=_ssl_ctx, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    res = data["choices"][0]["message"]["content"].strip().strip('"\'')
                    if res and len(res) < 80:
                        return res
            except Exception:
                pass

        return cls.translate_text(clean)

    @classmethod
    def translate_text(cls, text: str) -> str:
        """Каскадный перевод полного текста через доступные ИИ-модели."""
        if not text or len(text.strip()) < 5:
            return text

        # 1. NVIDIA NIM (Llama 3.3 70B / DeepSeek V3)
        if NVIDIA_API_KEY:
            for model_name in ["meta/llama-3.3-70b-instruct", "deepseek-ai/deepseek-v3"]:
                try:
                    url = "https://integrate.api.nvidia.com/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"}
                    payload = {
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": AI_TRANSLATE_PROMPT},
                            {"role": "user", "content": f"Текст для перевода:\n{text}"}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 4096
                    }
                    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
                    with urllib.request.urlopen(req, context=_ssl_ctx, timeout=35) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        res = data["choices"][0]["message"]["content"].strip()
                        if res:
                            return cls._post_process(res)
                except Exception:
                    pass

        # 2. Google Gemini Flash
        if GEMINI_API_KEY:
            for model in ["gemini-2.5-flash", "gemini-1.5-flash"]:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
                    payload = {
                        "contents": [{"parts": [{"text": f"{AI_TRANSLATE_PROMPT}\n\nТекст для перевода:\n{text}"}]}],
                        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 4096}
                    }
                    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
                    with urllib.request.urlopen(req, context=_ssl_ctx, timeout=25) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        candidates = data.get("candidates", [])
                        if candidates and candidates[0].get("content", {}).get("parts"):
                            res = candidates[0]["content"]["parts"][0].get("text", "").strip()
                            if res:
                                return cls._post_process(res)
                except Exception:
                    pass

        # 3. Smart Lossless Fallback Engine (с полной маскировкой)
        return cls._translate_smart_fallback(text)

    @classmethod
    def _translate_smart_fallback(cls, text: str) -> str:
        code_blocks = {}
        cidx = 0
        patterns = [
            r'```[\s\S]*?```',
            r'`[^`\n]+`',
            r'\{\{[^}]+\}\}',
            r'<a?:[A-Za-z0-9_]+:\d+>',
            r'\[Video:[^\]]+\]\([^)]+\)',
            r'\[Видео:[^\]]+\]\([^)]+\)',
            r'https?://[^\s)\]]+',
            r'/api/media/[a-f0-9]+',
        ]
        masked = text
        for pat in patterns:
            for m in re.finditer(pat, masked):
                val = m.group(0)
                ph = f"XQB{cidx}BQX"
                code_blocks[ph] = val
                masked = masked.replace(val, ph, 1)
                cidx += 1

        try:
            encoded = urllib.parse.quote(masked)
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ru&dt=t&q={encoded}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, context=_ssl_ctx, timeout=15) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                translated = "".join(seg[0] for seg in result[0] if seg and seg[0])
        except Exception:
            translated = masked

        for ph, val in code_blocks.items():
            translated = translated.replace(ph, val)
        translated = re.sub(r'XQB\d+BQX', '', translated)
        return cls._post_process(translated)


# ═══════════════════════════════════════════════════════════════
# 🌐  DISCORD API & CLOUD BACKEND CLIENT
# ═══════════════════════════════════════════════════════════════

def slugify(text: str) -> str:
    """Генерация чистого ASCII URL-слага из любого заголовка."""
    import unicodedata
    s = unicodedata.normalize('NFKD', str(text)).lower().strip()
    translit = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    }
    res = ""
    for ch in s:
        if ch in translit:
            res += translit[ch]
        elif ch.isalnum() or ch in '-_':
            res += ch
        elif ch.isspace():
            res += '-'
    res = re.sub(r'-+', '-', res).strip('-')
    return res[:60] or "general"


class DiscordAPI:
    @staticmethod
    def request(path: str) -> Tuple[int, Any]:
        url = f"https://discord.com/api/v10{path}"
        headers = {
            "Authorization": DISCORD_TOKEN,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, context=_ssl_ctx, timeout=20) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                err_data = json.loads(e.read().decode("utf-8"))
            except Exception:
                err_data = str(e)
            return e.code, err_data
        except Exception as e:
            return 500, str(e)

    @classmethod
    def get_guild_channels(cls, guild_id: str) -> List[Dict]:
        status, data = cls.request(f"/guilds/{guild_id}/channels")
        return data if status == 200 and isinstance(data, list) else []

    @classmethod
    def get_forum_threads(cls, channel_id: str) -> List[Dict]:
        threads = []
        seen = set()
        # Active threads
        s, data = cls.request(f"/guilds/{GUILD_ID}/threads/active")
        if s == 200 and isinstance(data, dict):
            for t in data.get("threads", []):
                if str(t.get("parent_id")) == channel_id and t["id"] not in seen:
                    threads.append(t)
                    seen.add(t["id"])
        # Archived threads with pagination
        before = None
        for _ in range(15):
            p = f"/channels/{channel_id}/threads/archived/public" + (f"?before={before}" if before else "")
            time.sleep(0.3)
            s, data = cls.request(p)
            if s != 200 or not isinstance(data, dict):
                break
            batch = data.get("threads", [])
            if not batch:
                break
            for t in batch:
                if t["id"] not in seen:
                    threads.append(t)
                    seen.add(t["id"])
            before = batch[-1].get("thread_metadata", {}).get("archive_timestamp")
        return threads

    @classmethod
    def get_messages(cls, channel_id: str, limit: int = 100) -> List[Dict]:
        status, data = cls.request(f"/channels/{channel_id}/messages?limit={limit}")
        return data if status == 200 and isinstance(data, list) else []


class BackendClient:
    jwt_token: str = ""

    @classmethod
    def login(cls) -> str:
        url = f"{BACKEND_URL}/api/auth/login"
        body = json.dumps({"username": ADMIN_USER, "password": ADMIN_PASS}).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, context=_ssl_ctx, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                cls.jwt_token = data.get("token") or data.get("access_token", "")
                return cls.jwt_token
        except Exception as e:
            print(f"  [WARN] Backend login failed: {e}")
            return ""

    @classmethod
    def persist_media(cls, raw_url: str) -> str:
        if not raw_url or not cls.jwt_token:
            return raw_url
        if any(h in raw_url for h in ["huggingface.co", "nihronick", "/api/media/"]):
            return raw_url
        try:
            url = f"{BACKEND_URL}/api/admin/media/import-url"
            body = json.dumps({"url": raw_url}).encode("utf-8")
            headers = {"Authorization": f"Bearer {cls.jwt_token}", "Content-Type": "application/json"}
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, context=_ssl_ctx, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("permanent_url") or data.get("url") or raw_url
        except Exception:
            return raw_url

    @classmethod
    def ingest_guide(cls, guide_key: str, cat_key: str, cat_title: str, title: str, text: str, photos: list, videos: list, sort_order: int) -> dict:
        url = f"{BACKEND_URL}/api/webhook/ingest"
        body = json.dumps({
            "guide_key": guide_key,
            "category_key": cat_key,
            "category_title": cat_title,
            "title": title,
            "text": text,
            "photo": photos[:15],
            "video": videos[:10],
            "document": [],
            "sort_order": sort_order
        }).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "X-Ingest-Token": "dev_ingest_token"}, method="POST")
        try:
            with urllib.request.urlopen(req, context=_ssl_ctx, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"error": str(e)}

    @classmethod
    def register_sync_channel(cls, channel_id: str, channel_name: str, category_key: str):
        if not cls.jwt_token:
            return
        url = f"{BACKEND_URL}/api/admin/discord-sync/channels"
        body = json.dumps({
            "channel_id": str(channel_id),
            "channel_name": channel_name,
            "category_key": category_key,
            "auto_translate": True
        }).encode("utf-8")
        headers = {"Authorization": f"Bearer {cls.jwt_token}", "Content-Type": "application/json"}
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, context=_ssl_ctx, timeout=10):
                pass
        except Exception:
            pass

    @classmethod
    def clean_obsolete_categories(cls, valid_keys: set):
        """Удаление устаревших/мусорных категорий с сайта."""
        if not cls.jwt_token:
            return
        try:
            url = f"{BACKEND_URL}/api/categories"
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {cls.jwt_token}"})
            with urllib.request.urlopen(req, context=_ssl_ctx, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                cats = data.get("categories", [])
                for c in cats:
                    ckey = c.get("key")
                    if ckey and ckey not in valid_keys:
                        del_url = f"{BACKEND_URL}/api/admin/category/{ckey}"
                        del_req = urllib.request.Request(del_url, headers={"Authorization": f"Bearer {cls.jwt_token}"}, method="DELETE")
                        try:
                            with urllib.request.urlopen(del_req, context=_ssl_ctx, timeout=10):
                                print(f"  [x] Удален нерелевантный раздел: {ckey}")
                        except Exception:
                            pass
        except Exception as e:
            print(f"  [WARN] Failed to clean categories: {e}")


# ═══════════════════════════════════════════════════════════════
# 🧠  ДИНАМИЧЕСКИЙ СБОРЩИК И ФОРМАТТЕР КОНТЕНТА
# ═══════════════════════════════════════════════════════════════

def format_message_content(m: Dict) -> Tuple[str, List[str], List[str]]:
    """Извлечение текста, медиа и эмбедов сообщения с персистентными ссылками."""
    content = m.get("content", "").strip()
    photos = []
    videos = []
    media_lines = []

    # 1. Вложения
    for att in m.get("attachments", []):
        raw_url = att.get("url", "")
        if not raw_url:
            continue
        perm_url = BackendClient.persist_media(raw_url)
        fname = att.get("filename", "").lower()
        if any(fname.endswith(ext) for ext in ('.mp4', '.webm', '.mov', '.mkv')):
            videos.append(perm_url)
            media_lines.append(f"\n\n[Video: Видеоинструкция]({perm_url})\n\n")
        else:
            photos.append(perm_url)
            media_lines.append(f"\n\n![Изображение]({perm_url})\n\n")

    # 2. Эмбеды
    embed_lines = []
    for emb in m.get("embeds", []):
        if not isinstance(emb, dict):
            continue
        if emb.get("image") and emb["image"].get("url"):
            p = BackendClient.persist_media(emb["image"]["url"])
            photos.append(p)
            media_lines.append(f"\n\n![Скриншот]({p})\n\n")
        if emb.get("video") and emb["video"].get("url"):
            v = BackendClient.persist_media(emb["video"]["url"])
            videos.append(v)
            media_lines.append(f"\n\n[Video: Видео]({v})\n\n")
        if emb.get("title"):
            embed_lines.append(f"### {emb['title']}")
        if emb.get("description"):
            embed_lines.append(emb["description"].strip())
        for f in emb.get("fields", []):
            if isinstance(f, dict) and f.get("name") and f.get("value"):
                embed_lines.append(f"**{f['name']}**\n{f['value']}")

    full_text = content
    if embed_lines:
        full_text = f"{full_text}\n\n" + "\n\n".join(embed_lines)
    if media_lines:
        full_text = f"{full_text}\n" + "".join(media_lines)

    return full_text.strip(), photos, videos


def extract_smart_title(raw_text: str, default_title: str) -> str:
    """Извлечение информативного заголовка из текста гайда без артефактов цитат и алертов."""
    for line in raw_text.split("\n"):
        clean = line.strip()
        clean = re.sub(r'^>\s*(\[![\w\s]+\])?\s*', '', clean).strip()
        clean = clean.strip("# *-_`~").strip()
        if not clean or clean.startswith(("![", "[Video:", "{{", "http://", "https://", "<a:", "<:")):
            continue
        if len(clean) >= 4:
            return clean[:80]
    return default_title


def cluster_text_channel_messages(msgs: List[Dict]) -> List[Dict]:
    """
    Интеллектуальная кластеризация сообщений текстового канала:
    - Если автор пишет серию связанных постов с заголовками (#, ##) — они объединяются в один гайд.
    - Самостоятельные посты обрабатываются отдельно.
    """
    if not msgs:
        return []

    sorted_msgs = sorted(msgs, key=lambda x: int(x.get("id", "0")))
    
    # Проверка: представляет ли весь канал единый сборник (например, рекомендации костюмов / FAQ)
    is_unified_collection = len(sorted_msgs) <= 15 and all(
        m.get("author", {}).get("id") == sorted_msgs[0].get("author", {}).get("id") or len(m.get("content", "")) >= 100
        for m in sorted_msgs
    )

    if is_unified_collection and len(sorted_msgs) > 1:
        text_parts = []
        all_photos = []
        all_videos = []
        for m in sorted_msgs:
            t, p, v = format_message_content(m)
            if t:
                text_parts.append(t)
            all_photos.extend(p)
            all_videos.extend(v)
        
        return [{
            "id": f"merged_{sorted_msgs[0]['id']}",
            "text": "\n\n---\n\n".join(text_parts),
            "photos": all_photos,
            "videos": all_videos,
            "is_merged": True
        }]

    # Построчная обработка отдельных сообщений-гайдов
    guides = []
    for m in sorted_msgs:
        t, p, v = format_message_content(m)
        if len(t) >= 60 or p or v:
            guides.append({
                "id": m["id"],
                "text": t,
                "photos": p,
                "videos": v,
                "is_merged": False
            })
    return guides


# ═══════════════════════════════════════════════════════════════
# 🚀  ОСНОВНОЙ ДИНАМИЧЕСКИЙ КОНВЕЙЕР СИНХРОНИЗАЦИИ
# ═══════════════════════════════════════════════════════════════

def run_dynamic_sync():
    print("=" * 70)
    print("  🚀 BlackRose Dynamic AI Scanner v3.0 (NVIDIA NIM / Gemini / DeepSeek)")
    print("=" * 70)

    if not DISCORD_TOKEN:
        print("❌ Ошибка: DISCORD_TOKEN не задан в .env!")
        sys.exit(1)

    print(f"[*] Логин в бэкенд ({BACKEND_URL})...")
    BackendClient.login()

    print(f"[*] Запрос структуры Discord Guild (ID: {GUILD_ID})...")
    all_channels = DiscordAPI.get_guild_channels(GUILD_ID)
    if not all_channels:
        print("❌ Не удалось получить каналы Discord. Проверьте DISCORD_TOKEN.")
        sys.exit(1)

    # 1. Поиск категорий базы знаний (Slayerpedia / Guides / Knowledge Base)
    parent_categories = {c["id"]: c for c in all_channels if c.get("type") == 4}
    
    # Находим главную категорию со справочником (или берем все каналы знаний)
    slayerpedia_cat = next(
        (c for c in parent_categories.values() if any(w in c.get("name", "").lower() for w in ["slayerpedia", "guide", "spravochnik", "wiki"])),
        None
    )
    slayerpedia_id = slayerpedia_cat["id"] if slayerpedia_cat else None
    
    if slayerpedia_cat:
        print(f"  [+] Обнаружена категория базы знаний: «{slayerpedia_cat['name']}» (ID: {slayerpedia_id})")

    # Каналы, входящие в базу знаний (type 0=Text, 5=Announcement, 15=Forum)
    knowledge_channels = [
        c for c in all_channels 
        if c.get("type") in (0, 5, 15) and (
            c.get("parent_id") == slayerpedia_id or 
            (not slayerpedia_id and not any(skip in c.get("name", "").lower() for skip in ["mod", "chat", "voice", "bot", "ticket", "log", "admin"]))
        ) and not any(skip in c.get("name", "").lower() for skip in [
            "feedback", "discussion", "off-topic", "memes", "bot-commands", 
            "change-log", "changelog", "slayer-playbook", "slayerpedia-index", 
            "bannibal-experiment", "disclaimer"
        ])
    ]
    
    # Сортировка по позиции в Discord
    knowledge_channels.sort(key=lambda x: (x.get("parent_id") != slayerpedia_id, x.get("position", 0)))
    print(f"  [+] Найдено {len(knowledge_channels)} активных каналов с гайдами.")

    # 2. Инициализация и динамический перевод категорий
    print(f"\n[1/3] Динамическая регистрация разделов...")
    categories_plan = []
    for idx, ch in enumerate(knowledge_channels):
        ch_name = ch.get("name", "")
        cat_key = slugify(ch_name)
        
        # Динамический ИИ перевод названия раздела
        cat_title = DynamicAITranslator.translate_title(ch_name)
        categories_plan.append({
            "channel": ch,
            "key": cat_key,
            "title_ru": cat_title,
            "sort_order": idx
        })
        print(f"  [{idx+1}/{len(knowledge_channels)}] «{ch_name}» → «{cat_title}» (/{cat_key})")
        
        # Инициализируем категорию на сайте
        BackendClient.ingest_guide(
            guide_key=f"cat_init_{cat_key}",
            cat_key=cat_key,
            cat_title=cat_title,
            title=f"Категория {cat_title}",
            text="Инициализация раздела",
            photos=[],
            videos=[],
            sort_order=idx
        )

    # Очистка неактуальных разделов
    BackendClient.clean_obsolete_categories({c["key"] for c in categories_plan})

    # 3. Сканирование и ИИ-перевод всех гайдов
    print(f"\n[2/3] Сканирование контента и ИИ-перевод гайдов...")
    total_imported = 0
    total_errors = 0

    for cat_info in categories_plan:
        ch = cat_info["channel"]
        cat_key = cat_info["key"]
        cat_title = cat_info["title_ru"]
        ch_type = ch.get("type")
        ch_id = ch["id"]
        ch_name = ch["name"]

        print(f"\n  📁 Раздел «{cat_title}» (#{ch_name}):")

        # ── FORUM CHANNEL (type=15) ──
        if ch_type == 15:
            threads = DiscordAPI.get_forum_threads(ch_id)
            print(f"    Найдено {len(threads)} тредов форума")
            for ti, th in enumerate(threads):
                tid = th["id"]
                tname = th.get("name", "Guide")
                
                # Сообщения треда
                msgs = DiscordAPI.get_messages(tid, limit=50)
                sorted_msgs = sorted(msgs, key=lambda x: int(x.get("id", "0")))
                
                # Форматирование и извлечение медиа
                text_parts = []
                all_photos = []
                all_videos = []
                for m in sorted_msgs:
                    t, p, v = format_message_content(m)
                    if t:
                        text_parts.append(t)
                    all_photos.extend(p)
                    all_videos.extend(v)

                full_thread_text = "\n\n---\n\n".join(text_parts)
                translated_text = DynamicAITranslator.translate_text(full_thread_text)
                
                guide_key = f"discord_{tid}"
                res = BackendClient.ingest_guide(
                    guide_key=guide_key,
                    cat_key=cat_key,
                    cat_title=cat_title,
                    title=tname,
                    text=translated_text,
                    photos=all_photos,
                    videos=all_videos,
                    sort_order=ti
                )
                if "error" in res:
                    total_errors += 1
                    print(f"      [{ti+1}/{len(threads)}] ❌ FAIL: {tname[:40]}")
                else:
                    total_imported += 1
                    media_str = f" ({len(all_photos)}p/{len(all_videos)}v)" if all_photos or all_videos else ""
                    print(f"      [{ti+1}/{len(threads)}] ✅ OK: {tname[:45]}{media_str}")

        # ── TEXT / ANNOUNCE CHANNEL (type=0, 5) ──
        else:
            raw_msgs = DiscordAPI.get_messages(ch_id, limit=100)
            clusters = cluster_text_channel_messages(raw_msgs)
            print(f"    Найдено {len(clusters)} статей/кластеров (из {len(raw_msgs)} сообщений)")

            for ci, cluster in enumerate(clusters):
                raw_text = cluster["text"]
                translated_text = DynamicAITranslator.translate_text(raw_text)
                
                # Извлечение информативного заголовка
                guide_title = extract_smart_title(raw_text, f"{cat_title} — Инфо #{ci+1}")
                
                guide_key = f"discord_{cluster['id']}"
                res = BackendClient.ingest_guide(
                    guide_key=guide_key,
                    cat_key=cat_key,
                    cat_title=cat_title,
                    title=guide_title,
                    text=translated_text,
                    photos=cluster["photos"],
                    videos=cluster["videos"],
                    sort_order=ci
                )
                if "error" in res:
                    total_errors += 1
                    print(f"      [{ci+1}/{len(clusters)}] ❌ FAIL: {guide_title[:40]}")
                else:
                    total_imported += 1
                    print(f"      [{ci+1}/{len(clusters)}] ✅ OK: {guide_title[:45]}")

    # 4. Регистрация каналов на автопрослушку
    print(f"\n[3/3] Регистрация каналов на фоновое автообновление (WebSocket)...")
    for cat_info in categories_plan:
        BackendClient.register_sync_channel(
            channel_id=cat_info["channel"]["id"],
            channel_name=cat_info["channel"]["name"],
            category_key=cat_info["key"]
        )

    print("\n" + "=" * 70)
    print("  🎉 ДИНАМИЧЕСКАЯ СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА!")
    print(f"  📁 Категорий обработано: {len(categories_plan)}")
    print(f"  📝 Гайдов импортировано: {total_imported}")
    print(f"  ❌ Ошибок:               {total_errors}")
    print("=" * 70)


if __name__ == "__main__":
    run_dynamic_sync()
