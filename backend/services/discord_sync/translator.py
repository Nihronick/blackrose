import re
import aiohttp
from core.logging import get_logger

logger = get_logger("blackrose.services.discord_sync.translator")

# Comprehensive BlackRose / Gaming Glossary Map
GAMING_GLOSSARY: dict[str, str] = {
    "Constellations": "Созвездия",
    "Constellation": "Созвездие",
    "Amount": "Количество",
    "amount": "количество",
    "Rift": "Рифт",
    "Golems": "Големы",
    "Golem": "Голем",
    "Awakening": "Пробуждение",
    "Sealed Shrine": "Запечатанное Святилище",
    "Latent Power": "Скрытая Сила",
    "Latent": "Латентка",
    "Skill Stone": "Камень Навыка",
    "Skill Stones": "Камни Навыков",
    "Companion": "Компаньон",
    "Companions": "Компаньоны",
    "Promotion": "Продвижение",
    "Promotions": "Продвижения",
    "Stage": "Этап",
    "Stages": "Этапы",
    "Rage": "Ярость",
    "Rave": "Рейв",
    "Slayer": "Слейер",
    "Slayers": "Слейеры",
    "Demon Metal": "Демон-Металл",
    "Ancient Canine": "Древний Клык",
    "Dark Nox": "Дарк Нокс",
    "Black Mythril": "Черный Мифрил",
    "Warfrost": "Варфрост",
    "Blue Abyss": "Голубая Бездна",
    "Orichalcum": "Орихалк",
    "Eldenwood": "Элденвуд",
    "Eisenhart": "Эйзенхарт",
    "Gigarock": "Гигарок",
    "Dragonos": "Драгонос",
    "Ragnablood": "Рагнаблод",
    "Infinaut": "Инфинавт",
    "Meloning": "Мелонинг",
    "Soul": "Душа",
    "Souls": "Души",
}


def sanitize_discord_markdown(text: str) -> tuple[str, list[str], list[str]]:
    """
    Cleans raw Discord formatting:
    - User/Channel/Role mentions: <@123>, <#123>, <@&123>
    - Spoilers: ||spoiler|| -> <details>
    - Custom emojis: <:name:id> -> {{https://cdn.discordapp.com/emojis/id.png}}
    - Extracts photo & video URLs
    Returns tuple: (cleaned_text, photo_urls, video_urls)
    """
    if not text:
        return "", [], []

    photos: list[str] = []
    videos: list[str] = []

    # 1. Extract YouTube and Video URLs
    yt_matches = re.findall(
        r'(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[a-zA-Z0-9_-]+)',
        text
    )
    for yt_url in yt_matches:
        if yt_url not in videos:
            videos.append(yt_url)

    direct_videos = re.findall(
        r'(https?://[^\s\)\>]+\.(?:mp4|webm|mov|mkv|gifv))',
        text,
        flags=re.IGNORECASE
    )
    for v_url in direct_videos:
        if v_url not in videos:
            videos.append(v_url)

    # 2. Extract Direct Image Links in text (CDN, Imgur, Tenor, attachments)
    img_matches = re.findall(
        r'(https?://(?:cdn|media|images-ext-\d+)\.discordapp\.(?:com|net)/attachments/[^\s\)\>]+)',
        text,
        flags=re.IGNORECASE
    )
    for img_url in img_matches:
        if img_url not in photos:
            photos.append(img_url)

    general_imgs = re.findall(
        r'(https?://[^\s\)\>]+\.(?:png|jpg|jpeg|gif|webp)(?:\?[^\s\)\>]*)?)',
        text,
        flags=re.IGNORECASE
    )
    for img_url in general_imgs:
        if not img_url.startswith("https://cdn.discordapp.com/emojis/") and img_url not in photos:
            photos.append(img_url)

    tenor_imgs = re.findall(
        r'(https?://media\.tenor\.com/[^\s\)\>]+)',
        text,
        flags=re.IGNORECASE
    )
    for img_url in tenor_imgs:
        if img_url not in photos:
            photos.append(img_url)

    # Replace user & role mentions
    text = re.sub(r'<@&?\d+>', '', text)
    # Replace channel mentions
    text = re.sub(r'<#\d+>', '', text)

    # Convert Discord internal links [Label](https://discord.com/channels/guild/target_id) -> [[discord_target_id|Label]]
    text = re.sub(
        r'\[(.*?)\]\(https?://(?:ptb\.|canary\.)?discord\.com/channels/\d+/(\d+)(?:/\d+)?\)',
        r'[[discord_\2|\1]]',
        text
    )
    text = re.sub(
        r'https?://(?:ptb\.|canary\.)?discord\.com/channels/\d+/(\d+)(?:/\d+)?',
        r'[[discord_\1]]',
        text
    )

    # Replace Discord custom animated/static emojis <:name:id> or <a:name:id>
    def replace_custom_emoji(match: re.Match) -> str:
        is_anim, name, emoji_id = match.groups()
        ext = "gif" if is_anim else "webp"
        cdn_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}?size=48&quality=lossless"
        return f"{{{{{cdn_url}}}}}"

    text = re.sub(r'<(a)?:([a-zA-Z0-9_]+):(\d+)>', replace_custom_emoji, text)

    # Convert video links in text to clean embeds
    for v_url in videos:
        if "youtube.com" in v_url or "youtu.be" in v_url:
            text = text.replace(v_url, f"\n\n[Video: YouTube]({v_url})\n\n")

    # Replace Discord spoilers ||text||
    text = re.sub(
        r'\|\|(.*?)\|\|',
        r'<details class="my-2 p-2 bg-muted/30 rounded-xl"><summary className="cursor-pointer font-bold text-xs">Спойлер</summary><div className="pt-2">\1</div></details>',
        text,
        flags=re.DOTALL
    )

    return text.strip(), photos, videos


async def translate_en_to_ru(text: str) -> str:
    """
    Translates English guide markdown to Russian using translation API with gaming terminology protection.
    Preserves Markdown links, code blocks, and {{...}} syntax.
    """
    if not text or len(text.strip()) == 0:
        return text

    # Extract & protect code blocks, URLs, and {{...}} tags from translation
    placeholders: dict[str, str] = {}
    counter = 0

    def mask_match(match: re.Match) -> str:
        nonlocal counter
        key = f"___PH_{counter}___"
        placeholders[key] = match.group(0)
        counter += 1
        return key

    def mask_str(val: str) -> str:
        nonlocal counter
        key = f"___PH_{counter}___"
        placeholders[key] = val
        counter += 1
        return key

    # Mask code blocks ```...```
    masked_text = re.sub(r'```[\s\S]*?```', mask_match, text)
    # Mask inline code `...`
    masked_text = re.sub(r'`[^`]+`', mask_match, masked_text)
    # Mask icon / image placeholders {{...}}
    masked_text = re.sub(r'\{\{[^}]+\}\}', mask_match, masked_text)
    # Mask markdown URLs [label](url) -> protect url part
    masked_text = re.sub(r'\]\((https?://[^\s)]+)\)', lambda m: f"]({mask_str(m.group(1))})", masked_text)

    # Protect Gaming Glossary Terms before sending to translation
    for term, ru_term in GAMING_GLOSSARY.items():
        # Mask specific exact gaming terms
        pattern = re.compile(rf'\b{re.escape(term)}\b')
        masked_text = pattern.sub(lambda m: mask_match(m), masked_text)

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
        # If val was a gaming glossary term, substitute its authentic Russian term!
        if val in GAMING_GLOSSARY:
            translated_text = translated_text.replace(key, GAMING_GLOSSARY[val])
        else:
            translated_text = translated_text.replace(key, val)

    # Clean up any leftover translation artifacts
    translated_text = re.sub(r'__(?:ГЛОСС|GLOSS|CODE|КОД)\d*__', '', translated_text, flags=re.IGNORECASE)
    translated_text = re.sub(r'\baМаунт\b', 'количество', translated_text)
    translated_text = re.sub(r'\bМаунт\b', 'количество', translated_text)
    translated_text = re.sub(r'\bСозвездиеs\b', 'Созвездия', translated_text)
    translated_text = re.sub(r'\bПробуждениеs\b', 'Пробуждения', translated_text)

    return translated_text.strip()


def generate_tldr_block(text: str) -> str:
    """
    Extracts key points from guide text and builds a TL;DR summary block.
    """
    if not text:
        return text

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    content_lines = [line_str for line_str in lines if not line_str.startswith("#")]
    
    summary_bullets = content_lines[:3] if content_lines else lines[:3]
    if not summary_bullets:
        return text

    tldr_markdown = (
        "> [!NOTE]\n"
        "> **💡 Краткая выжимка (TL;DR):**\n"
    )
    for b in summary_bullets:
        clean_b = b[:120] + ("..." if len(b) > 120 else "")
        tldr_markdown += f"> • {clean_b}\n"

    return tldr_markdown + "\n\n" + text

