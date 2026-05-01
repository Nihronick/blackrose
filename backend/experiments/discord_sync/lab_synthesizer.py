import re
import json
import os
from typing import List, Dict

class DiscordGuideSynthesizer:
    """
    Лабораторный инструмент для склейки разрозненных сообщений Discord в один гайд.
    """
    def __init__(self, icons_map: Dict[str, str] = None):
        # Словарь замен: :emoji: -> icons.PY_SYSTEM_CALL
        self.icons_map = icons_map or {
            "fire": "{{icon:fire}}",
            "water": "{{icon:water}}",
            "wind": "{{icon:wind}}",
            "earth": "{{icon:earth}}",
            "spirit": "{{icon:spirit}}",
            "slayer": "{{icon:slayer}}"
        }
        self.glossary = self._load_glossary()

    def clean_noise(self, text: str) -> str:
        # Убираем ссылки на юзеров <@123...>, лишние пробелы и мусор
        text = re.sub(r'<@\d+>', '', text)
        # Убираем ссылки на каналы <#123...>
        text = re.sub(r'<#\d+>', '', text)
        return text.strip()

    def map_emojis(self, text: str) -> str:
        # Регулярка для поиска дискорд-эмодзи: <:name:id>
        # Заменяем на системный тег, который потом подхватит фронтенд
        discord_emoji_re = r'<:(.*?):(\d+)>'
        
        def replace_emoji(match):
            name, eid = match.groups()
            # Здесь будет проверка по вашему словарю из icons.py
            # Если ID найден - ставим иконку, если нет - оставляем имя
            return f"{{{{icon:{eid}}}}}" # или icons.get(eid, name)

        return re.sub(discord_emoji_re, replace_emoji, text)

    def _load_glossary(self) -> Dict:
        path = os.path.join(os.path.dirname(__file__), 'glossary.json')
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def enrich_text(self, text: str) -> str:
        # Умная подсветка терминов из глоссария
        if not self.glossary: return text
        
        # Собираем все термины в один плоский словарь для поиска
        all_terms = {}
        for category in self.glossary.values():
            if isinstance(category, dict):
                all_terms.update(category)
            
        for term, full_name in all_terms.items():
            # Заменяем только целые слова (с учетом того что термин может быть коротким)
            pattern = r'\b' + re.escape(term) + r'\b'
            text = re.sub(pattern, f"{term} ({full_name})", text)
        return text

    def extract_external_media(self, text: str) -> List[str]:
        # Ищем ссылки на CDN дискорда прямо в тексте (не только во вложениях)
        urls = re.findall(r'https://cdn\.discordapp\.com/\S+', text)
        return urls

    def synthesize(self, messages: List[Dict]) -> Dict:
        """
        Берет список сообщений из одной ветки и превращает в структуру гайда.
        """
        # Сортируем по времени, чтобы не терять нить
        sorted_msgs = sorted(messages, key=lambda x: x.get('timestamp', ''))
        
        full_content = []
        media_urls = []
        
        for msg in sorted_msgs:
            content = msg.get('content', '')
            author = msg.get('author', {}).get('username', 'Unknown')
            
            # Пропускаем слишком короткие "шумные" сообщения (типа "thx", "ty", "bump")
            if len(content) < 5 and not msg.get('attachments'):
                continue
                
            # Очистка и замена иконок
            clean_text = self.clean_noise(content)
            mapped_text = self.map_emojis(clean_text)
            enriched_text = self.enrich_text(mapped_text)
            
            if enriched_text:
                # Добавляем разметку автора (потом AI это объединит, но для теста так)
                full_content.append(f"--- (Автор: {author}) ---\n{enriched_text}")
            
            # Собираем медиа
            for att in msg.get('attachments', []):
                media_urls.append({
                    "url": att.get('url'),
                    "type": att.get('content_type', 'image'),
                    "name": att.get('filename')
                })

        return {
            "raw_synthetic_text": "\n\n".join(full_content),
            "media_count": len(media_urls),
            "media_list": media_urls
        }

# --- ТЕСТОВЫЕ ДАННЫЕ (как будто из API Discord) ---
test_json = [
    {
        "author": {"username": "HalfSquirrel"},
        "content": "Eldenwood guide (for the modern fire degen) :fire:\nSpirit: Noah, Sala, Loar",
        "timestamp": "2024-04-28T10:00:00",
        "attachments": []
    },
    {
        "author": {"username": "OtherProPlayer"},
        "content": "Don't forget to use DH here! it's crucial for phase 2",
        "timestamp": "2024-04-28T10:05:00",
        "attachments": [{"url": "https://cdn.discord/image1.png", "filename": "build.png", "content_type": "image"}]
    },
    {
        "author": {"username": "HalfSquirrel"},
        "content": "Good point. Added that to the Fire Phase section. :spirit:",
        "timestamp": "2024-04-28T10:10:00",
        "attachments": []
    }
]

if __name__ == "__main__":
    lab = DiscordGuideSynthesizer()
    result = lab.synthesize(test_json)
    print("=== РЕЗУЛЬТАТ СКЛЕЙКИ ===")
    print(result["raw_synthetic_text"])
    print(f"\nНайдено медиа: {result['media_count']}")
