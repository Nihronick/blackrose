import re
import json
import os
import aiohttp
from typing import List, Dict
from core.config import settings
from core.http import http_client
from core.logging import get_logger
from services.common import utils

logger = get_logger("blackrose.services.discord_lab")

class DiscordGuideSynthesizer:
    """
    Service for synthesizing Discord messages into structured guide content.
    """
    def __init__(self, icons_map: Dict[str, str] = {}):
        self.icons_map = icons_map or {
            "fire": "{{icon:fire}}",
            "water": "{{icon:water}}",
            "wind": "{{icon:wind}}",
            "earth": "{{icon:earth}}",
            "spirit": "{{icon:spirit}}",
            "slayer": "{{icon:slayer}}"
        }
        self.glossary = self._load_glossary()

    def _load_glossary(self) -> Dict:
        path = settings.GLOSSARY_PATH
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load glossary from {path}: {e}")
        return {}

    def clean_noise(self, text: str) -> str:
        text = re.sub(r'<@\d+>', '', text)
        text = re.sub(r'<#\d+>', '', text)
        return text.strip()

    def map_emojis(self, text: str) -> str:
        return utils.normalize_icon_syntax(text)

    def enrich_text(self, text: str) -> str:
        if not self.glossary:
            return text
        # Use abbreviations and terminology from glossary
        abbrs = self.glossary.get("abbreviations", {})

        for term, full_name in abbrs.items():
            pattern = r'\b' + re.escape(term) + r'\b'
            text = re.sub(pattern, f"{term} ({full_name})", text)
        return text

    def synthesize(self, messages: List[Dict]) -> Dict:
        sorted_msgs = sorted(messages, key=lambda x: x.get('timestamp', ''))
        full_content = []
        media_urls = []

        for msg in sorted_msgs:
            content = msg.get('content', '')
            author = msg.get('author', {}).get('username', 'Unknown')
            if len(content) < 5 and not msg.get('attachments'):
                continue

            clean_text = self.clean_noise(content)
            mapped_text = self.map_emojis(clean_text)
            enriched_text = self.enrich_text(mapped_text)

            if enriched_text:
                full_content.append(f"--- (Автор: {author}) ---\n{enriched_text}")

            for att in msg.get('attachments', []):
                media_urls.append({
                    "url": att.get('url'),
                    "type": att.get('content_type', 'image'),
                    "name": att.get('filename')
                })

        return {
            "content": "\n\n".join(full_content),
            "media": media_urls
        }

    async def synthesize_ai(self, messages: List[Dict]) -> Dict:
        """
        Synthesizes Discord messages using Gemini AI for high-quality structuring.
        """
        if not settings.GEMINI_API_KEY:
            logger.info("GEMINI_API_KEY not found, falling back to manual synthesis")
            return self.synthesize(messages)

        raw_text = self.synthesize(messages)["content"]

        glossary = self._load_glossary()
        terms_hint = json.dumps(glossary.get("terminology_ru", {}), ensure_ascii=False)
        no_translate = ", ".join(glossary.get("no_translate", []))
        abbrs_hint = json.dumps(glossary.get("abbreviations", {}), ensure_ascii=False)

        prompt = (
            "You are a professional gaming wiki editor for Slayer Legend. "
            "I will provide you with a raw log of Discord messages that form a game guide. "
            "Your task is to transform them into a clean, structured Markdown guide in Russian.\n\n"
            f"TERMINOLOGY MAP: {terms_hint}\n"
            f"ABBREVIATIONS: {abbrs_hint}\n"
            f"DO NOT TRANSLATE: {no_translate}\n\n"
            "RULES:\n"
            "1. Remove all noise (usernames, timestamps, meta-talk).\n"
            "2. Use logical headings (##, ###).\n"
            "3. Use bullet points for stats and lists.\n"
            "4. KEEP all media tags like ![video](...) or ![image](...) exactly as they are.\n"
            "5. KEEP all custom icons like {{icon:...}} or {{icon_id}}.\n"
            "6. Use professional RU gaming terminology from the map above. Translate abbreviations to full RU terms where appropriate.\n"
            "7. The output must be ONLY the Markdown content.\n\n"
            f"RAW LOG:\n{raw_text}"
        )

        try:
            session = await http_client.get_session()
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}

            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    ai_content = data["candidates"][0]["content"]["parts"][0]["text"]
                    return {
                        "content": ai_content.strip(),
                        "media": self.synthesize(messages)["media"]
                    }
                else:
                    logger.error(f"Gemini AI synthesis failed with status {resp.status}")
        except Exception as e:
            logger.error(f"AI synthesis error: {e}")

        return self.synthesize(messages)

discord_lab_service = DiscordGuideSynthesizer()
