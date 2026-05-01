import re
from pathlib import Path

# Все видео на диске - создаём маппинг по ID
video_path = Path("assets/images/slayerpedia/video")
disk_by_id = {}

for vf in video_path.glob("*.mp4"):
    name = vf.name
    # Ищем числовые ID в имени
    for match in re.finditer(r'(\d+)', name):
        vid_id = match.group(1)
        if len(vid_id) >= 10:  # Discord IDs обычно длинные
            if vid_id not in disk_by_id:
                disk_by_id[vid_id] = name

# Все видео которые ищут гайды
guide_files = list(Path("guides/ru").rglob("*.md"))
wanted = {}
for gf in guide_files:
    content = gf.read_text(encoding="utf-8", errors="ignore")
    for match in re.finditer(r'\(https://[^\s)]+/([^/]+\.mp4)\)', content):
        fn = match.group(1)
        if fn not in wanted:
            wanted[fn] = []
        wanted[fn].append(gf.name)

# Найти маппинг
print("МАППИНГ ЗАМЕН:\n")
mappings = []
for wanted_name in sorted(wanted.keys()):
    if not (video_path / wanted_name).exists():
        # Ищем ID в wanted_name
        id_match = re.search(r'(\d+)\.mp4', wanted_name)
        if id_match:
            vid_id = id_match.group(1)
            if vid_id in disk_by_id:
                actual_name = disk_by_id[vid_id]
                mappings.append((wanted_name, actual_name))
                print(f"❌ → ✅  {wanted_name}")
                print(f"       ↓")
                print(f"       {actual_name}\n")

print(f"Всего маппингов: {len(mappings)}")
