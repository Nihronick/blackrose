import re
from pathlib import Path

# Все видео на диске
video_path = Path("assets/images/slayerpedia/video")
print("На ДИСКЕ видео (.mp4):")
disk_files = sorted(video_path.glob("*.mp4"))
for vf in disk_files:
    print(f"  {vf.name}")

print("\n" + "="*80 + "\n")
print("В ГАЙДАХ ищут (видео-ссылки):")

guide_files = list(Path("guides/ru").rglob("*.md"))
wanted = {}
for gf in guide_files:
    content = gf.read_text(encoding="utf-8", errors="ignore")
    for match in re.finditer(r'\(https://[^\s)]+/([^/]+\.mp4)\)', content):
        fn = match.group(1)
        if fn not in wanted:
            wanted[fn] = []
        wanted[fn].append(gf.name)

for fn in sorted(wanted.keys()):
    exists = "✅" if (video_path / fn).exists() else "❌"
    print(f"  {exists} {fn}")
    print(f"      используется в: {wanted[fn][0]}")
