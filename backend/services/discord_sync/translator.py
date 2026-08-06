import re
import aiohttp
from core.logging import get_logger

logger = get_logger("blackrose.services.discord_sync.translator")

def sanitize_discord_markdown(text: str) -> str:
    """
    Cleans raw Discord formatting:
    - User/Channel/Role mentions: <@123>, <#123>, <@&123>
    - Spoilers: ||spoiler|| -> <details>
    - Custom emojis: <:name:id> -> {{icon:name}}
    """
    if not text:
        return ""

    # Replace user & role mentions
    text = re.sub(r'<@&?\d+>', '', text)
    # Replace channel mentions
    text = re.sub(r'<#\d+>', '', text)
    
    # Replace custom emojis <:emoji_name:123456789>
    text = re.sub(r'<a?:([a-zA-Z0-9_]+):\d+>', r'{{icon:\1}}', text)

    # Replace Discord spoilers ||text||
    text = re.sub(r'\|\|(.*?)\|\|', r'<details class="my-2 p-2 bg-muted/30 rounded-xl"><summary className="cursor-pointer font-bold text-xs">Спойлер</summary><div className="pt-2">\1</div></details>', text, flags=re.DOTALL)

    return text.strip()


async def translate_en_to_ru(text: str) -> str:
    """
    Translates English guide markdown to Russian using free translation API with fallback.
    Preserves Markdown links, code blocks, and {{icon:...}} syntax.
    """
    if not text or len(text.strip()) == 0:
        return text

    # Extract & protect code blocks and {{icon:...}} tags from translation
    placeholders: dict[str, str] = {}
    counter = 0

    def mask_match(match: re.Match) -> str:
        nonlocal counter
        key = f"___PH_{counter}___"
        placeholders[key] = match.group(0)
        counter += 1
        return key

    # Mask code blocks ```...```
    masked_text = re.sub(r'```[\s\S]*?```', mask_match, text)
    # Mask inline code `...`
    masked_text = re.sub(r'`[^`]+`', mask_match, masked_text)
    # Mask icon placeholders {{icon:...}}
    masked_text = re.sub(r'\{\{icon:[^}]+\}\}', mask_match, masked_text)

    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "en",
            "tl": "ru",
            "dt": "t",
            "q": masked_text,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    translated_chunks = []
                    if isinstance(data, list) and data and isinstance(data[0], list):
                        for chunk in data[0]:
                            if isinstance(chunk, list) and chunk and chunk[0]:
                                translated_chunks.append(chunk[0])
                    translated_text = "".join(translated_chunks)
                else:
                    logger.warning(f"Translation API status {resp.status}, returning original")
                    translated_text = text
    except Exception as e:
        logger.error(f"Error during translation: {e}")
        translated_text = text

    # Restore masked placeholders
    for key, val in placeholders.items():
        translated_text = translated_text.replace(key, val)

    return translated_text
