import logging
import os
import aiohttp
from fastapi import HTTPException

logger = logging.getLogger("blackrose.translation")

class TranslationService:
    @staticmethod
    async def translate_text(text: str) -> str:
        if not text:
            return ""

        # Try Hugging Face (Qwen 2.5)
        hf_token = os.getenv("HF_TOKEN")
        if hf_token:
            res = await TranslationService._translate_hf(text, hf_token)
            if res:
                return res

        # Try Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            res = await TranslationService._translate_gemini(text, api_key)
            if res:
                return res

        # Try Google Translate Fallback
        return await TranslationService._translate_google(text)

    @staticmethod
    async def _translate_hf(text: str, token: str) -> str | None:
        try:
            hf_model = "Qwen/Qwen2.5-72B-Instruct"
            url = f"https://api-inference.huggingface.co/models/{hf_model}"
            headers = {"Authorization": f"Bearer {token}"}
            
            prompt = (
                f"<|im_start|>system\nТы — профессиональный переводчик игровых гайдов. Переводи с английского на русский.\n"
                "ПРАВИЛА:\n"
                "1. НЕ ПЕРЕВОДИ теги в квадратных скобках: ![video], ![image] — оставляй их как есть.\n"
                "2. Сохраняй эмодзи Discord (<:name:id>) и ссылки без изменений.\n"
                "3. Используй игровой сленг (например, 'билд', 'скиллы', 'статы').<|im_end|>\n"
                f"<|im_start|>user\nПереведи этот текст:\n{text}<|im_end|>\n"
                "<|im_start|>assistant\n"
            )
            
            payload = {
                "inputs": prompt,
                "parameters": {"max_new_tokens": 2048, "temperature": 0.1}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=30) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        full_text = ""
                        if isinstance(data, list) and len(data) > 0:
                            full_text = data[0].get("generated_text", "")
                        elif isinstance(data, dict):
                            full_text = data.get("generated_text", "")
                        
                        if full_text:
                            translated = full_text.split("<|im_start|>assistant\n")[-1].strip()
                            return TranslationService._post_process(translated)
        except Exception as e:
            logger.warning(f"HF translation failed: {e}")
        return None

    @staticmethod
    async def _translate_gemini(text: str, api_key: str) -> str | None:
        try:
            models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro"]
            async with aiohttp.ClientSession() as session:
                for model_name in models_to_try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                    prompt = (
                        "Переведи следующий текст гайда Slayer Legend на русский язык.\n"
                        "ВАЖНО: Оставляй теги ![video] и ![image] БЕЗ ИЗМЕНЕНИЙ. Не переводи слова внутри скобок [] для этих тегов.\n"
                        "Сохрани ссылки и эмодзи Discord.\n\n"
                        f"Текст:\n{text}"
                    )
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    async with session.post(url, json=payload, timeout=20) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            translated = data["candidates"][0]["content"]["parts"][0]["text"]
                            return TranslationService._post_process(translated)
        except Exception as e:
            logger.warning(f"Gemini translation failed: {e}")
        return None

    @staticmethod
    async def _translate_google(text: str) -> str:
        try:
            from deep_translator import GoogleTranslator
            translated = GoogleTranslator(source='auto', target='ru').translate(text)
            return TranslationService._post_process(translated)
        except Exception as e:
            logger.error(f"Google fallback failed: {e}")
            return text # Return original if all fails

    @staticmethod
    def _post_process(text: str) -> str:
        """Fix common translation artifacts like translated tags."""
        return text.replace("![видео]", "![video]").replace("![изображение]", "![image]")
