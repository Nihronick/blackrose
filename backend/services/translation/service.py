import logging
import aiohttp
import json
import os
from core.config import settings
from core.http import http_client
from core.logging import get_logger

logger = get_logger("blackrose.services.translation")

class TranslationService:
    _glossary = None

    @classmethod
    def _load_glossary(cls):
        if cls._glossary is not None:
            return cls._glossary
        
        path = settings.GLOSSARY_PATH
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    cls._glossary = json.load(f)
                    return cls._glossary
            except Exception as e:
                logger.error(f"Failed to load glossary: {e}")
        cls._glossary = {}
        return cls._glossary

    @staticmethod
    async def translate_text(text: str) -> str:
        if not text: return ""

        # Cascade: HF -> Gemini -> Google
        if settings.HF_TOKEN:
            res = await TranslationService._translate_hf(text, settings.HF_TOKEN)
            if res: return res

        # Check for GEMINI_API_KEY from environment or settings
        gemini_key = os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY
        if gemini_key:
            res = await TranslationService._translate_gemini(text, gemini_key)
            if res: return res

        return await TranslationService._translate_google(text)

    @staticmethod
    async def _translate_hf(text: str, token: str) -> str | None:
        try:
            glossary = TranslationService._load_glossary()
            terms_hint = json.dumps(glossary.get("terminology_ru", {}), ensure_ascii=False)
            no_translate = ", ".join(glossary.get("no_translate", []))
            
            model = "Qwen/Qwen2.5-72B-Instruct"
            url = f"https://api-inference.huggingface.co/models/{model}"
            headers = {"Authorization": f"Bearer {token}"}
            prompt = (
                f"<|im_start|>system\nProfessional gaming translator (EN -> RU) for Slayer Legend. "
                f"GLOSSARY: {terms_hint}. "
                f"DO NOT TRANSLATE: {no_translate}. "
                "RULES: 1. Do NOT translate tags ![video], ![image], {{icon:...}}. 2. Keep Discord emojis. 3. Use professional gaming terms from glossary.<|im_end|>\n"
                f"<|im_start|>user\n{text}<|im_end|>\n<|im_start|>assistant\n"
            )
            session = await http_client.get_session()
            async with session.post(url, json={"inputs": prompt, "parameters": {"max_new_tokens": 2048}}, headers=headers, timeout=30) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        full = data[0].get("generated_text", "") if isinstance(data, list) else data.get("generated_text", "")
                        return TranslationService._post_process(full.split("<|im_start|>assistant\n")[-1].strip())
        except Exception as e:
            logger.debug(f"HF translation failed: {e}")
        return None

    @staticmethod
    async def _translate_gemini(text: str, api_key: str) -> str | None:
        try:
            glossary = TranslationService._load_glossary()
            terms_hint = json.dumps(glossary.get("terminology_ru", {}), ensure_ascii=False)
            no_translate = ", ".join(glossary.get("no_translate", []))

            session = await http_client.get_session()
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            prompt = (
                "Translate this Slayer Legend game guide to Russian.\n"
                f"MANDATORY TERMINOLOGY (EN: RU): {terms_hint}\n"
                f"DO NOT TRANSLATE THESE TERMS: {no_translate}\n"
                "IMPORTANT: Keep ![video], ![image], links, emojis, and {{icon_name}} tags exactly as they are. "
                "Use the provided glossary to ensure professional gaming terminology.\n\n"
                f"TEXT TO TRANSLATE:\n{text}"
            )
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            async with session.post(url, json=payload, timeout=20) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return TranslationService._post_process(data["candidates"][0]["content"]["parts"][0]["text"])
        except Exception as e:
            logger.debug(f"Gemini translation failed: {e}")
        return None

    @staticmethod
    async def _translate_google(text: str) -> str:
        try:
            from deep_translator import GoogleTranslator
            return TranslationService._post_process(GoogleTranslator(source='auto', target='ru').translate(text))
        except: return text

    @staticmethod
    def _post_process(text: str) -> str:
        return text.replace("![видео]", "![video]").replace("![изображение]", "![image]")

translation_service = TranslationService()
