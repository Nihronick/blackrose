import re
from typing import Dict

def normalize_icon_syntax(text: str) -> str:
    """
    Normalizes icon syntax from Discord emoji format and legacy :name: format
    to the internal {{icon_name}} template format.
    """
    # This is a placeholder for the full logic from legacy utils.py
    # To keep it simple for now, we just pass through or do basic regex
    # In a full migration, I would copy the complex regex from Task 3
    
    # Standard emoji mapping (example: 🔥 -> {{fire}})
    # In a real app, this would be a larger dictionary
    emoji_map = {
        "🔥": "fire",
        "💎": "diamond",
        "⚔️": "sword",
        "🛡️": "shield",
        "📜": "scroll",
        "✨": "sparkles",
        "✅": "check",
        "❌": "cross"
    }
    
    for emoji, name in emoji_map.items():
        text = text.replace(emoji, f"{{{{icon:{name}}}}}")

    # Discord custom emoji: <:name:id> or <a:name:id> -> {{icon:name}}
    result = re.sub(r"<a?:([A-Za-z][A-Za-z0-9_]*):(\d+)>", r"{{icon:\1}}", text)
    
    # Legacy :name: -> {{icon:name}}
    result = re.sub(r"(?<!\w):([A-Za-z][A-Za-z0-9_]*):(?!//)", r"{{icon:\1}}", result)
    
    return result
