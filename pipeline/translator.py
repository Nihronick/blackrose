"""
ИИ-система перевода: каскад NVIDIA NIM → Gemini → Google Translate с маскировкой разметки.
"""
import json
import re
import urllib.request
import urllib.parse

from .config import NVIDIA_API_KEY, GEMINI_API_KEY, ssl_ctx
from .glossary import AI_TRANSLATE_PROMPT, CANONICAL_TITLES, TITLE_TRANSLATE_PROMPT


class DynamicAITranslator:
    """Каскадный ИИ-переводчик с защитой Markdown-разметки."""

    @staticmethod
    def _post_process(text: str) -> str:
        text = text.replace("![видео]", "![video]").replace("![изображение]", "![image]")
        text = text.replace("\ufffd", "")
        return text.strip()

    @classmethod
    def translate_title(cls, text: str) -> str:
        """Перевод заголовка раздела или гайда через ИИ с каноничным словарём."""
        clean = text.replace("-", " ").replace("_", " ").strip()
        if not clean:
            return text

        lower_clean = clean.lower()

        # 1. Точный словарь
        if lower_clean in CANONICAL_TITLES:
            return CANONICAL_TITLES[lower_clean]
        for k, v in CANONICAL_TITLES.items():
            if lower_clean == k.replace("-", " "):
                return v

        # 2. NVIDIA NIM
        if NVIDIA_API_KEY:
            try:
                url = "https://integrate.api.nvidia.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"}
                payload = {
                    "model": "meta/llama-3.3-70b-instruct",
                    "messages": [
                        {"role": "system", "content": TITLE_TRANSLATE_PROMPT},
                        {"role": "user", "content": clean}
                    ],
                    "temperature": 0.05,
                    "max_tokens": 40
                }
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
                with urllib.request.urlopen(req, context=ssl_ctx, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    res = data["choices"][0]["message"]["content"].strip().strip('"\'')
                    first_line = res.split("\n")[0].strip("# *-_`~").strip()
                    # Защита от галлюцинаций
                    if "slayer" not in clean.lower() and first_line in [
                        "Легенда Убийцы", "Легенда убийцы", "Легендарный убийца", "Убийца Легенды"
                    ]:
                        return clean
                    if first_line and len(first_line) < 60:
                        return first_line
            except Exception:
                pass

        return cls.translate_text(clean)

    @classmethod
    def translate_text(cls, text: str) -> str:
        """Каскадный перевод полного текста через доступные ИИ-модели."""
        if not text or len(text.strip()) < 5:
            return text

        # Секционное разбиение для длинных текстов
        if "\n\n---\n\n" in text and len(text) > 3000:
            sections = text.split("\n\n---\n\n")
            translated = [cls.translate_text(s.strip()) for s in sections if s.strip()]
            return "\n\n---\n\n".join(translated)

        # 1. NVIDIA NIM (Llama 3.3 70B / DeepSeek V3)
        if NVIDIA_API_KEY:
            for model_name in ["meta/llama-3.3-70b-instruct", "deepseek-ai/deepseek-v3"]:
                try:
                    url = "https://integrate.api.nvidia.com/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"}
                    payload = {
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": AI_TRANSLATE_PROMPT},
                            {"role": "user", "content": f"Текст для перевода:\n{text}"}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 4096
                    }
                    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
                    with urllib.request.urlopen(req, context=ssl_ctx, timeout=45) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        res = data["choices"][0]["message"]["content"].strip()
                        if res and len(res) > len(text) * 0.3:
                            return cls._post_process(res)
                except Exception:
                    pass

        # 2. Google Gemini Flash
        if GEMINI_API_KEY:
            for model in ["gemini-2.5-flash", "gemini-1.5-flash"]:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
                    payload = {
                        "contents": [{"parts": [{"text": f"{AI_TRANSLATE_PROMPT}\n\nТекст для перевода:\n{text}"}]}],
                        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 4096}
                    }
                    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                                headers={"Content-Type": "application/json"}, method="POST")
                    with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        candidates = data.get("candidates", [])
                        if candidates and candidates[0].get("content", {}).get("parts"):
                            res = candidates[0]["content"]["parts"][0].get("text", "").strip()
                            if res and len(res) > len(text) * 0.3:
                                return cls._post_process(res)
                except Exception:
                    pass

        # 3. Fallback: Google Translate с маскировкой
        return cls._translate_smart_fallback(text)

    @classmethod
    def _translate_single_short_chunk(cls, text: str) -> str:
        """Перевод короткого фрагмента через Google Translate с маскировкой разметки."""
        if not text.strip():
            return text
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
            encoded = urllib.parse.quote(masked)
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ru&dt=t&q={encoded}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                translated = "".join(seg[0] for seg in result[0] if seg and seg[0])
        except Exception:
            translated = masked

        for ph, val in code_blocks.items():
            translated = translated.replace(ph, val)
        translated = re.sub(r'XQB\d+BQX', '', translated)
        return cls._post_process(translated)

    @classmethod
    def _translate_smart_fallback(cls, text: str) -> str:
        """Итеративный перевод длинного текста чанками через Google Translate."""
        if len(text) <= 1000:
            return cls._translate_single_short_chunk(text)

        # Итеративное разбиение на чанки по ~1000 символов (без рекурсии!)
        chunks = []
        current_lines = []
        current_len = 0
        for line in text.split("\n"):
            if current_len + len(line) + 1 > 1000 and current_lines:
                chunks.append("\n".join(current_lines))
                current_lines = [line]
                current_len = len(line)
            else:
                current_lines.append(line)
                current_len += len(line) + 1
        if current_lines:
            chunks.append("\n".join(current_lines))

        translated_chunks = [cls._translate_single_short_chunk(c) for c in chunks if c.strip()]
        return "\n".join(translated_chunks)
