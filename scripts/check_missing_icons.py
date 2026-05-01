import os
import re

def get_mapped_icons():
    icons_file = os.path.join('backend', 'icons.py')
    with open(icons_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract all strings inside _url("...")
    mapped = set(re.findall(r'_url\("([^"]+)"\)', content))
    return mapped

def get_physical_icons():
    base_path = os.path.join('frontend', 'public', 'assets', 'images', 'icons')
    physical = set()
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.lower().endswith(('.png', '.webp', '.jpg', '.jpeg', '.svg')):
                # Get relative path from icons folder
                rel_path = os.path.relpath(os.path.join(root, file), base_path)
                # Normalize slashes to forward slashes
                rel_path = rel_path.replace('\\', '/')
                physical.add(rel_path)
    return physical

def main():
    mapped = get_mapped_icons()
    physical = get_physical_icons()
    
    missing = physical - mapped
    
    print(f"Total physical icons: {len(physical)}")
    print(f"Total mapped entries in icons.py (via _url): {len(mapped)}")
    
    if missing:
        print(f"\nFound {len(missing)} icons in assets NOT mapped in icons.py:")
        # Sort by category
        for icon in sorted(list(missing)):
            print(f"  - {icon}")
    else:
        print("\nAll physical icons are mapped in icons.py!")

if __name__ == "__main__":
    main()
