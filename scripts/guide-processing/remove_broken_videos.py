import re
from pathlib import Path

# Видео которые РАБОТАЮТ
working_videos = {
    "beginner-guide-rage-rave-early-late-game-rotation-late__1266503160097406986.mp4",
    "beginner-guide-rage-rave-early-late-game-rotation-late__1266503189138505728.mp4",
    "beginner-guide-rage-rave-early-late-game-rotation-late__1350263616565149706.mp4",
    "beginner-guide-rage-rave-early-late-game-rotation-late__1414463709320839229.mp4",
    "beginner-guide-rage-rave-early-late-game-rotation-late__1414464776553369681.mp4",
    "beginner-guide-rage-rave-early-late-game-rotation-late__1455018174004330566.mp4",
}

# Найти и удалить все неработающие видео-ссылки
guide_files = list(Path("guides/ru").rglob("*.md"))
removed_count = 0

for gf in guide_files:
    content = gf.read_text(encoding="utf-8", errors="ignore")
    original = content
    
    # Удалить все видео-ссылки которые не в списке working_videos
    for match in re.finditer(r'\[Video:[^\]]+\]\(https://[^\s)]+/([^/]+\.mp4)\)', content):
        video_name = match.group(1)
        if video_name not in working_videos:
            # Удалить эту ссылку
            content = content.replace(match.group(0), "")
            removed_count += 1
    
    # Убрать лишние пустые строки
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    if content != original:
        gf.write_text(content, encoding="utf-8")
        print(f"✅ {gf.name} - удалено неработающих видео")

print(f"\n✅ Всего удалено неработающих видео-ссылок: {removed_count}")
print(f"✅ Сохранено рабочих видео: 6 (beginner-guide Rage+Rave)")
