import json
import os
import re
from core.config import settings
from core.http import http_client
from core.logging import get_logger

logger = get_logger("blackrose.services.translation")

SYSTEM_PROMPT = """Ты — профессиональный игровой локализатор и эксперт по мобильной игре Slayer Legend.
Твоя задача — качественно и естественно перевести руководство по игре с английского на русский язык.

КРИТИЧЕСКИЕ ПРАВИЛА:
1. СОХРАНЯЙ ВСЮ РАЗМЕТКУ И МЕДИА-ТЕГИ:
   - Ссылки [Текст](url) — переводи только текст ссылки, URL оставляй без изменений!
   - Медиа-теги ![...](url), видео [Video: ...](url) — сохраняй в точности.
   - Иконки и эмодзи {{...}}, <:name:id>, <a:name:id>, юникод-эмодзи — НЕ удаляй, НЕ изменяй, НЕ переводи внутри скобок!
   - Код `...`, блоки кода ```...```, заголовки #, ##, списки -, * — сохраняй структуру Markdown.
   - Таблицы Markdown | col | col | — сохраняй структуру колонок и разделители.
2. ИСПОЛЬЗУЙ ИГРОВОЙ СЛЕНГ И ТЕРМИНОЛОГИЮ SLAYER LEGEND:
   - Rave -> Рейв
   - Rage -> Ярость
   - Spirits -> Духи
   - Familiars -> Фамильяры
   - Promotion -> Продвижение
   - Latent / Latent Power -> Латентка / Скрытая сила
   - CD / Cooldown -> КД (перезарядка)
   - DPS -> ДПС (урон в секунду)
   - Boss -> Босс
   - Mobs -> Мобы
   - Beast -> Зверь
   - Stage -> Этап
   - Breakthrough -> Прорыв
   - WoG / Wrath of Gods -> Гнев богов (WoG)
   - Flowing Blade -> Текущий клинок
   - Warrior Burn -> Пылающий воин
   - Strong Current -> Сильное течение
   - Earth's Will -> Воля земли
   - Auto -> Авто-режим / Авто
3. Перевод должен быть естественным, чистым и понятным русскоязычным игрокам.
4. Выводи ТОЛЬКО готовый переведенный Markdown текст без вступительных или заключительных фраз."""

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
        if not text or len(text.strip()) < 4:
            return text

        # Provider Cascade: NVIDIA NIM -> Gemini -> DeepSeek -> Groq -> OpenAI -> HF Serverless -> Smart Fallback
        nvidia_key = os.getenv("NVIDIA_API_KEY") or settings.NVIDIA_API_KEY
        if nvidia_key:
            res = await TranslationService._translate_nvidia(text, nvidia_key)
            if res:
                return res

        gemini_key = os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY
        if gemini_key:
            res = await TranslationService._translate_gemini(text, gemini_key)
            if res:
                return res

        deepseek_key = os.getenv("DEEPSEEK_API_KEY") or settings.DEEPSEEK_API_KEY
        if deepseek_key:
            res = await TranslationService._translate_deepseek(text, deepseek_key)
            if res:
                return res

        groq_key = os.getenv("GROQ_API_KEY") or settings.GROQ_API_KEY
        if groq_key:
            res = await TranslationService._translate_groq(text, groq_key)
            if res:
                return res

        openai_key = os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY
        if openai_key:
            res = await TranslationService._translate_openai(text, openai_key)
            if res:
                return res

        # Hugging Face Serverless Inference (Free Cloud GPU)
        hf_token = os.getenv("HF_TOKEN") or settings.HF_TOKEN
        if hf_token:
            hf_res = await TranslationService._translate_hf(text, hf_token)
            if hf_res:
                return hf_res

        # Lossless Smart Google Fallback (with placeholder preservation)
        return await TranslationService._translate_smart_fallback(text)

    @staticmethod
    async def _translate_gemini(text: str, api_key: str) -> str | None:
        try:
            session = await http_client.get_session()
            for model_name in ["gemini-2.5-flash", "gemini-1.5-flash"]:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {"text": f"{SYSTEM_PROMPT}\n\nТекст для перевода:\n{text}"}
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 4096,
                    }
                }
                async with session.post(url, json=payload, timeout=25) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        candidates = data.get("candidates", [])
                        if candidates and candidates[0].get("content", {}).get("parts"):
                            out = candidates[0]["content"]["parts"][0].get("text", "").strip()
                            if out:
                                return TranslationService._post_process(out)
        except Exception as e:
            logger.debug(f"Gemini translation failed: {e}")
    @staticmethod
    async def _translate_nvidia(text: str, api_key: str) -> str | None:
        try:
            session = await http_client.get_session()
            url = "https://integrate.api.nvidia.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            for model_name in ["meta/llama-3.3-70b-instruct", "deepseek-ai/deepseek-v3", "qwen/qwen2.5-72b-instruct"]:
                payload = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Текст для перевода:\n{text}"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 4096,
                }
                async with session.post(url, json=payload, headers=headers, timeout=30) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        res = data["choices"][0]["message"]["content"].strip()
                        if res:
                            return TranslationService._post_process(res)
        except Exception as e:
            logger.debug(f"NVIDIA NIM translation failed: {e}")
        return None

    @staticmethod
    async def _translate_deepseek(text: str, api_key: str) -> str | None:
        try:
            session = await http_client.get_session()
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Текст для перевода:\n{text}"}
                ],
                "temperature": 0.1,
            }
            async with session.post(url, json=payload, headers=headers, timeout=25) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return TranslationService._post_process(data["choices"][0]["message"]["content"].strip())
        except Exception as e:
            logger.debug(f"DeepSeek translation failed: {e}")
        return None

    @staticmethod
    async def _translate_groq(text: str, api_key: str) -> str | None:
        try:
            session = await http_client.get_session()
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Текст для перевода:\n{text}"}
                ],
                "temperature": 0.1,
            }
            async with session.post(url, json=payload, headers=headers, timeout=20) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return TranslationService._post_process(data["choices"][0]["message"]["content"].strip())
        except Exception as e:
            logger.debug(f"Groq translation failed: {e}")
        return None

    @staticmethod
    async def _translate_openai(text: str, api_key: str) -> str | None:
        try:
            session = await http_client.get_session()
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Текст для перевода:\n{text}"}
                ],
                "temperature": 0.1,
            }
            async with session.post(url, json=payload, headers=headers, timeout=25) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return TranslationService._post_process(data["choices"][0]["message"]["content"].strip())
        except Exception as e:
            logger.debug(f"OpenAI translation failed: {e}")
        return None

    @staticmethod
    async def _translate_hf(text: str, token: str) -> str | None:
        try:
            model = "Qwen/Qwen2.5-72B-Instruct"
            url = f"https://api-inference.huggingface.co/models/{model}"
            headers = {"Authorization": f"Bearer {token}"}
            prompt = (
                f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
                f"<|im_start|>user\n{text}<|im_end|>\n<|im_start|>assistant\n"
            )
            session = await http_client.get_session()
            async with session.post(url, json={"inputs": prompt, "parameters": {"max_new_tokens": 2048}}, headers=headers, timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    full = data[0].get("generated_text", "") if isinstance(data, list) else data.get("generated_text", "")
                    res = full.split("<|im_start|>assistant\n")[-1].strip()
                    if res:
                        return TranslationService._post_process(res)
        except Exception as e:
            logger.debug(f"HF translation failed: {e}")
        return None

    @staticmethod
    async def _translate_smart_fallback(text: str) -> str:
        """Безопасный фоллбэк с защитой Markdown-тегов и эмодзи от поломки."""
        code_blocks = {}
        cidx = 0
        patterns = [
            r'```[\s\S]*?```',
            r'`[^`\n]+`',
            r'\{\{[^}]+\}\}',
            r'<a?:[A-Za-z0-9_]+:\d+>',
            r'\[Video:[^\]]+\]\([^)]+\)',
            r'\[Видео:[^\]]+\]\([^)]+\)',
            r'https?://[^\s)\]]+',
            r'/api/media/[a-f0-9]+',
        ]
        masked = text
        for pat in patterns:
            for m in re.finditer(pat, masked):
                val = m.group(0)
                ph = f"XQB{cidx}BQX"
                code_blocks[ph] = val
                masked = masked.replace(val, ph, 1)
                cidx += 1

        try:
            from deep_translator import GoogleTranslator
            res = GoogleTranslator(source='auto', target='ru').translate(masked)
        except Exception:
            res = masked

        # Restore code blocks and media
        for ph, val in code_blocks.items():
            res = res.replace(ph, val)
        res = re.sub(r'XQB\d+BQX', '', res)
        return TranslationService._post_process(res)

    @staticmethod
    def _post_process(text: str) -> str:
        # Normalize tags and remove artifacts
        text = text.replace("![видео]", "![video]").replace("![изображение]", "![image]")
        # Remove unicode replacement char if any
        text = text.replace("\ufffd", "")
        return text

translation_service = TranslationService()
