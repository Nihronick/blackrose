"""
Этап 5: Дедупликация и перманентное кэширование медиафайлов (картинки, видео, кастомные эмодзи).
"""
import json
import re
from typing import Dict, List

from .config import MEDIA_CACHE_FILE
from .backend_client import BackendClient


def _canonical_url(url: str) -> str:
    """Удаление временных query-параметров Discord CDN (?ex=...&is=...&hm=...)."""
    if not url:
        return ""
    if "?" in url and "cdn.discordapp.com" in url:
        return url.split("?")[0]
    return url


def _load_cache() -> Dict[str, str]:
    """Загрузка таблицы кэша медиа {canonical_url: permanent_url}."""
    if MEDIA_CACHE_FILE.exists():
        try:
            with open(MEDIA_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_cache(cache: Dict[str, str]):
    """Сохранение таблицы кэша на диск."""
    try:
        with open(MEDIA_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"  [WARN] Ошибка сохранения media_cache.json: {e}")


def run(guides: List[Dict]) -> List[Dict]:
    """Этап 5: скачивание и дедупликация медиафайлов."""
    print("\n" + "=" * 60)
    print("  📸 Этап 5: Дедупликация и кэширование медиа")
    print("=" * 60)

    # Авторизация в бэкенде для доступа к /api/admin/media/import-url
    BackendClient.login()

    cache = _load_cache()
    cached_hits = 0
    new_uploads = 0

    def resolve_url(raw_url: str) -> str:
        nonlocal cached_hits, new_uploads
        if not raw_url:
            return raw_url
        
        # Уже в перманентном хранилище
        if any(h in raw_url for h in ["huggingface.co", "nihronick", "/api/media/"]):
            return raw_url

        canon = _canonical_url(raw_url)
        if canon in cache:
            cached_hits += 1
            return cache[canon]

        # Новый файл -> загрузка в облачный бэкенд
        perm = BackendClient.persist_media(raw_url)
        if perm and perm != raw_url:
            cache[canon] = perm
            new_uploads += 1
            return perm
        return raw_url

    for idx, g in enumerate(guides):
        # 1. Фото
        new_photos = []
        for p in g.get("raw_photos", []):
            new_photos.append(resolve_url(p))
        g["raw_photos"] = new_photos

        # 2. Видео
        new_videos = []
        for v in g.get("raw_videos", []):
            new_videos.append(resolve_url(v))
        g["raw_videos"] = new_videos

        # 3. Ссылки внутри текста статьи
        text = g.get("raw_text", "")
        discord_urls = set(re.findall(r'https://cdn\.discordapp\.com/[^\s)\]"\'>]+', text))
        for d_url in discord_urls:
            p_url = resolve_url(d_url)
            if p_url != d_url:
                text = text.replace(d_url, p_url)
        g["raw_text"] = text

        if (idx + 1) % 25 == 0 or (idx + 1) == len(guides):
            print(f"  ...обработано {idx+1}/{len(guides)} гайдов (кэш: {cached_hits}, новых: {new_uploads})")

    _save_cache(cache)

    print(f"\n  ✅ Этап 5 завершен:")
    print(f"     ⚡ Взято из кэша (0 запросов): {cached_hits}")
    print(f"     ☁️ Загружено новых:           {new_uploads}")
    print(f"     📦 Всего в реестре кэша:      {len(cache)}")
    return guides
