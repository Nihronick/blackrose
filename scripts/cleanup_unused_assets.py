import os
import re

# Пути
ICONS_PY = r"c:\Users\moroz\Desktop\blackrose-free\backend\icons.py"
ASSETS_DIR = r"c:\Users\moroz\Desktop\blackrose-free\frontend\public\assets\images\icons"

def clean():
    if not os.path.exists(ICONS_PY): return
    with open(ICONS_PY, 'r', encoding='utf-8') as f:
        content = f.read()
    used_files = set(re.findall(r'_url\("(.*?)"\)', content))
    all_quoted = re.findall(r'"(.*?)"', content)
    for q in all_quoted:
        if any(q.startswith(d) for d in ["class_etc/", "discord_migrated/", "promotion/", "skills/", "spirits/"]):
            used_files.add(q)
    
    if not os.path.exists(ASSETS_DIR): return
    for root, dirs, files in os.walk(ASSETS_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, ASSETS_DIR).replace("\\", "/")
            if rel_path not in used_files:
                os.remove(full_path)
                print(f"Removed unused asset: {rel_path}")

if __name__ == "__main__":
    clean()
