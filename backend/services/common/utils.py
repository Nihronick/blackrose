import re
import nh3
from services.common.icons import icon_url

def normalize_icon_syntax(text: str) -> str:
    """
    Normalizes icon syntax to {{KEY}} format.
    Handles:
    - Unicode emojis
    - Discord syntax <:name:id>
    - :name: syntax
    """
    if not text:
        return ""

    # 1. Unicode Emoji Mapping
    emoji_map = {
        "🔥": "FIRE", "💎": "DIAMOND", "⚔️": "SWORD", "🛡️": "SHIELD",
        "📜": "SCROLL", "✨": "SPARKLES", "✅": "CHECK", "❌": "CROSS",
        "💡": "IDEA", "⭐": "STAR", "🔋": "BATTERY", "⚙️": "GEAR",
        "🔔": "BELL", "📍": "PIN", "🔗": "LINK", "🏹": "BOW",
        "🧪": "FLASK", "🎒": "BACKPACK", "🧭": "COMPASS"
    }

    for emoji, name in emoji_map.items():
        text = text.replace(emoji, f"{{{{{name}}}}}")

    # 2. Discord custom emoji: <:name:id> or <a:name:id> -> {{NAME}}
    text = re.sub(r"<a?:([A-Za-z0-9_]+):(\d+)>", r"{{\1}}", text)

    # 3. Legacy :name: -> {{NAME}} (ensure not part of URL)
    text = re.sub(r"(?<!https)(?<!http)(?<!\w):([A-Za-z0-9_]+):(?!\d)", lambda m: f"{{{{{m.group(1).upper()}}}}}", text)

    # 4. Standardize {{name}} to {{NAME}}
    text = re.sub(r"\{\{([A-Za-z0-9_]+)\}\}", lambda m: f"{{{{{m.group(1).upper()}}}}}", text)

    return text

def format_guide_text(text: str, guide_links: dict | None = None) -> str:
    """
    Renders guide markdown into safe HTML. 
    Sync with frontend/src/lib/markdown.ts logic.
    """
    if not text:
        return ""

    guide_links = guide_links or {}

    # 1. Normalize Icons First
    text = normalize_icon_syntax(text)

    # 2. Markdown Processing (Regex based for performance/simplicity in backend)

    # Newlines to <br> (handle CRLF)
    text = text.replace("\r\n", "\n")

    # Spoilers ||text|| -> <span class="guide-spoiler">text</span>
    text = re.sub(r"\|\|(.*?)\|\|", r'<span class="guide-spoiler">\1</span>', text)

    # Headers
    text = re.sub(r"^### (.*)$", r'<h3 class="guide-h3">\1</h3>', text, flags=re.M)
    text = re.sub(r"^## (.*)$", r'<h2 class="guide-h2">\1</h2>', text, flags=re.M)

    # Blockquotes
    text = re.sub(r"^> (.*)$", r'<blockquote class="guide-quote">\1</blockquote>', text, flags=re.M)

    # Lists (ul)
    text = re.sub(r"^- (.*)$", r'<li class="guide-li guide-ul">\1</li>', text, flags=re.M)
    # Lists (ol)
    text = re.sub(r"^\d+\. (.*)$", r'<li class="guide-li guide-ol">\1</li>', text, flags=re.M)

    # External Links [text](url) — External if starts with http
    def replace_link(match):
        label, url = match.groups()
        is_external = url.startswith("http") or url.startswith("//")
        attrs = 'target="_blank" rel="noreferrer" class="guide-extlink"' if is_external else 'class="text-primary"'
        return f'<a href="{url}" {attrs}>{label}</a>'

    text = re.sub(r"\[(.*?)\]\((.*?)\)", replace_link, text)

    # Internal Guide Links [[key|label]] or [[key]]
    def replace_guide_link(match):
        content = match.group(1)
        if "|" in content:
            key, label = content.split("|", 1)
        else:
            key = content
            label = guide_links.get(key, {}).get("title", key)

        icon_url = guide_links.get(key, {}).get("icon", "")
        icon_html = f'<img src="{icon_url}" class="inline-icon"> ' if icon_url else ""
        return f'<a href="#" class="guide-cyberlink" data-guide-key="{key}">{icon_html}{label}</a>'

    text = re.sub(r"\[\[(.*?)\]\]", replace_guide_link, text)

    # Bold/Italic
    text = re.sub(r"\*\*\*(.*?)\*\*\*", r"<strong><em>\1</em></strong>", text, flags=re.DOTALL)
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text, flags=re.DOTALL)
    text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)
    text = re.sub(r"~~(.*?)~~", r"<s>\1</s>", text, flags=re.DOTALL)

    # Inline Code
    text = re.sub(r"`(.*?)`", r'<code class="guide-code">\1</code>', text)

    # HR
    text = re.sub(r"^---$", r'<hr class="guide-hr">', text, flags=re.M)

    # Icons {{NAME}} -> <img ...>
    def replace_icon(match):
        name = match.group(1)
        return f'<img src="{icon_url(name)}" class="inline-icon" alt="{name}">'

    text = re.sub(r"\{\{([A-Z0-9_]+)\}\}", replace_icon, text)

    # Final line break handling for plain paragraphs
    text = text.replace("\n", "<br>")

    # 3. Final Sanitization
    # NOTE: nh3 manages `rel` internally — do NOT put "rel" in attributes
    # or it will panic. Use link_rel parameter instead.
    return nh3.clean(text, tags={
        "strong", "em", "a", "h2", "h3", "span", "img", "blockquote", "ul", "ol", "li", "br", "p", "code", "s", "hr"
    }, attributes={
        "a": {"href", "class", "data-guide-key", "target"},
        "span": {"class"},
        "img": {"src", "class", "alt"},
        "h2": {"class"},
        "h3": {"class"},
        "blockquote": {"class"},
        "li": {"class"},
        "code": {"class"},
        "hr": {"class"}
    }, link_rel="noreferrer")

def _strip_html(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"<[^>]*>", "", text)

def _strip_markdown(text: str | None) -> str:
    if not text:
        return ""
    # Process guide links FIRST to preserve underscores in keys
    text = re.sub(r"\[\[(.*?)(?:\|.*?)?\]\]", r"\1", text)
    # Strip markdown formatting (** __ * ~~ `) but NOT single underscores
    text = re.sub(r"(\*\*\*|__|\*\*|\*|~~|`)", "", text)
    text = re.sub(r"\{\{.*?\}\}", "", text)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    return text.strip()
