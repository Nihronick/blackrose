#!/usr/bin/env python3
"""
BlackRose Discord Full Sync v2 — полная автосинхронизация Discord → Сайт.

Что делает:
  0. Очищает ВСЕ гайды и категории на сайте
  1. Считывает структуру Discord-сервера (категории → каналы → треды)
  2. Создаёт категории с русскими названиями
  3. Импортирует ВСЕ гайды с полным содержимым
  4. Регистрирует каналы для прослушки (автообновление)

Использование:
  1. Вставьте свежий DISCORD_TOKEN ниже
  2. python scan_discord.py
"""

import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

# ═══════════════════════════════════════════════════════════════
# ⚙️  НАСТРОЙКИ
# ═══════════════════════════════════════════════════════════════

# Ваш Discord User Token (из переменной окружения или указать перед запуском)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")

# Discord Guild ID (BlackRose сервер)
GUILD_ID = "1052865879609724968"

# Бэкенд BlackRose
BACKEND_URL = "https://nihronick-blackrose-backend.hf.space"

# Логин/пароль админа (из переменных окружения)
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "BlackRose2026SecureAdminKey!")

# Перевод названий категорий Discord → русский
CATEGORY_NAME_MAP = {
    "shop": "Магазин",
    "equipment": "Экипировка",
    "character": "Персонаж",
    "skills": "Навыки",
    "companion": "Компаньоны и Фамильяры",
    "companions": "Компаньоны и Фамильяры",
    "familiars": "Фамильяры",
    "spirit": "Духи",
    "spirits": "Духи",
    "adventure": "Приключения",
    "stage": "Этапы",
    "beginner-guide": "Гайд для начинающих",
    "early-game-promotions": "Продвижение (Early Game)",
    "mid-game-promotions": "Продвижение (Mid Game)",
    "late-game-promotions": "Продвижение (Late Game)",
    "story-lore": "Сюжет и Лор",
    "slayer-playbook": "Книга Охотника",
    "bannibal-experiment-builds": "Экспериментальные Билды",
    "promotion-and-suit-recommendation": "Рекомендации Костюмов",
    "event-help": "Помощь по Ивентам",
    "slayerpedia-index": "Индекс Охотникпедии",
    "beginners": "Для новичков",
    "beginner": "Для новичков",
    "beginners guide": "Гайды для новичков",
    "beginner guide": "Гайд для новичков",
    "beginner's guide": "Гайды для новичков",
    "slayer": "Охотник",
    "slayer playbook": "Книга Охотника",
    "stage": "Этапы",
    "stages": "Этапы",
    "character": "Персонаж",
    "characters": "Персонажи",
    "promotions": "Продвижение",
    "mid game promotions": "Продвижение Mid Game",
    "mid-game promotions": "Продвижение Mid Game",
    "late game promotions": "Продвижение Late Game",
    "late-game promotions": "Продвижение Late Game",
    "suit recommendation": "Рекомендации Снаряжения",
    "suits": "Снаряжение",
    "guides": "Гайды",
    "general": "Общее",
    "information": "Информация",
    "events": "Ивенты",
    "pvp": "PvP",
    "pve": "PvE",
    "guild": "Гильдия",
    "guilds": "Гильдии",
    "tips": "Советы",
    "tips & tricks": "Советы и Хитрости",
    "resources": "Ресурсы",
    "builds": "Билды",
    "classes": "Классы",
    "equipment": "Экипировка",
    "pets": "Питомцы",
    "mounts": "Маунты",
    "crafting": "Крафт",
    "dungeons": "Подземелья",
    "raids": "Рейды",
    "boss": "Боссы",
    "bosses": "Боссы",
    "awakening": "Пробуждение",
    "abyss": "Бездна",
    "rift": "Рифт",
    "arena": "Арена",
    "farming": "Фарм",
    "leveling": "Прокачка",
    "guide channel": "Канал гайдов",
    "media": "Медиа",
    "announcements": "Объявления",
    "community": "Сообщество",
    "off-topic": "Оффтоп",
    "bot commands": "Команды ботов",
}

# Категории Discord которые нужно ВКЛЮЧИТЬ (гайды и ресурсы)
GUIDE_CATEGORIES_WHITELIST = {
    "slayerpedia", "resources", "start here", "beginners", "beginner",
    "guides", "skills", "familiars", "slayer playbook", "stage",
    "character", "promotions", "suit recommendation", "builds", "tips",
}

# Категории Discord которые нужно ПРОПУСТИТЬ (служебные и болталки)
SKIP_CATEGORIES = {
    "moderation", "mod", "staff", "admin", "administration",
    "voice channels", "voice", "vc", "bot", "bots", "bot commands",
    "logs", "server logs", "tickets", "support", "archive", "archived",
    "slayer general", "slayer off topic", "slayer bot", "support tickets",
    "event-archive", "all about you",
}

# Каналы Discord которые нужно ПРОПУСТИТЬ (флуд)
SKIP_CHANNELS = {
    "rules", "welcome", "announcements", "general", "off-topic",
    "bot-commands", "bot-spam", "media", "memes", "introductions",
    "suggestions", "feedback", "report", "apply", "art", "muted-only",
    "cookie-jar", "food-and-animals", "flex", "true-salt", "cake-help-chat",
    "skill-chat", "personal-roles", "promotion-roles", "botsetup",
}

# Типы каналов которые содержат гайды
GUIDE_CHANNEL_TYPES = {0, 5, 15}  # TEXT, ANNOUNCE, FORUM


def slugify(text: str) -> str:
    """Генерация безопасного ASCII ключа."""
    import unicodedata
    s = unicodedata.normalize('NFKD', str(text)).lower().strip()
    
    translit = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    }
    result = ""
    for ch in s:
        if ch in translit:
            result += translit[ch]
        elif ch.isalnum() or ch in '-_':
            result += ch
        elif ch.isspace():
            result += '_'
    result = re.sub(r'_+', '_', result).strip('_')
    return result[:55] or "general"


DISCORD_API = "https://discord.com/api/v10"
_ssl_ctx = ssl.create_default_context()

HEADERS_DISCORD = {
    "Authorization": "",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# ── Игровой глоссарий для перевода ──
GAMING_GLOSSARY = {
    "Rift": "Рифт", "Golem": "Голем", "Slayer": "Охотник",
    "Demon Metal": "Демон-Металл", "Sealed Shrine": "Запечатанное Святилище",
    "Ancient Canine": "Древний Пёс", "Blue Abyss": "Синяя Бездна",
    "Latent Power": "Латентная Сила", "Skill Stone": "Камень Навыка",
    "Companion": "Компаньон", "Familiar": "Фамильяр",
    "Promotion": "Продвижение", "Awakening": "Пробуждение",
    "Stage": "Этап", "Orichalcum": "Орихалк",
    "Dark Realm": "Тёмное Царство", "Soul Crystal": "Кристалл Души",
    "Enhancement": "Усиление", "Transcendence": "Трансценденция",
    "Artifact": "Артефакт", "Rune": "Руна",
    "Constellation": "Созвездие", "Talent": "Талант",
    "Ascension": "Вознесение", "Breakthrough": "Прорыв",
    "Refine": "Улучшение", "Forge": "Ковка",
    "Mount": "Маунт", "Pet": "Питомец",
    "Dungeon": "Подземелье", "Raid": "Рейд",
    "Boss": "Босс", "Arena": "Арена",
    "Guild": "Гильдия", "Alliance": "Альянс",
    "Territory": "Территория", "Siege": "Осада",
}


def discord_get(path: str) -> tuple[int, any]:
    """GET запрос к Discord API с retry."""
    url = f"{DISCORD_API}{path}"
    req = urllib.request.Request(url, headers=HEADERS_DISCORD)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, context=_ssl_ctx, timeout=20) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            if e.code == 429:
                retry_after = 5
                try:
                    retry_after = json.loads(body).get("retry_after", 5)
                except Exception:
                    pass
                print(f"      Rate limited, waiting {retry_after}s...")
                time.sleep(retry_after + 0.5)
                continue
            try:
                return e.code, json.loads(body)
            except Exception:
                return e.code, body
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
                continue
            return 0, str(e)
    return 0, "max retries"


def backend_request(path: str, data: dict | None, token: str, method: str = "PUT") -> dict:
    """HTTP запрос к бэкенду BlackRose."""
    url = f"{BACKEND_URL}{path}"
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, context=_ssl_ctx, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        return {"error": f"HTTP {e.code}: {body[:300]}"}
    except Exception as e:
        return {"error": str(e)}


def ingest_guide(guide_key: str, cat_key: str, cat_title: str, title: str, text: str, photos: list, videos: list, sort_order: int) -> dict:
    """Безопасный импорт гайда через эндпоинт webhook ingest."""
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
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Ingest-Token", "dev_ingest_token")
    try:
        with urllib.request.urlopen(req, context=_ssl_ctx, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_str = e.read().decode("utf-8", errors="ignore")
        return {"error": f"HTTP {e.code}: {body_str[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def backend_login() -> str:
    """Логин в админку, возвращает JWT-токен (или пустую строку при сбое)."""
    url = f"{BACKEND_URL}/api/auth/admin-login"
    body = json.dumps({"username": ADMIN_USER, "password": ADMIN_PASS}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, context=_ssl_ctx, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            token = data.get("token")
            return token or ""
    except urllib.error.HTTPError as e:
        print(f"  Внимание: Ошибка логина (HTTP {e.code}): {e.read().decode('utf-8', errors='ignore')[:100]}")
        return ""
    except Exception as e:
        print(f"  Внимание: Ошибка логина: {e}")
        return ""


def sanitize_discord_markdown(text: str) -> str:
    """Очистка Discord-маркдауна + эмодзи + спойлеры + ссылки."""
    if not text:
        return ""
    # Упоминания
    text = re.sub(r'<@&?\d+>', '', text)
    text = re.sub(r'<#\d+>', '', text)
    # Кастом-эмодзи Discord -> прямая ссылка на CDN Discord!
    text = re.sub(r'<a?:(\w+):(\d+)>', r'{{https://cdn.discordapp.com/emojis/\2.webp?size=48&quality=lossless}}', text)
    # Спойлеры → <details>
    text = re.sub(r'\|\|(.+?)\|\|', r'<details><summary>Спойлер</summary>\1</details>', text, flags=re.DOTALL)
    # Внутренние Discord-ссылки → [[discord_id|label]]
    def _convert_markdown_discord_link(m):
        label = m.group(1).strip() or "Ссылка на гайд"
        url = m.group(2)
        parts = url.rstrip("/").split("/")
        ch_id = parts[-1] if len(parts) >= 1 else parts[-2]
        return f"[[discord_{ch_id}|{label}]]"

    text = re.sub(
        r'\[([^\]]*)\]\((https?://(?:discord\.com|discordapp\.com)/channels/[^)]+)\)',
        _convert_markdown_discord_link,
        text
    )
    # Простые Discord channel links без markdown
    text = re.sub(
        r'https?://(?:discord\.com|discordapp\.com)/channels/\d+/(\d+)(?:/\d+)?',
        r'[[discord_\1|Ссылка на гайд]]',
        text
    )
    return text.strip()


def _translate_single_chunk(text: str) -> str:
    """Перевод одного блока (до 3000 символов) через Google GTX с защитой глоссария."""
    if not text or len(text.strip()) < 10:
        return text

    placeholders = {}
    masked = text
    idx = 0
    for en, ru in GAMING_GLOSSARY.items():
        pattern = re.compile(re.escape(en), re.IGNORECASE)
        if pattern.search(masked):
            ph = f"__GLOSS{idx}__"
            masked = pattern.sub(ph, masked)
            placeholders[ph] = ru
            idx += 1

    code_blocks = {}
    cidx = 0
    for pat in [r'```[\s\S]*?```', r'`[^`]+`', r'\{\{[^}]+\}\}', r'\[\[[^\]]+\]\]',
                r'https?://\S+', r'<details>[\s\S]*?</details>']:
        for m in re.finditer(pat, masked):
            ph = f"XZYBLOCK{cidx}XZY"
            code_blocks[ph] = m.group()
            masked = masked.replace(m.group(), ph, 1)
            cidx += 1

    try:
        encoded = urllib.parse.quote(masked)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ru&dt=t&q={encoded}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, context=_ssl_ctx, timeout=12) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            translated = "".join(seg[0] for seg in result[0] if seg and seg[0])
    except Exception as e:
        print(f"      [WARN] Перевод фрагмента пропущен ({e}), сохраняем оригинал")
        translated = masked

    for ph, val in code_blocks.items():
        translated = re.sub(re.escape(ph), lambda _m, v=val: v, translated, flags=re.IGNORECASE)
    for ph, val in placeholders.items():
        translated = re.sub(re.escape(ph), lambda _m, v=val: v, translated, flags=re.IGNORECASE)

    return translated


def translate_text(text: str) -> str:
    """Перевод EN→RU с разбиением на параграфы без обрезок длины."""
    if not text or len(text.strip()) < 10:
        return text

    paragraphs = text.split("\n\n")
    translated_chunks = []
    current_chunk = ""

    for p in paragraphs:
        if len(current_chunk) + len(p) + 2 <= 2500:
            current_chunk += ("\n\n" if current_chunk else "") + p
        else:
            if current_chunk:
                translated_chunks.append(_translate_single_chunk(current_chunk))
            current_chunk = p

    if current_chunk:
        translated_chunks.append(_translate_single_chunk(current_chunk))

    return "\n\n".join(translated_chunks)


def translate_category_name(name: str) -> str:
    """Перевод названия категории Discord → русский."""
    lower = name.lower().strip()
    if lower in CATEGORY_NAME_MAP:
        return CATEGORY_NAME_MAP[lower]
    # Попробовать без спецсимволов
    clean = re.sub(r'[^\w\s]', '', lower).strip()
    if clean in CATEGORY_NAME_MAP:
        return CATEGORY_NAME_MAP[clean]
    # Перевести через Google
    return translate_text(name)


def slugify(text: str) -> str:
    """Генерация ключа."""
    s = text.lower().strip()
    # Транслитерация кириллицы
    translit = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    }
    result = ""
    for ch in s:
        if ch in translit:
            result += translit[ch]
        elif ch.isalnum() or ch in '-_':
            result += ch
        elif ch.isspace():
            result += '_'
    result = re.sub(r'_+', '_', result).strip('_')
    return result[:55] or "general"


def fetch_all_forum_threads(channel_id: str) -> list[dict]:
    """Получить ВСЕ треды форум-канала (active + archived с пагинацией)."""
    threads = []
    seen_ids = set()

    # 1. Active threads
    status, data = discord_get(f"/guilds/{GUILD_ID}/threads/active")
    if status == 200 and isinstance(data, dict):
        for th in data.get("threads", []):
            if str(th.get("parent_id")) == channel_id and th["id"] not in seen_ids:
                threads.append(th)
                seen_ids.add(th["id"])

    # 2. Archived threads с пагинацией
    before_ts = None
    for _ in range(20):  # макс 20 страниц
        path = f"/channels/{channel_id}/threads/archived/public"
        if before_ts:
            path += f"?before={before_ts}"

        time.sleep(0.5)
        status, data = discord_get(path)
        if status != 200 or not isinstance(data, dict):
            break

        page_threads = data.get("threads", [])
        if not page_threads:
            break

        for th in page_threads:
            if th["id"] not in seen_ids:
                threads.append(th)
                seen_ids.add(th["id"])

        if not data.get("has_more", False):
            break

        # Get last thread's archive timestamp for pagination
        last = page_threads[-1]
        meta = last.get("thread_metadata", {})
        before_ts = meta.get("archive_timestamp")
        if not before_ts:
            break

    return threads


def fetch_all_messages(channel_id: str, limit: int = 200) -> list[dict]:
    """Получить ВСЕ сообщения канала/треда с пагинацией."""
    all_msgs = []
    before_id = None

    for _ in range(limit // 50 + 1):
        path = f"/channels/{channel_id}/messages?limit=50"
        if before_id:
            path += f"&before={before_id}"

        time.sleep(0.4)
        status, data = discord_get(path)
        if status != 200 or not isinstance(data, list) or not data:
            break

        all_msgs.extend(data)
        if len(data) < 50:
            break
        before_id = data[-1]["id"]

    all_msgs.sort(key=lambda x: x.get("id", ""))
    return all_msgs


def format_message_with_inline_media(m: dict) -> str:
    """Встроить прикрепленные фото и видео прямо в текст сообщения."""
    content = m.get("content", "").strip()
    media_lines = []

    # 1. Attachments
    for att in m.get("attachments", []):
        url = att.get("url", "")
        if not url:
            continue
        fname = att.get("filename", "").lower()
        if any(fname.endswith(ext) for ext in ('.mp4', '.webm', '.mov', '.mkv')):
            media_lines.append(f"\n\n[Video: Видеоинструкция]({url})\n\n")
        elif any(fname.endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
            media_lines.append(f"\n\n![Скриншот]({url})\n\n")

    # 2. Embeds
    for emb in m.get("embeds", []):
        if emb.get("video"):
            v_url = emb["video"].get("url")
            if v_url:
                media_lines.append(f"\n\n[Video: Видеоинструкция]({v_url})\n\n")
        elif emb.get("image"):
            i_url = emb["image"].get("url")
            if i_url:
                media_lines.append(f"\n\n![Скриншот]({i_url})\n\n")

    media_str = "".join(media_lines)
    if content and media_str:
        return f"{content}\n{media_str}"
    elif content:
        return content
    elif media_str:
        return media_str.strip()
    return ""


def extract_media_from_messages(msgs: list[dict]) -> tuple[list[str], list[str]]:
    """Извлечь все фото и видео из списка сообщений."""
    photos = []
    videos = []
    seen = set()

    for m in msgs:
        # Attachments
        for att in m.get("attachments", []):
            url = att.get("url", "")
            if not url or url in seen:
                continue
            seen.add(url)
            ct = att.get("content_type", "")
            fname = att.get("filename", "").lower()
            if any(fname.endswith(ext) for ext in ('.mp4', '.webm', '.mov', '.mkv')):
                videos.append(url)
            elif any(fname.endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                photos.append(url)
            elif ct.startswith("image/"):
                photos.append(url)
            elif ct.startswith("video/"):
                videos.append(url)
            else:
                photos.append(url)  # default to photo

        # Embeds
        for emb in m.get("embeds", []):
            if not isinstance(emb, dict):
                continue
            if emb.get("image") and emb["image"].get("url"):
                url = emb["image"]["url"]
                if url not in seen:
                    photos.append(url)
                    seen.add(url)
            if emb.get("thumbnail") and emb["thumbnail"].get("url"):
                url = emb["thumbnail"]["url"]
                if url not in seen:
                    photos.append(url)
                    seen.add(url)
            if emb.get("video") and emb["video"].get("url"):
                url = emb["video"]["url"]
                if url not in seen:
                    videos.append(url)
                    seen.add(url)

        # YouTube links in content
        content = m.get("content", "")
        for yt_match in re.finditer(r'https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)', content):
            yt_url = f"https://www.youtube.com/watch?v={yt_match.group(1)}"
            if yt_url not in seen:
                videos.append(yt_url)
                seen.add(yt_url)

    return photos, videos


# ═══════════════════════════════════════════════════════════════
# 🚀  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("  BlackRose Discord Full Sync v2.0")
    print("  Полная автосинхронизация Discord -> Сайт")
    print("=" * 65)

    # Проверка
    if not DISCORD_TOKEN or len(DISCORD_TOKEN) < 20:
        print("\n  Укажите DISCORD_TOKEN!")
        sys.exit(1)

    HEADERS_DISCORD["Authorization"] = DISCORD_TOKEN.strip().strip("\"'")

    # ── 0. Проверка Discord токена ──
    print("\n[0/4] Проверка Discord токена...")
    s, me = discord_get("/users/@me")
    if s != 200:
        print(f"  Discord токен невалидный (HTTP {s})")
        print("  Получите новый: DevTools -> Console -> скрипт из README")
        sys.exit(1)
    print(f"  OK: {me.get('username', '?')}#{me.get('discriminator', '0')}")

    # ── 0.1 Логин в бэкенд ──
    print(f"\n  Логин в бэкенд ({BACKEND_URL})...")
    jwt = backend_login()
    print(f"  JWT: {jwt[:20]}...****")

    # ── 0.2 Очистка сайта ──
    print("\n[0.5/4] Очистка всех категорий и гайдов на сайте...")
    nuke_result = backend_request("/api/admin/nuke-all", None, jwt, method="DELETE")
    if "error" in nuke_result:
        print(f"  Ошибка очистки: {nuke_result['error'][:200]}")
        print("  Продолжаю без очистки...")
    else:
        print(f"  Очищено: {nuke_result.get('categories_deleted', 0)} категорий, "
              f"{nuke_result.get('synced_cleared', 0)} синхронизированных записей")

    # ── 1. Считывание структуры Discord ──
    print("\n[1/4] Считывание структуры Discord-сервера...")
    s, channels = discord_get(f"/guilds/{GUILD_ID}/channels")
    if s != 200:
        print(f"  Ошибка получения каналов (HTTP {s}): {str(channels)[:100]}")
        sys.exit(1)

    # Группировка
    categories_raw = sorted(
        [c for c in channels if c.get("type") == 4],
        key=lambda x: x.get("position", 0)
    )
    print(f"  Найдено {len(categories_raw)} категорий Discord")

    # Построение дерева: Работаем СТРОГО с категорией Slayerpedia
    tree = []
    import unicodedata
    for cat in categories_raw:
        cat_name = cat["name"].strip()
        cat_name_clean = unicodedata.normalize('NFKD', cat_name).lower().strip()
        cat_id = cat["id"]

        # РАБОТАЕМ ТОЛЬКО С SLAYERPEDIA! Всё остальное проходит мимо.
        if "slayerpedia" not in cat_name_clean:
            print(f"  [SKIP] {cat_name} (пропускаем, работаем только с Slayerpedia)")
            continue

        # Дочерние каналы из Slayerpedia (forum channels & text channels)
        child_channels = [
            c for c in channels
            if c.get("parent_id") == cat_id
            and c.get("type") in GUIDE_CHANNEL_TYPES
            and c.get("name", "").lower() not in {"slayerpedia-feedback", "slayerpedia-change-log", "disclaimer"}
        ]

        print(f"  🎯 НАЙДЕНА КАТЕГОРИЯ SLAYERPEDIA! Содержит {len(child_channels)} каналов-разделов.")

        # Каждый канал внутри Slayerpedia становится отдельной Категорией на сайте
        for ch in child_channels:
            ch_name = ch["name"].strip()
            # Очистка и перевод названия канала (напр. "equipment" -> "Экипировка", "skills" -> "Навыки")
            clean_ch_name = re.sub(r'^[^\w\s]+', '', ch_name).strip()
            ru_cat_name = translate_category_name(clean_ch_name or ch_name)
            cat_key = slugify(clean_ch_name or ch_name)

            tree.append({
                "discord_id": ch["id"],
                "name_en": ch_name,
                "name_ru": ru_cat_name,
                "key": cat_key,
                "channels": [ch],
            })
            print(f"    ├─ Раздел: «{ch_name}» -> Категория сайта: «{ru_cat_name}» (/{cat_key})")

    if not tree:
        print("\n  Нет категорий с гайдами для импорта!")
        sys.exit(1)

    # ── 2. Создание категорий на сайте ──
    print(f"\n[2/4] Создание {len(tree)} категорий на сайте...")
    for idx, cat in enumerate(tree):
        result = ingest_guide(
            guide_key=f"cat_init_{cat['key']}",
            cat_key=cat["key"],
            cat_title=cat["name_ru"],
            title=f"Инициализация {cat['name_ru']}",
            text="Категория инициализирована",
            photos=[],
            videos=[],
            sort_order=idx
        )
        if "error" in result:
            print(f"  Ошибка: {cat['name_ru']}: {result['error'][:100]}")
        else:
            print(f"  [{idx+1}/{len(tree)}] {cat['name_ru']} -> /{cat['key']}")
            print(f"  [{idx+1}/{len(tree)}] {cat['name_ru']} -> /{cat['key']}")

    # ── 3. Импорт всех гайдов ──
    print(f"\n[3/4] Импорт гайдов...")
    total_imported = 0
    total_skipped = 0
    total_errors = 0

    for cat in tree:
        cat_key = cat["key"]
        cat_name = cat["name_ru"]
        print(f"\n  === {cat_name} ({len(cat['channels'])} каналов) ===")

        for ch in cat["channels"]:
            ch_id = ch["id"]
            ch_type = ch["type"]
            ch_name = ch["name"]
            time.sleep(0.5)

            # ── FORUM CHANNEL (type=15) ──
            if ch_type == 15:
                print(f"\n    [FORUM] {ch_name}")
                threads = fetch_all_forum_threads(ch_id)
                print(f"    Найдено {len(threads)} тредов")

                for ti, th in enumerate(threads):
                    tid = th["id"]
                    tname = th.get("name", "Гайд")
                    time.sleep(0.5)

                    msgs = fetch_all_messages(tid)
                    if not msgs:
                        total_skipped += 1
                        continue

                    # Объединить все сообщения со встроенными в текст фото и видео
                    msg_blocks = [format_message_with_inline_media(m) for m in msgs]
                    combined = "\n\n".join(b for b in msg_blocks if b.strip())
                    if not combined.strip() or len(combined.strip()) < 20:
                        total_skipped += 1
                        continue

                    # Обработка
                    clean = sanitize_discord_markdown(combined)
                    translated = translate_text(clean)
                    photos, videos = extract_media_from_messages(msgs)
                    guide_key = f"discord_{tid}"

                    result = ingest_guide(
                        guide_key=guide_key,
                        cat_key=cat_key,
                        cat_title=cat_name,
                        title=tname,
                        text=translated,
                        photos=photos,
                        videos=videos,
                        sort_order=ti
                    )

                    if "error" in result:
                        total_errors += 1
                        print(f"      [{ti+1}/{len(threads)}] FAIL {tname[:40]}: {result['error'][:60]}")
                    else:
                        total_imported += 1
                        media_info = f" ({len(photos)}p/{len(videos)}v)" if photos or videos else ""
                        print(f"      [{ti+1}/{len(threads)}] OK: {tname[:50]}{media_info}")

            # ── TEXT / ANNOUNCE CHANNEL (type=0, 5) ──
            else:
                print(f"\n    [TEXT] {ch_name}")
                msgs = fetch_all_messages(ch_id, limit=100)
                guide_msgs = [m for m in msgs if len(m.get("content", "")) >= 80 or len(m.get("attachments", [])) > 0]
                print(f"    Найдено {len(guide_msgs)} сообщений-гайдов (из {len(msgs)} всего)")

                for mi, msg in enumerate(guide_msgs):
                    mid = msg["id"]
                    msg_text = format_message_with_inline_media(msg)
                    clean = sanitize_discord_markdown(msg_text)
                    translated = translate_text(clean)

                    # Заголовок — первая строка
                    first_line = clean.split("\n")[0].strip("# ").strip()
                    title = first_line[:80] if first_line else f"Гайд {mid}"

                    photos, videos = extract_media_from_messages([msg])
                    guide_key = f"discord_{mid}"

                    result = ingest_guide(
                        guide_key=guide_key,
                        cat_key=cat_key,
                        cat_title=cat_name,
                        title=title,
                        text=translated,
                        photos=photos,
                        videos=videos,
                        sort_order=mi
                    )

                    if "error" in result:
                        total_errors += 1
                        print(f"      [{mi+1}/{len(guide_msgs)}] FAIL: {title[:40]}: {result['error'][:60]}")
                    else:
                        total_imported += 1
                        print(f"      [{mi+1}/{len(guide_msgs)}] OK: {title[:50]}")

                    time.sleep(0.3)

    # ── 4. Регистрация каналов для прослушки ──
    print(f"\n[4/4] Регистрация каналов для прослушки...")
    registered = 0
    for cat in tree:
        for ch in cat["channels"]:
            result = backend_request("/api/admin/discord-sync/channels", {
                "channel_id": str(ch["id"]),
                "channel_name": ch["name"],
                "category_key": cat["key"],
                "auto_translate": True,
            }, jwt, method="POST")
            if "error" not in result:
                registered += 1
            time.sleep(0.2)
    print(f"  Зарегистрировано {registered} каналов для прослушки")

    # Сохранить токен и запустить прослушку
    start_result = backend_request("/api/admin/discord-sync/start", {
        "user_token": DISCORD_TOKEN,
    }, jwt, method="POST")
    if "error" not in start_result:
        print("  Токен сохранён, WebSocket прослушка запущена!")
    else:
        print(f"  Токен сохранён, но прослушка не запустилась: {start_result.get('error', '')[:100]}")
        print("  (Прослушка автозапустится при перезагрузке бэкенда)")

    # ── Итог ──
    print("\n" + "=" * 65)
    print(f"  ГОТОВО!")
    print(f"  Категорий создано:    {len(tree)}")
    print(f"  Гайдов импортировано: {total_imported}")
    print(f"  Пропущено:           {total_skipped}")
    print(f"  Ошибок:              {total_errors}")
    print(f"  Каналов на прослушке: {registered}")
    print("=" * 65)


if __name__ == "__main__":
    main()
