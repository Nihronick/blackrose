import re
from pathlib import Path

# Шаг 1: Собрать все видео на диске и их ID
video_path = Path("assets/images/slayerpedia/video")
disk_videos = {}
for vf in sorted(video_path.glob("*.mp4")):
    # Извлечь ID из имени (последняя числа после __или-)
    name = vf.name
    # Ищем числовой ID в конце
    match = re.search(r'(\d+)\.mp4$', name)
    if match:
        vid_id = match.group(1)
        disk_videos[vid_id] = name

print(f"На диске найдено видео: {len(disk_videos)}")

# Шаг 2: Найти все видео-ссылки в гайдах
guide_files = list(Path("guides/ru").rglob("*.md"))
replacements = []

for gf in guide_files:
    content = gf.read_text(encoding="utf-8", errors="ignore")
    original_content = content
    
    # Найти все видео-ссылки
    for match in re.finditer(r'\[Video:[^\]]+\]\(https://[^\s)]+/([^/]+\.mp4)\)', content):
        wanted_name = match.group(1)
        
        if wanted_name not in disk_videos.values():
            # Попытаться найти правильный файл по ID
            # Извлечь ID из wanted_name
            id_match = re.search(r'(\d+)\.mp4$', wanted_name)
            if id_match:
                vid_id = id_match.group(1)
                if vid_id in disk_videos:
                    correct_name = disk_videos[vid_id]
                    # Заменить URL
                    old_url = match.group(0)
                    new_url = old_url.replace(wanted_name, correct_name)
                    content = content.replace(old_url, new_url)
                    replacements.append({
                        'file': gf.name,
                        'old': wanted_name,
                        'new': correct_name
                    })
    
    # Если был какой-то контент изменён - сохранить
    if content != original_content:
        gf.write_text(content, encoding="utf-8")

print(f"\nОбновлено ссылок: {len(replacements)}\n")
for r in replacements:
    print(f"📄 {r['file']}")
    print(f"   ❌ было: {r['old']}")
    print(f"   ✅ стало: {r['new']}")
    print()
