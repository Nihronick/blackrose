import os
import hashlib

def get_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def find_duplicates(root_dir):
    hashes = {}
    duplicates = []
    
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            full_path = os.path.join(dirpath, f)
            h = get_md5(full_path)
            if h in hashes:
                duplicates.append((full_path, hashes[h]))
            else:
                hashes[h] = full_path
    return duplicates

if __name__ == "__main__":
    assets_dir = r"c:\Users\moroz\Desktop\blackrose-free\frontend\public\assets"
    print(f"Scanning {assets_dir}...")
    dupes = find_duplicates(assets_dir)
    if dupes:
        print(f"Found {len(dupes)} duplicate files:")
        for d in dupes:
            print(f"DUPE: {d[0]} == {d[1]}")
    else:
        print("No duplicates found.")
