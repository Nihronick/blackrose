import re
from pathlib import Path

# Все URL видео из гайдов
guide_files = Path("guides/ru").rglob("*.md")
urls = {}

for gf in guide_files:
    content = gf.read_text(encoding="utf-8", errors="ignore")
    for match in re.findall(r'\(https://[^\s)]+\.mp4\)', content):
        url = match.strip("()")
        fn = url.split("/")[-1]
        if fn not in urls:
            urls[fn] = []
        urls[fn].append(gf.name)

# Какие файлы существуют
video_path = Path("assets/images/slayerpedia/video")
existing = set(vf.name for vf in video_path.glob("*.mp4"))

print(f"Видео ссылок в гайдах: {len(urls)}")
print(f"Видео файлов на диске: {len(existing)}")

# Какие видео ссылаются но не существуют
missing = {}
for fn, sources in urls.items():
    if fn not in existing:
        missing[fn] = sources

if missing:
    print(f"\n🔴 ВИДЕО ССЫЛАЮТСЯ НО НЕ СУЩЕСТВУЮТ ({len(missing)}):")
    for fn in sorted(missing.keys())[:20]:
        print(f"  - {fn}")
else:
    print("\n✅ Все видео из ссылок существуют на диске")
