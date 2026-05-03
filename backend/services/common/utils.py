import re

def normalize_icon_syntax(text: str) -> str:
    """
    Normalizes icon syntax from:
    1. Unicode emojis (🔥 -> {{icon:fire}})
    2. Discord custom emojis (<:name:id> -> {{icon:name}})
    3. Legacy colon syntax (:name: -> {{icon:name}})
    """
    if not text:
        return ""

    # 1. Standard Unicode Emoji Mapping
    emoji_map = {
        "🔥": "fire", "💎": "diamond", "⚔️": "sword", "🛡️": "shield",
        "📜": "scroll", "✨": "sparkles", "✅": "check", "❌": "cross",
        "💡": "idea", "⭐": "star", "🔋": "battery", "⚙️": "gear",
        "🔔": "bell", "📍": "pin", "🔗": "link", "🏹": "bow",
        "🧪": "flask", "🎒": "backpack", "🧭": "compass"
    }
    
    for emoji, name in emoji_map.items():
        text = text.replace(emoji, f"{{{{icon:{name}}}}}")

    # 2. Discord custom emoji: <:name:id> or <a:name:id> -> {{icon:name}}
    text = re.sub(r"<a?:([A-Za-z0-9_]+):(\d+)>", r"{{icon:\1}}", text)
    
    # 3. Legacy :name: (only if not a URL or inside braces) -> {{icon:name}}
    # Avoid matching https://
    text = re.sub(r"(?<!https)(?<!http)(?<!\w):([A-Za-z0-9_]+):(?!\d)", r"{{icon:\1}}", text)
    
    # 4. Standardize {{name}} to {{icon:name}} if it doesn't have a prefix
    text = re.sub(r"\{\{([A-Za-z0-9_]+)\}\}", r"{{icon:\1}}", text)
    
    return text

def format_guide_text(text: str, guide_links: dict | None = None) -> str:
    """
    Renders guide markdown into safe HTML. 
    Handles spoilers, custom icons, and internal guide links.
    """
    if not text:
        return ""
    
    import nh3
    guide_links = guide_links or {}

    # 1. Normalize Icons First
    text = normalize_icon_syntax(text)

    # 2. Basic Markdown (Simplified)
    # Headers
    text = re.sub(r"^### (.*)$", r'<h3 class="guide-h3">\1</h3>', text, flags=re.M)
    text = re.sub(r"^## (.*)$", r'<h2 class="guide-h2">\1</h2>', text, flags=re.M)
    
    # Spoilers ||text|| -> <span class="guide-spoiler">text</span>
    text = re.sub(r"\|\|(.*?)\|\|", r'<span class="guide-spoiler">\1</span>', text)
    
    # Internal Guide Links [[key|label]] or [[key]]
    def replace_guide_link(match):
        content = match.group(1)
        if "|" in content:
            key, label = content.split("|", 1)
        else:
            key, label = content, guide_links.get(content, {}).get("title", content)
        
        icon_url = guide_links.get(key, {}).get("icon_url", "")
        icon_html = f'<img src="{icon_url}" class="inline-icon"> ' if icon_url else ""
        return f'<a href="/guides/{key}" class="guide-cyberlink" data-guide-key="{key}">{icon_html}{label}</a>'

    text = re.sub(r"\[\[(.*?)\]\]", replace_guide_link, text)

    # Bold/Italic
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)

    # Icons {{icon:name}} -> <img ...>
    def replace_icon(match):
        name = match.group(1)
        # In a real app, this would resolve to a CDN URL
        return f'<img src="/api/icons/{name}" class="inline-icon" alt="{name}">'

    text = re.sub(r"\{\{icon:(.*?)\}\}", replace_icon, text)

    # 3. Final Sanitization
    return nh3.clean(text, tags={
        "strong", "em", "a", "h2", "h3", "span", "img", "blockquote", "ul", "ol", "li", "br", "p"
    }, attributes={
        "a": {"href", "class", "data-guide-key", "target", "rel"},
        "span": {"class"},
        "img": {"src", "class", "alt"},
        "h2": {"class"},
        "h3": {"class"}
    })


def _strip_html(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"<[^>]*>", "", text)

def _strip_markdown(text: str | None) -> str:
    if not text:
        return ""
    # Simple markdown stripping (bold, italic, links, icons)
    text = re.sub(r"(\*\*|__|\*|_|`|~~)", "", text)
    text = re.sub(r"\{\{.*?\}\}", "", text)
    text = re.sub(r"\[\[(.*?)\]\]", r"\1", text)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    return text.strip()

