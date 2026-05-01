import html
import logging
import os
import re
from urllib.parse import quote

import aiohttp
import nh3
from database import get_sessionmaker, get_subscribers
from db_models import Guide
from dependencies import BOT_TOKEN
from icons import get_icon

logger = logging.getLogger("blackrose.utils")


def _miniapp_base_url() -> str:
    mini = os.getenv("MINIAPP_URL", "").strip()
    if mini:
        return mini.rstrip("/")
    front = os.getenv("FRONTEND_URL", "").strip()
    if front:
        return front.split(",")[0].strip().rstrip("/")
    return ""


async def _telegram_send_new_guide_notifications(
    guide_key: str,
    guide_title: str,
    category_key: str,
) -> tuple[int, int]:
    if not BOT_TOKEN:
        return 0, 0
    base = _miniapp_base_url()
    if not base:
        logger.warning(
            "push skipped: задайте MINIAPP_URL или FRONTEND_URL на backend для ссылок WebApp"
        )
        return 0, 0

    user_ids = await get_subscribers(category_key)
    if not user_ids:
        return 0, 0

    webapp_url = f"{base}?guide={quote(guide_key, safe='')}"
    safe_title = html.escape(guide_title, quote=False)
    safe_cat = html.escape(category_key, quote=False)
    msg_text = f"🆕 Новый гайд в <b>BlackRose</b>!\n\n📖 <b>{safe_title}</b>\nКатегория: {safe_cat}"
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "📖 Открыть гайд", "web_app": {"url": webapp_url}},
            ]
        ]
    }
    api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    sent: int = 0
    timeout = aiohttp.ClientTimeout(total=15)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for uid in user_ids:
                try:
                    async with session.post(
                        api,
                        json={
                            "chat_id": uid,
                            "text": msg_text,
                            "parse_mode": "HTML",
                            "reply_markup": reply_markup,
                        },
                    ) as r:
                        if r.status != 200:
                            body = await r.text()
                            logger.debug(
                                f"telegram sendMessage uid={uid} status={r.status} body={body[:200]}"
                            )
                        else:
                            sent += 1  # type: ignore
                except Exception as e:
                    logger.debug(f"telegram sendMessage uid={uid}: {e}")
    except Exception as e:
        logger.warning(f"_telegram_send_new_guide_notifications: {e}")
        return sent, len(user_ids)

    if sent < len(user_ids):
        logger.info(
            f"new guide push: sent {sent}/{len(user_ids)} for category={category_key!r}"
        )
    else:
        logger.info(f"new guide push: sent {sent} for category={category_key!r}")
    return sent, len(user_ids)


async def _notify_new_guide(
    guide_key: str, guide_title: str, category_key: str
) -> None:
    try:
        await _telegram_send_new_guide_notifications(
            guide_key, guide_title, category_key
        )
    except Exception as e:
        logger.warning(f"_notify_new_guide failed: {e}")


_ALLOWED_TAGS: set[str] = {
    "strong",
    "em",
    "s",
    "u",
    "code",
    "h2",
    "h3",
    "blockquote",
    "li",
    "a",
    "img",
    "br",
    "hr",
    "span",
    "svg",
    "path",
    "line",
    "video",
}
_ALLOWED_ATTRS: dict[str, set[str]] = {
    "a": {
        "href",
        "target",
        "class",
        "data-guide-key",
        "data-guide-title",
        "data-guide-icon",
    },
    "img": {"src", "alt", "width", "height", "class", "style", "loading"},
    "svg": {
        "viewBox",
        "width",
        "height",
        "fill",
        "stroke",
        "stroke-width",
        "stroke-linecap",
        "class",
        "style",
    },
    "path": {"d", "fill", "stroke", "stroke-width", "stroke-linecap"},
    "line": {"x1", "y1", "x2", "stroke", "stroke-width"},
    "strong": {"class", "style"},
    "em": {"class", "style"},
    "s": {"class", "style"},
    "u": {"class", "style"},
    "code": {"class", "style"},
    "h2": {"class", "style"},
    "h3": {"class", "style"},
    "blockquote": {"class", "style"},
    "li": {"class", "style"},
    "br": {"class"},
    "hr": {"class"},
    "span": {"class", "style"},
    "video": {"src", "controls", "class", "style", "preload", "playsinline", "width", "height"},
}


def normalize_icon_syntax(text: str) -> str:
    from icons import _ICONS_LOWER, ALL_ICONS

    def resolve_key(raw: str) -> str:
        if raw in ALL_ICONS:
            return raw
        return _ICONS_LOWER.get(raw.lower(), raw)

    def resolve_discord_emoji(match: re.Match) -> str:
        raw_name = match.group(1)
        raw_id = match.group(2)

        # Prefer explicit icon key by name.
        by_name = resolve_key(raw_name)
        if by_name in ALL_ICONS:
            return f"{{{{{by_name}}}}}"

        # Fall back to migrated discord asset by numeric id.
        by_id = f"icon_{raw_id}"
        if by_id in ALL_ICONS:
            return f"{{{{{by_id}}}}}"

        # Keep unresolved name in template form to preserve readability.
        return f"{{{{{by_name}}}}}"

    # Convert Discord custom emoji (<:name:id> / <a:name:id>) to internal icon syntax.
    result = re.sub(
        r"<a?:([A-Za-z][A-Za-z0-9_]*):(\d+)>",
        resolve_discord_emoji,
        text,
    )

    # Convert plain :name: icons, but do not touch URL schemes like https://.
    result = re.sub(
        r"(?<!\w):([A-Za-z][A-Za-z0-9_]*):(?!//)",
        lambda m: f"{{{{{resolve_key(m.group(1))}}}}}",
        result,
    )
    result = re.sub(
        r"\{\{(\w+)\}\}", lambda m: f"{{{{{resolve_key(m.group(1))}}}}}", result
    )
    return result


async def resolve_guide_links_bulk(keys: list[str]) -> dict[str, dict]:
    if not keys:
        return {}
    try:
        from sqlalchemy import select

        async with get_sessionmaker()() as session:
            stmt = select(Guide.key, Guide.title, Guide.icon_url).where(
                Guide.key.in_(keys)
            )
            res = await session.execute(stmt)
            return {
                r.key: {"title": r.title, "icon": r.icon_url or ""} for r in res.all()
            }
    except Exception as e:
        logger.warning(f"resolve_guide_links_bulk: {e}")
        return {}


def format_guide_text(text: str, guide_links: dict | None = None) -> str:
    if guide_links is None:
        guide_links = {}

    def replace_icon(match):
        icon_name = match.group(1)
        icon_url = get_icon(icon_name)
        return (
            f'<img src="{icon_url}" alt="{icon_name}" class="inline-icon" '
            f'width="20" height="20" style="vertical-align:middle;margin:0 4px;">'
        )

    result = re.sub(r"\{\{(\w+)\}\}", replace_icon, text)

    def replace_guide_link(match):
        key_part = match.group(1)
        label_part = match.group(2)
        if "|" in key_part:
            key, label = key_part.split("|", 1)
        else:
            key = key_part
            label = label_part
        key = key.strip()
        info = guide_links.get(key, {})
        title = info.get("title", key)
        icon = info.get("icon", "")
        display = label.strip() if label else title
        icon_html = (
            f'<img src="{icon}" width="16" height="16" '
            f'style="vertical-align:middle;margin-right:4px;border-radius:3px;">'
            if icon
            else ""
        )
        return (
            f'<a class="guide-cyberlink" data-guide-key="{key}" '
            f'data-guide-title="{title}" data-guide-icon="{icon}" href="#">'
            f"{icon_html}{display}"
            f'<svg class="guide-cyberlink-arrow" viewBox="0 0 16 16" width="12" height="12" '
            f'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            f'style="margin-left:4px;vertical-align:middle">'
            f'<path d="M3 8h10M9 4l4 4-4 4"/></svg></a>'
        )

    result = re.sub(r"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]", replace_guide_link, result)

    lines = result.split("\n")
    out: list[str] = []
    for line in lines:
        if line.startswith("### "):
            out.append(f'<h3 class="guide-h3">{line[4:]}</h3>')
        elif line.startswith("## "):
            out.append(f'<h2 class="guide-h2">{line[3:]}</h2>')
        elif line.startswith("> "):
            out.append(f'<blockquote class="guide-quote">{line[2:]}</blockquote>')
        elif line.startswith("- "):
            out.append(f'<li class="guide-li guide-ul">{line[2:]}</li>')
        elif re.match(r"^\d+\. ", line):
            content = re.sub(r"^\d+\. ", "", line)
            out.append(f'<li class="guide-li guide-ol">{content}</li>')
        elif line.strip() == "---":
            out.append('<hr class="guide-hr">')
        else:
            out.append(line)
    result = "\n".join(out)

    # Inline formatting — deliberately no re.DOTALL so they don't span line breaks
    result = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", result)
    result = re.sub(r"\*(.+?)\*", r"<em>\1</em>", result)
    result = re.sub(r"~~(.+?)~~", r"<s>\1</s>", result)
    result = re.sub(
        r"`(.+?)`", r'<code class="guide-code">\1</code>', result
    )
    # Spoilers may intentionally span multiple lines
    result = re.sub(
        r"\|\|(.+?)\|\|",
        r'<span class="guide-spoiler">\1</span>',
        result,
        flags=re.DOTALL,
    )
    def media_replacer(m):
        alt, url = m.group(1), m.group(2)
        is_video = any(ext in url.lower() for ext in [".mp4", ".webm", ".mov", "youtube.com", "youtu.be"])
        caption = f'<p class="text-[11px] text-muted-foreground mt-2 text-center italic">{alt}</p>' if alt else ""
        
        if is_video:
            return f'<div class="guide-inline-video my-6"><video src="{url}" controls class="w-full rounded-2xl border border-border/50 shadow-2xl" preload="none" playsinline></video>{caption}</div>'
        else:
            return f'<div class="my-6"><img src="{url}" alt="{alt}" class="guide-img rounded-2xl border border-border/30 shadow-xl" loading="lazy" referrerpolicy="no-referrer">{caption}</div>'

    result = re.sub(
        r"!\[(.*?)\]\((https?://[^\)]+)\)",
        media_replacer,
        result,
    )
    result = re.sub(
        r"\[(.+?)\]\((https?://[^\)]+)\)",
        r'<a href="\2" target="_blank" rel="noreferrer" class="guide-extlink">\1</a>',
        result,
    )
    result = result.replace("\n", "<br>")
    result = nh3.clean(
        result,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRS,
        link_rel="noreferrer",  # nh3 sets rel on <a> via this param, not attributes
    )
    return result
