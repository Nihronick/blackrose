import re
from pathlib import Path

# Все URL видео из гайдов
guide_files = Path("guides/ru").rglob("*.md")
url_map = {}

for gf in guide_files:
    content = gf.read_text(encoding="utf-8", errors="ignore")
    for match in re.findall(r'\(https://[^\s)]+\.mp4\)', content):
        url = match.strip("()")
        fn = url.split("/")[-1]
        url_map[fn] = url

# Какие файлы существуют на диске
video_path = Path("assets/images/slayerpedia/video")
existing = {}
for vf in video_path.glob("*.mp4"):
    existing[vf.name] = str(vf)

# Создать маппинг
print("МАППИНГ: ЧТО ГАЙДЫ ИЩУТ vs ЧТО НА ДИСКЕ\n")
mapping = []
for wanted_name in sorted(url_map.keys()):
    if wanted_name not in existing:
        # Найти похожий файл на диске
        parts = wanted_name.split("__")
        if len(parts) > 1:
            id_part = parts[-1]
        else:
            id_part = wanted_name.split(".")[0]
        
        # Ищем файл с таким ID
        matching = [f for f in existing.keys() if id_part in f]
        if matching:
            print(f"❌ ГАЙД ИЩЕТ:  {wanted_name}")
            print(f"   НА ДИСКЕ:   {matching[0]}")
            mapping.append((matching[0], wanted_name))
            print()

print(f"\nВсего нужно переименовать: {len(mapping)} файлов")
