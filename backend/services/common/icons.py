from urllib.parse import quote


_ICON_EMOJI: dict[str, str] = {
    "fire": "🔥",
    "water": "💧",
    "wind": "💨",
    "earth": "🪨",
    "spirit": "✨",
    "slayer": "⚔️",
    "diamond": "💎",
    "sword": "⚔️",
    "shield": "🛡️",
    "scroll": "📜",
    "check": "✅",
    "cross": "❌",
    "idea": "💡",
    "star": "⭐",
    "battery": "🔋",
    "gear": "⚙️",
    "bell": "🔔",
    "pin": "📍",
    "link": "🔗",
    "bow": "🏹",
    "flask": "🧪",
    "backpack": "🎒",
    "compass": "🧭",
}


def icon_catalog() -> list[str]:
    return sorted(_ICON_EMOJI.keys())


def icon_url(name: str) -> str:
    key = (name or "").strip().lower()
    emoji = _ICON_EMOJI.get(key, "❔")
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='64' height='64' viewBox='0 0 64 64'>"
        "<rect width='64' height='64' rx='14' fill='#111827'/>"
        f"<text x='50%' y='54%' dominant-baseline='middle' text-anchor='middle' "
        f"font-size='36'>{emoji}</text></svg>"
    )
    return f"data:image/svg+xml;utf8,{quote(svg)}"
