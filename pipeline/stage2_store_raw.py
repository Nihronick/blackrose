"""
Этап 2: Сохранение сырых данных Discord в локальное хранилище и загрузка обратно.
"""
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from .config import RAW_DIR


def save(channels_data: List[Dict]) -> Path:
    """Сохраняет сырые данные Discord в data/raw/latest/."""
    snapshot_dir = RAW_DIR / "latest"
    if snapshot_dir.exists():
        shutil.rmtree(snapshot_dir)
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    # Полный дамп
    all_path = snapshot_dir / "_all_channels.json"
    with open(all_path, "w", encoding="utf-8") as f:
        json.dump(channels_data, f, ensure_ascii=False, indent=1)

    # Отдельные файлы по каналам
    for ch in channels_data:
        name = ch.get("channel_name", ch.get("channel_id", "unknown"))
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        ch_path = snapshot_dir / f"{safe_name}.json"
        with open(ch_path, "w", encoding="utf-8") as f:
            json.dump(ch, f, ensure_ascii=False, indent=1)

    print(f"  💾 Сохранено {len(channels_data)} каналов в {snapshot_dir}")
    return snapshot_dir


def load(snapshot_path: Optional[Path] = None) -> List[Dict]:
    """Загружает сырые данные из локального хранилища."""
    path = snapshot_path or (RAW_DIR / "latest" / "_all_channels.json")
    if not path.exists():
        print(f"  ❌ Файл не найден: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"  📂 Загружено {len(data)} каналов из {path}")
    return data


def run(channels_data: List[Dict]) -> List[Dict]:
    """Этап 2: сохранение и проход дальше."""
    print("\n" + "=" * 60)
    print("  💾 Этап 2: Сохранение сырых данных")
    print("=" * 60)
    save(channels_data)
    return channels_data
