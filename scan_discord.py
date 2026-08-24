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

# Ваш Discord User Token (из переменной окружения DISCORD_TOKEN или файла .env)
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
    "resources": "Ресурсы и Таблицы",
    "faq": "Часто Задаваемые Вопросы",
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
    # Духи и питомцы
    "Strong Spirits": "Сильные Духи",
    "Spirits": "Духи",
    "Spirit": "Дух",
    "Fountain of Circulation": "Фонтан Циркуляции",
    "Forest of Circulation": "Лес Циркуляции",
    "Familiars": "Фамильяры",
    "Familiar": "Фамильяр",
    "Fams": "Фамильяры",
    "Fam": "Фамильяр",
    "Salamander": "Саламандра",
    "Sala": "Саламандра",
    "Noah": "Ной",
    "Golem": "Голем",
    "Draco": "Драко",
    "Shadow Beast": "Теневой Зверь",
    "Beasts": "Звери",
    "Beast": "Зверь",
    
    # Механики боя и кулдауны
    "Cooldowns": "Перезарядка (КД)",
    "Cooldown": "Перезарядка (КД)",
    "Bossing": "Битвы с боссами",
    "bossing": "битвы с боссами",
    "Bosses": "Боссы",
    "Boss": "Босс",
    "Raves": "Рейвы",
    "Rave": "Рейв",
    "Rage": "Ярость",
    "Meditation": "Медитация",
    "Demon Hunter": "Охотник на Демонов (DH)",
    "DH": "DH (Demon Hunter)",
    "Life Steal": "Похищение жизни (Вампиризм)",
    "Stuns": "Оглушения",
    "Stun": "Оглушение (Стан)",
    "HP bars": "Полоски HP",
    "HP bar": "Полоска HP",
    "HP": "HP",
    "Shield": "Щит",
    "Attack Speed": "Скорость атаки",
    "Attack": "Атака",
    "Pity System": "Система Гаранта (Pity)",
    "Pity": "Гарант (Pity)",
    "Summons": "Призывы",
    "Summon": "Призыв",
    "Tornado Mark": "Метка Торнадо",
    "Torando Mark": "Метка Торнадо",
    "Tornado": "Торнадо",
    "Torando": "Торнадо",
    "Statues": "Статуи",
    "Statue": "Статуя",
    "Late Game": "Поздняя игра (Late Game)",
    "late game": "поздней игры",
    "Early Game": "Ранняя игра (Early Game)",
    "early game": "ранней игры",
    "Mid Game": "Средняя игра (Mid Game)",
    "mid game": "средней игры",
    
    # Продвижения (Promotions)
    "Blitz Gold": "Блиц Голд (Blitz Gold)",
    "Diadust": "Диадаст (Diadust)",
    "Gigarock": "Гигарок (Gigarock)",
    "Eldenwood": "Элденвуд (Eldenwood)",
    "Auroite": "Ауроит (Auroite)",
    "Eisenhart": "Эйзенхарт (Eisenhart)",
    "Infinaut": "Инфинавт (Infinaut)",
    "Ragnablood": "Рагнаблад (Ragnablood)",
    "Ancient Canine": "Древний Пёс (Ancient Canine)",
    "Dragonos": "Драгонос (Dragonos)",
    "Demon Metal": "Демон-Металл (Demon Metal)",
    "Cyclos": "Циклос (Cyclos)",
    "Warfrost": "Варфрост (Warfrost)",
    "Dark Nox": "Темный Нокс (Dark Nox)",
    "Blue Abyss": "Синяя Бездна (Blue Abyss)",
    "Black Mythril": "Черный Мифрил (Black Mythril)",
    "Mithril": "Мифрил",
    "Arcanite": "Арканит",
    "Adamant": "Адамант",
    "Orichalcum": "Орихалк",
    "Ether": "Эфир",
    "Bronze": "Бронза",
    "Silver": "Серебро",
    "Gold": "Золото",
    "Iron": "Железо",
    "Stone": "Камень",
    
    # Локации и контент
    "Sealed Shrine": "Запечатанное Святилище",
    "Closed Mine": "Закрытая Шахта",
    "Training Cave": "Пещера Тренировок",
    "Dragon Valley": "Долина Драконов",
    "Dimensional Rift": "Пространственный Рифт",
    "Rift": "Рифт",
    "Latent Power": "Латентная Сила",
    "Skill Stone": "Камень Навыка",
    "Soul Weapons": "Оружие Души",
    "Soul Weapon": "Оружие Души",
    "Light Shard": "Осколок Света",
    "Memory Tree": "Дерево Памяти",
    "Training Diary": "Дневник Тренировок",
    "Constellation": "Созвездие",
    "Immortal Skills": "Бессмертные Навыки",
    "Immortal Skill": "Бессмертный Навык",
    "Skill Mastery": "Мастерство Навыков",
    "Skill Refinement": "Улучшение Навыков",
    "Slayerpedia": "Охотникпедия",
    "Slayer": "Охотник",
    "Promotions": "Продвижение",
    "Promotion": "Продвижение",
    "Awakening": "Пробуждение",
    "Stages": "Этапы",
    "Stage": "Этап",
    "Enhancement": "Усиление",
    "Transcendence": "Трансценденция",
    "Artifact": "Артефакт",
    "Rune": "Руна",
    "Talent": "Талант",
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
    """Безопасный импорт гайда через эндпоинт webhook ingest с автоматическим retry."""
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

    last_err = ""
    for attempt in range(3):
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("X-Ingest-Token", "dev_ingest_token")
        try:
            with urllib.request.urlopen(req, context=_ssl_ctx, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body_str = e.read().decode("utf-8", errors="ignore")
            last_err = f"HTTP {e.code}: {body_str[:200]}"
            if e.code in (500, 502, 503, 504, 429) and attempt < 2:
                time.sleep(1.5 * (attempt + 1))
                continue
            return {"error": last_err}
        except Exception as e:
            last_err = str(e)
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
                continue
            return {"error": last_err}
    return {"error": last_err}


MEDIA_MAP_FILE = "media_url_map.json"
_media_url_cache = {}
if os.path.exists(MEDIA_MAP_FILE):
    try:
        with open(MEDIA_MAP_FILE, "r", encoding="utf-8") as f:
            _media_url_cache = json.load(f)
    except Exception:
        pass

def save_media_cache():
    try:
        with open(MEDIA_MAP_FILE, "w", encoding="utf-8") as f:
            json.dump(_media_url_cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def persist_media_url(raw_url: str, admin_jwt: str = "") -> str:
    """Скачивает медиафайл локально и загружает в постоянное облачное хранилище Hugging Face."""
    if not raw_url or not raw_url.startswith("http"):
        return raw_url

    if "huggingface.co" in raw_url:
        return raw_url

    canonical = raw_url.split("?")[0]
    if canonical in _media_url_cache:
        return _media_url_cache[canonical]

    # Обрабатываем Discord CDN ссылки
    if "discordapp." not in raw_url and "discord.com" not in raw_url:
        return raw_url

    if not admin_jwt:
        return raw_url

    for attempt in range(3):
        try:
            req = urllib.request.Request(raw_url, headers=HEADERS_DISCORD)
            with urllib.request.urlopen(req, context=_ssl_ctx, timeout=30) as resp:
                content = resp.read()
                content_type = resp.headers.get("Content-Type", "image/png")
            
            if not content:
                return raw_url

            filename = canonical.rsplit("/", 1)[-1] or "image.png"
            boundary = "----WebKitFormBoundary" + os.urandom(16).hex()
            
            body = bytearray()
            body.extend(f'--{boundary}\r\n'.encode('utf-8'))
            body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode('utf-8'))
            body.extend(f'Content-Type: {content_type}\r\n\r\n'.encode('utf-8'))
            body.extend(content)
            body.extend(f'\r\n--{boundary}--\r\n'.encode('utf-8'))

            up_req = urllib.request.Request(
                f"{BACKEND_URL}/api/admin/upload",
                data=bytes(body),
                method="POST",
                headers={
                    "Content-Type": f"multipart/form-data; boundary={boundary}",
                    "Authorization": f"Bearer {admin_jwt}",
                }
            )
            with urllib.request.urlopen(up_req, context=_ssl_ctx, timeout=40) as up_resp:
                up_data = json.loads(up_resp.read().decode("utf-8"))
                perm_url = up_data.get("url")
                if perm_url:
                    _media_url_cache[canonical] = perm_url
                    save_media_cache()
                    return perm_url
        except Exception as e:
            if attempt < 2:
                time.sleep(1.0 * (attempt + 1))
                continue
            print(f"      [MEDIA UPLOAD NOTICE] {canonical.split('/')[-1]}: {e}")

    return raw_url


def backend_login() -> str:
    """Логин в админку, возвращает JWT-токен (или пустую строку при сбое)."""
    # 1. Попытка через emergency login
    try:
        url = f"{BACKEND_URL}/api/auth/emergency-login"
        body = json.dumps({"emergency_key": "BlackRose_ProjectAdmin_Emergency_Key_2026_Secure_Key"}).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, context=_ssl_ctx, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("token"):
                return data["token"]
    except Exception:
        pass

    # 2. Логин по паролю
    url = f"{BACKEND_URL}/api/auth/admin-login"
    body = json.dumps({"username": ADMIN_USER, "password": ADMIN_PASS}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, context=_ssl_ctx, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            token = data.get("token")
            return token or ""
    except Exception as e:
        print(f"  Внимание: Ошибка логина: {e}")
        return ""


def sanitize_discord_markdown(text: str, admin_jwt: str = "") -> str:
    """Очистка Discord-маркдауна + сохранение эмодзи и изображений в постоянное хранилище."""
    if not text:
        return ""
    # Упоминания
    text = re.sub(r'<@&?\d+>', '', text)
    text = re.sub(r'<#\d+>', '', text)

    # Кастом-эмодзи Discord -> сохраняем в постоянное хранилище
    def _replace_emoji(match):
        emoji_id = match.group(2)
        raw_emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.webp?size=48&quality=lossless"
        perm_url = persist_media_url(raw_emoji_url, admin_jwt) if admin_jwt else raw_emoji_url
        return f"{{{{{perm_url}}}}}"

    text = re.sub(r'<a?:(\w+):(\d+)>', _replace_emoji, text)

    # Спойлеры → <details>
    text = re.sub(r'\|\|(.+?)\|\|', r'<details><summary>Спойлер</summary>\1</details>', text, flags=re.DOTALL)
    # Преобразуем прямые ссылки на Discord CDN в тексте в постоянные ссылки
    def _replace_discord_cdn(m):
        raw_url = m.group(0)
        perm = persist_media_url(raw_url, admin_jwt) if admin_jwt else raw_url
        clean_url = raw_url.split('?')[0].lower()
        if any(clean_url.endswith(ext) for ext in ('.mp4', '.webm', '.mov', '.avi')):
            return f"[Видео: Видеоинструкция]({perm})"
        if any(clean_url.endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.webp', '.gif')):
            return f"![Скриншот]({perm})"
        return perm

    text = re.sub(r'https?://(?:cdn\.discordapp\.com|media\.discordapp\.net)/attachments/\S+', _replace_discord_cdn, text)

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
    """Перевод одного блока (до 3000 символов) через Google GTX с надежной защитой плейсхолдеров и глоссария."""
    if not text or len(text.strip()) < 5:
        return text

    # Очистка мусорных пометок авторов
    text = re.sub(r'\(insert_[a-zA-Z0-9_\.]+\)', '', text)
    text = re.sub(r'insert_[a-zA-Z0-9_\.]+', '', text)

    # 1. ЗАЩИТА ВСЕХ URL, ПУТЕЙ, ИКОНОК И ТЕГОВ
    code_blocks = {}
    cidx = 0
    patterns = [
        r'```[\s\S]*?```',
        r'`[^`]+`',
        r'\{\{[^}]+\}\}',
        r'\[\[[^\]]+\]\]',
        r'\[(?:Видео|Video)[^\]]*\]\([^)]+\)',
        r'!\[[^\]]*\]\([^)]+\)',
AI_SYSTEM_PROMPT = """Ты — профессиональный игровой локализатор и эксперт по мобильной игре Slayer Legend.
Твоя задача — качественно и естественно перевести руководство по игре с английского на русский язык.

КРИТИЧЕСКИЕ ПРАВИЛА:
1. СОХРАНЯЙ ВСЮ РАЗМЕТКУ И МЕДИА-ТЕГИ:
   - Ссылки [Текст](url) — переводи только текст ссылки, URL оставляй без изменений!
   - Медиа-теги ![...](url), видео [Video: ...](url) — сохраняй в точности.
   - Иконки и эмодзи {{...}}, <:name:id>, <a:name:id>, юникод-эмодзи — НЕ удаляй, НЕ изменяй, НЕ переводи внутри скобок!
   - Код `...`, блоки кода ```...```, заголовки #, ##, списки -, * — сохраняй структуру Markdown.
   - Таблицы Markdown | col | col | — сохраняй структуру колонок и разделители.
2. ИСПОЛЬЗУЙ ИГРОВОЙ СЛЕНГ И ТЕРМИНОЛОГИЮ SLAYER LEGEND:
   - Rave -> Рейв
   - Rage -> Ярость
   - Spirits -> Духи
   - Familiars -> Фамильяры
   - Promotion -> Продвижение
   - Latent / Latent Power -> Латентка / Скрытая сила
   - CD / Cooldown -> КД (перезарядка)
   - DPS -> ДПС (урон в секунду)
   - Boss -> Босс
   - Mobs -> Мобы
   - Beast -> Зверь
   - Stage -> Этап
   - Breakthrough -> Прорыв
   - WoG / Wrath of Gods -> Гнев богов (WoG)
   - Flowing Blade -> Текущий клинок
   - Warrior Burn -> Пылающий воин
   - Strong Current -> Сильное течение
   - Earth's Will -> Воля земли
   - Auto -> Авто-режим / Авто
3. Перевод должен быть естественным, чистым и понятным русскоязычным игрокам.
4. Выводи ТОЛЬКО готовый переведенный Markdown текст без вступительных или заключительных фраз."""


def _translate_ai_orcarouter(text: str, api_key: str) -> str | None:
    try:
        url = "https://api.orcarouter.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        for model in ["meta-llama/llama-3.3-70b-instruct:free", "deepseek/deepseek-chat:free", "qwen/qwen-2.5-72b-instruct:free"]:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": AI_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Текст для перевода:\n{text}"}
                ],
                "temperature": 0.1,
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, context=_ssl_ctx, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return _post_process_translation(data["choices"][0]["message"]["content"].strip())
    except Exception:
        pass
    return None


def _translate_ai_openrouter(text: str, api_key: str) -> str | None:
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        for model in ["deepseek/deepseek-chat:free", "meta-llama/llama-3.3-70b-instruct:free", "google/gemini-2.0-flash-exp:free"]:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": AI_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Текст для перевода:\n{text}"}
                ],
                "temperature": 0.1,
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, context=_ssl_ctx, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return _post_process_translation(data["choices"][0]["message"]["content"].strip())
    except Exception:
        pass
    return None


def _translate_ai_nvidia(text: str, api_key: str) -> str | None:
    try:
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        for model in ["meta/llama-3.3-70b-instruct", "deepseek-ai/deepseek-v3", "qwen/qwen2.5-72b-instruct"]:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": AI_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Текст для перевода:\n{text}"}
                ],
                "temperature": 0.1,
                "max_tokens": 4096,
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, context=_ssl_ctx, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return _post_process_translation(data["choices"][0]["message"]["content"].strip())
    except Exception:
        pass
    return None


def _translate_ai_gemini(text: str, api_key: str) -> str | None:
    try:
        for model in ["gemini-2.5-flash", "gemini-1.5-flash"]:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": f"{AI_SYSTEM_PROMPT}\n\nТекст для перевода:\n{text}"}]}],
                "generationConfig": {"temperature": 0.1, "maxOutputTokens": 4096}
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, context=_ssl_ctx, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates and candidates[0].get("content", {}).get("parts"):
                    res = candidates[0]["content"]["parts"][0].get("text", "").strip()
                    if res:
                        return _post_process_translation(res)
    except Exception:
        pass
    return None


def _translate_ai_deepseek(text: str, api_key: str) -> str | None:
    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": AI_SYSTEM_PROMPT},
                {"role": "user", "content": f"Текст для перевода:\n{text}"}
            ],
            "temperature": 0.1,
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, context=_ssl_ctx, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return _post_process_translation(data["choices"][0]["message"]["content"].strip())
    except Exception:
        pass
    return None


def _translate_ai_groq(text: str, api_key: str) -> str | None:
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": AI_SYSTEM_PROMPT},
                {"role": "user", "content": f"Текст для перевода:\n{text}"}
            ],
            "temperature": 0.1,
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, context=_ssl_ctx, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return _post_process_translation(data["choices"][0]["message"]["content"].strip())
    except Exception:
        pass
    return None


def _translate_ai_hf(text: str, token: str) -> str | None:
    try:
        model = "Qwen/Qwen2.5-72B-Instruct"
        url = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        prompt = f"<|im_start|>system\n{AI_SYSTEM_PROMPT}<|im_end|>\n<|im_start|>user\n{text}<|im_end|>\n<|im_start|>assistant\n"
        req = urllib.request.Request(url, data=json.dumps({"inputs": prompt, "parameters": {"max_new_tokens": 2048}}).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, context=_ssl_ctx, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            full = data[0].get("generated_text", "") if isinstance(data, list) else data.get("generated_text", "")
            res = full.split("<|im_start|>assistant\n")[-1].strip()
            if res:
                return _post_process_translation(res)
    except Exception:
        pass
    return None


def _post_process_translation(text: str) -> str:
    text = text.replace("![видео]", "![video]").replace("![изображение]", "![image]")
    text = text.replace("\ufffd", "")
    return text


def _translate_single_chunk(text: str) -> str:
    """Перевод отдельного фрагмента текста с защитой тегов."""
    # 1. AI LLM Providers
    orca_key = os.environ.get("ORCAROUTER_API_KEY", "")
    if orca_key:
        res = _translate_ai_orcarouter(text, orca_key)
        if res:
            return res

    openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
    if openrouter_key:
        res = _translate_ai_openrouter(text, openrouter_key)
        if res:
            return res

    nvidia_key = os.environ.get("NVIDIA_API_KEY", "")
    if nvidia_key:
        res = _translate_ai_nvidia(text, nvidia_key)
        if res:
            return res

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if gemini_key:
        res = _translate_ai_gemini(text, gemini_key)
        if res:
            return res

    deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if deepseek_key:
        res = _translate_ai_deepseek(text, deepseek_key)
        if res:
            return res

    groq_key = os.environ.get("GROQ_API_KEY", "")
    if groq_key:
        res = _translate_ai_groq(text, groq_key)
        if res:
            return res

    hf_token = os.environ.get("HF_TOKEN", "")
    if hf_token:
        res = _translate_ai_hf(text, hf_token)
        if res:
            return res

    # 2. Безопасный фоллбэк с маскированием
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
    return _post_process_translation(translated)


def translate_text(text: str) -> str:
    """Перевод EN→RU с разбиением на параграфы без обрезок длины."""
    if not text or len(text.strip()) < 10:
        return text

    # Если есть AI ключ, переводим весь текст целиком для сохранения контекста
    if os.environ.get("ORCAROUTER_API_KEY") or os.environ.get("OPENROUTER_API_KEY") or os.environ.get("NVIDIA_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("GROQ_API_KEY"):
        res = _translate_single_chunk(text)
        if res and res != text:
            return res

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

    # 3. Deep historical thread search via Guild Search API (находит ВСЕ треды, включая старые)
    time.sleep(0.5)
    search_path = f"/guilds/{GUILD_ID}/messages/search?channel_id={channel_id}"
    status, search_data = discord_get(search_path)
    if status == 200 and isinstance(search_data, dict):
        for th in search_data.get("threads", []):
            if th["id"] not in seen_ids:
                threads.append(th)
                seen_ids.add(th["id"])

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

    all_msgs.sort(key=lambda x: int(x.get("id", "0")) if str(x.get("id", "")).isdigit() else 0)
    return all_msgs


def format_message_with_inline_media(m: dict, admin_jwt: str = "") -> str:
    """Встроить прикрепленные фото и видео прямо в текст сообщения (с постоянными ссылками)."""
    content = m.get("content", "").strip()
    media_lines = []

    # 1. Attachments
    for att in m.get("attachments", []):
        raw_url = att.get("url", "")
        if not raw_url:
            continue
        url = persist_media_url(raw_url, admin_jwt) if admin_jwt else raw_url
        fname = att.get("filename", "").lower()
        if any(fname.endswith(ext) for ext in ('.mp4', '.webm', '.mov', '.mkv')):
            media_lines.append(f"\n\n[Video: Видеоинструкция]({url})\n\n")
        elif any(fname.endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
            media_lines.append(f"\n\n![Скриншот]({url})\n\n")

    # 2. Embeds (Images, Videos, and Rich Text/Fields)
    embed_text_parts = []
    for emb in m.get("embeds", []):
        if not isinstance(emb, dict):
            continue
        # Media in embeds
        if emb.get("video"):
            v_url = emb["video"].get("url")
            if v_url:
                perm_v = persist_media_url(v_url, admin_jwt) if admin_jwt else v_url
                media_lines.append(f"\n\n[Video: Видеоинструкция]({perm_v})\n\n")
        elif emb.get("image"):
            i_url = emb["image"].get("url")
            if i_url:
                perm_i = persist_media_url(i_url, admin_jwt) if admin_jwt else i_url
                media_lines.append(f"\n\n![Скриншот]({perm_i})\n\n")
        elif emb.get("thumbnail"):
            t_url = emb["thumbnail"].get("url")
            if t_url:
                perm_t = persist_media_url(t_url, admin_jwt) if admin_jwt else t_url
                media_lines.append(f"\n\n![Иконка]({perm_t})\n\n")

        # Rich text and fields in embeds
        emb_parts = []
        if emb.get("title"):
            title = emb["title"].strip()
            if emb.get("url"):
                emb_parts.append(f"### [{title}]({emb['url']})")
            else:
                emb_parts.append(f"### {title}")
        if emb.get("description"):
            emb_parts.append(emb["description"].strip())
        for field in emb.get("fields", []):
            if isinstance(field, dict):
                f_name = field.get("name", "").strip()
                f_val = field.get("value", "").strip()
                if f_name and f_val:
                    emb_parts.append(f"**{f_name}**\n{f_val}")
                elif f_val:
                    emb_parts.append(f_val)
        if emb.get("footer") and isinstance(emb["footer"], dict) and emb["footer"].get("text"):
            emb_parts.append(f"> *{emb['footer']['text'].strip()}*")
        if emb_parts:
            embed_text_parts.append("\n\n".join(emb_parts))

    combined_embed_text = "\n\n---\n\n".join(embed_text_parts)
    if combined_embed_text:
        content = f"{content}\n\n{combined_embed_text}".strip() if content else combined_embed_text

    media_str = "".join(media_lines)
    if content and media_str:
        return f"{content}\n{media_str}"
    elif content:
        return content
    elif media_str:
        return media_str.strip()
    return ""


def extract_media_from_messages(msgs: list[dict], admin_jwt: str = "") -> tuple[list[str], list[str]]:
    """Извлечь все фото и видео из списка сообщений и сохранить их в постоянное хранилище."""
    photos = []
    videos = []
    seen = set()

    for m in msgs:
        # Attachments
        for att in m.get("attachments", []):
            raw_url = att.get("url", "")
            if not raw_url or raw_url in seen:
                continue
            seen.add(raw_url)
            url = persist_media_url(raw_url, admin_jwt) if admin_jwt else raw_url
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
                photos.append(url)

        # Embeds
        for emb in m.get("embeds", []):
            if not isinstance(emb, dict):
                continue
            if emb.get("image") and emb["image"].get("url"):
                raw_url = emb["image"]["url"]
                if raw_url not in seen:
                    seen.add(raw_url)
                    url = persist_media_url(raw_url, admin_jwt) if admin_jwt else raw_url
                    photos.append(url)
            if emb.get("thumbnail") and emb["thumbnail"].get("url"):
                raw_url = emb["thumbnail"]["url"]
                if raw_url not in seen:
                    seen.add(raw_url)
                    url = persist_media_url(raw_url, admin_jwt) if admin_jwt else raw_url
                    photos.append(url)
            if emb.get("video") and emb["video"].get("url"):
                raw_url = emb["video"]["url"]
                if raw_url not in seen:
                    seen.add(raw_url)
                    url = persist_media_url(raw_url, admin_jwt) if admin_jwt else raw_url
                    videos.append(url)

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

    # Точный список официальных разделов Slayerpedia в порядке Discord:
    SLAYERPEDIA_ORDER = [
        ("beginner-guide", "Гайд для начинающих"),
        ("faq", "Часто Задаваемые Вопросы (FAQ)"),
        ("character", "Персонаж"),
        ("promotion-and-suit-recommendation", "Рекомендации Костюмов"),
        ("late-game-promotions", "Продвижение (Late Game)"),
        ("mid-game-promotions", "Продвижение (Mid Game)"),
        ("early-game-promotions", "Продвижение (Early Game)"),
        ("stage", "Этапы"),
        ("skills", "Навыки"),
        ("spirit", "Духи"),
        ("equipment", "Экипировка"),
        ("companion", "Компаньоны и Фамильяры"),
        ("adventure", "Приключения"),
        ("event-help", "Помощь по Ивентам"),
        ("resources", "Калькуляторы и Таблицы"),
        ("story-lore", "Сюжет и Лор"),
        ("shop", "Магазин"),
    ]

    # Находим категорию Slayerpedia
    slayerpedia_cat_id = None
    for c in channels:
        if c.get("type") == 4 and "slayerpedia" in c.get("name", "").lower():
            slayerpedia_cat_id = c["id"]
            break

    # Ищем каналы внутри Slayerpedia
    tree = []
    for slug, ru_title in SLAYERPEDIA_ORDER:
        matched_ch = None
        for ch in channels:
            # Проверяем каналы из категории Slayerpedia или по названию
            ch_name_clean = ch.get("name", "").lower().strip()
            if (ch.get("parent_id") == slayerpedia_cat_id or not slayerpedia_cat_id) and ch.get("type") in GUIDE_CHANNEL_TYPES:
                if ch_name_clean == slug or ch_name_clean.replace("-", "") == slug.replace("-", "") or (slug in ch_name_clean):
                    matched_ch = ch
                    break

        if matched_ch:
            tree.append({
                "discord_id": matched_ch["id"],
                "name_en": matched_ch["name"],
                "name_ru": ru_title,
                "key": slug,
                "channels": [matched_ch],
            })
            print(f"  [+] Раздел: «{matched_ch['name']}» -> Категория сайта: «{ru_title}» (/{slug})")
        else:
            print(f"  [-] Внимание: канал «{slug}» не найден в Discord")

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
                    msg_blocks = [format_message_with_inline_media(m, jwt) for m in msgs]
                    combined = "\n\n".join(b for b in msg_blocks if b.strip())
                    if not combined.strip() or len(combined.strip()) < 20:
                        total_skipped += 1
                        continue

                    # Обработка
                    clean = sanitize_discord_markdown(combined, jwt)
                    translated = translate_text(clean)
                    photos, videos = extract_media_from_messages(msgs, jwt)
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
                
                # Если это канал рекомендаций костюмов/продвижений — склеиваем все сообщения в 1 полный лонгрид
                if cat_key == "promotion-and-suit-recommendation" or "promotion-and-suit" in ch_slug:
                    sorted_msgs = sorted(msgs, key=lambda x: int(x.get("id", "0")))
                    full_text_parts = []
                    all_photos = []
                    all_videos = []
                    for m in sorted_msgs:
                        msg_text = format_message_with_inline_media(m, jwt)
                        clean = sanitize_discord_markdown(msg_text, jwt)
                        if clean.strip():
                            full_text_parts.append(clean.strip())
                        p, v = extract_media_from_messages([m], jwt)
                        all_photos.extend(p)
                        all_videos.extend(v)

                    full_raw_text = "\n\n---\n\n".join(full_text_parts)
                    translated = translate_text(full_raw_text)
                    guide_key = f"discord_merged_{ch_id}"
                    
                    result = ingest_guide(
                        guide_key=guide_key,
                        cat_key=cat_key,
                        cat_title=cat_name,
                        title="Рекомендации по Костюмам и Продвижению (Early / Mid / Late Game)",
                        text=translated,
                        photos=all_photos,
                        videos=all_videos,
                        sort_order=0
                    )
                    if "error" in result:
                        total_errors += 1
                        print(f"      [1/1] FAIL: Рекомендации по Костюмам: {result['error'][:60]}")
                    else:
                        total_imported += 1
                        print(f"      [1/1] OK: Рекомендации по Костюмам ({len(all_photos)}p/{len(all_videos)}v)")
                else:
                    guide_msgs = [m for m in msgs if len(m.get("content", "")) >= 80 or len(m.get("attachments", [])) > 0]
                    print(f"    Найдено {len(guide_msgs)} сообщений-гайдов (из {len(msgs)} всего)")

                    for mi, msg in enumerate(guide_msgs):
                        mid = msg["id"]
                        msg_text = format_message_with_inline_media(msg, jwt)
                        clean = sanitize_discord_markdown(msg_text, jwt)
                        translated = translate_text(clean)

                        # Заголовок — первая осмысленная текстовая строка
                        text_lines = [
                            line.strip("# ").strip() 
                            for line in clean.split("\n") 
                            if line.strip() and not line.strip().startswith(("![", "[Video:", "{{", "http://", "https://"))
                        ]
                        title = text_lines[0][:80] if text_lines else f"{cat_name} — Инфо #{mi+1}"

                        photos, videos = extract_media_from_messages([msg], jwt)
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
    jwt = backend_login() or jwt
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
