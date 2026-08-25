"""
Этап 3: Кластеризация сообщений Discord в логические гайды.
"""
import json
import re
from typing import Dict, List, Tuple

from .config import STRUCTURED_DIR, slugify


def _format_message(m: Dict) -> Tuple[str, List[str], List[str]]:
    """Извлечение текста, фото и видео из одного сообщения Discord."""
    content = m.get("content", "").strip()
    photos = []
    videos = []
    media_lines = []

    # Вложения
    for att in m.get("attachments", []):
        raw_url = att.get("url", "")
        if not raw_url:
            continue
        fname = att.get("filename", "").lower()
        if any(fname.endswith(ext) for ext in ('.mp4', '.webm', '.mov', '.mkv')):
            videos.append(raw_url)
            media_lines.append(f"\n\n[Video: Видеоинструкция]({raw_url})\n\n")
        else:
            photos.append(raw_url)
            media_lines.append(f"\n\n![Изображение]({raw_url})\n\n")

    # Эмбеды
    embed_lines = []
    for emb in m.get("embeds", []):
        if not isinstance(emb, dict):
            continue
        if emb.get("image") and emb["image"].get("url"):
            url = emb["image"]["url"]
            photos.append(url)
            media_lines.append(f"\n\n![Скриншот]({url})\n\n")
        if emb.get("video") and emb["video"].get("url"):
            url = emb["video"]["url"]
            videos.append(url)
            media_lines.append(f"\n\n[Video: Видео]({url})\n\n")
        if emb.get("title"):
            embed_lines.append(f"### {emb['title']}")
        if emb.get("description"):
            embed_lines.append(emb["description"].strip())
        for f in emb.get("fields", []):
            if isinstance(f, dict) and f.get("name") and f.get("value"):
                embed_lines.append(f"**{f['name']}**\n{f['value']}")

    full_text = content
    if embed_lines:
        full_text = f"{full_text}\n\n" + "\n\n".join(embed_lines)
    if media_lines:
        full_text = f"{full_text}\n" + "".join(media_lines)

    return full_text.strip(), photos, videos


def _extract_smart_title(raw_text: str, default_title: str) -> str:
    """Извлечение информативного заголовка из текста гайда."""
    for line in raw_text.split("\n"):
        clean = line.strip()
        clean = re.sub(r'^>\s*(\[![\w\s]+\])?\s*', '', clean).strip()
        clean = clean.strip("# *-_`~").strip()
        if not clean or clean.startswith(("![", "[Video:", "{{", "http://", "https://", "<a:", "<:")):
            continue
        if len(clean) >= 4:
            return clean[:80]
    return default_title


def _cluster_text_channel(msgs: List[Dict]) -> List[Dict]:
    """Кластеризация сообщений текстового канала в гайды."""
    if not msgs:
        return []

    sorted_msgs = sorted(msgs, key=lambda x: int(x.get("id", "0")))

    # Проверка: единый сборник от одного автора?
    is_unified = len(sorted_msgs) <= 15 and all(
        m.get("author", {}).get("id") == sorted_msgs[0].get("author", {}).get("id")
        or len(m.get("content", "")) >= 100
        for m in sorted_msgs
    )

    if is_unified and len(sorted_msgs) > 1:
        text_parts, all_photos, all_videos = [], [], []
        for m in sorted_msgs:
            t, p, v = _format_message(m)
            if t:
                text_parts.append(t)
            all_photos.extend(p)
            all_videos.extend(v)
        return [{
            "id": f"merged_{sorted_msgs[0]['id']}",
            "text": "\n\n---\n\n".join(text_parts),
            "photos": all_photos,
            "videos": all_videos,
            "is_merged": True
        }]

    guides = []
    for m in sorted_msgs:
        t, p, v = _format_message(m)
        if len(t) >= 60 or p or v:
            guides.append({
                "id": m["id"],
                "text": t,
                "photos": p,
                "videos": v,
                "is_merged": False
            })
    return guides


def run(channels_data: List[Dict]) -> List[Dict]:
    """Этап 3: сборка гайдов из сырых данных Discord."""
    print("\n" + "=" * 60)
    print("  🧩 Этап 3: Структурирование и кластеризация")
    print("=" * 60)

    guides = []

    for ch in channels_data:
        ch_name = ch["channel_name"]
        ch_type = ch["channel_type"]
        cat_key = slugify(ch_name)

        if ch_type == 15:
            # Форум: каждый тред = отдельный гайд
            for ti, thread in enumerate(ch.get("threads", [])):
                msgs = sorted(thread.get("messages", []), key=lambda x: int(x.get("id", "0")))
                text_parts, all_photos, all_videos = [], [], []
                for m in msgs:
                    t, p, v = _format_message(m)
                    if t:
                        text_parts.append(t)
                    all_photos.extend(p)
                    all_videos.extend(v)

                full_text = "\n\n---\n\n".join(text_parts)
                if not full_text.strip() and not all_photos and not all_videos:
                    continue

                guides.append({
                    "guide_key": f"discord_{thread['thread_id']}",
                    "category_key": cat_key,
                    "category_name": ch_name,
                    "raw_title": thread["thread_name"],
                    "raw_text": full_text,
                    "raw_photos": all_photos,
                    "raw_videos": all_videos,
                    "sort_order": ti
                })
        else:
            # Текстовый канал: кластеризация
            clusters = _cluster_text_channel(ch.get("messages", []))
            for ci, cluster in enumerate(clusters):
                raw_title = _extract_smart_title(
                    cluster["text"], f"{ch_name} — Часть #{ci+1}"
                )
                guides.append({
                    "guide_key": f"discord_{cluster['id']}",
                    "category_key": cat_key,
                    "category_name": ch_name,
                    "raw_title": raw_title,
                    "raw_text": cluster["text"],
                    "raw_photos": cluster["photos"],
                    "raw_videos": cluster["videos"],
                    "sort_order": ci
                })

    # Сохраняем промежуточный результат
    out_path = STRUCTURED_DIR / "guides.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(guides, f, ensure_ascii=False, indent=1)

    print(f"  ✅ Этап 3 завершен: {len(guides)} гайдов собрано")
    return guides
