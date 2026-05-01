import asyncio
import logging
import os
from datetime import datetime

from database import init_db, get_sessionmaker, close_pool
from db_models import Guide, Category
from sqlalchemy import select
from storage import hf_api, HF_DATASET_REPO, HF_PATH, delete_files

logger = logging.getLogger("blackrose.gc")

async def run_storage_gc():
    """
    Garbage Collector для хранилища Hugging Face.
    Удаляет файлы, которые есть в репозитории, но отсутствуют в базе данных.
    """
    if not HF_DATASET_REPO:
        logger.warning("HF_DATASET_REPO not configured. Skipping GC.")
        return

    logger.info("🚀 Starting Storage Garbage Collection...")
    
    await init_db()
    try:
        # 1. Собираем все файлы, на которые ссылается БД
        db_files = set()
        async with get_sessionmaker()() as session:
            # Гайды
            guides_result = await session.execute(select(Guide))
            for g in guides_result.scalars():
                if g.icon_url: db_files.add(g.icon_url)
                if g.photo: db_files.update(g.photo)
                if g.video: db_files.update(g.video)
                if g.document: db_files.update(g.document)
            
            # Категории
            cats_result = await session.execute(select(Category))
            for c in cats_result.scalars():
                if c.icon_url: db_files.add(c.icon_url)

        logger.info(f"DB references {len(db_files)} files.")

        # 2. Получаем список всех файлов в репозитории HF
        try:
            repo_files = hf_api.list_repo_files(repo_id=HF_DATASET_REPO, repo_type="dataset")
            # Фильтруем только те, что в нашей папке uploads
            storage_files = [f for f in repo_files if f.startswith(HF_PATH)]
            logger.info(f"Storage contains {len(storage_files)} files in '{HF_PATH}' folder.")
        except Exception as e:
            logger.error(f"Failed to list HF repo files: {e}")
            return

        # 3. Сравниваем
        # Превращаем пути из сторейджа в полные URL для сравнения с БД
        prefix = f"https://huggingface.co/datasets/{HF_DATASET_REPO}/resolve/main/"
        
        orphaned_paths = []
        for path in storage_files:
            full_url = prefix + path
            if full_url not in db_files:
                # Проверка: не удаляем .gitkeep или другие важные файлы
                if path.endswith(".gitkeep") or path.endswith("README.md"):
                    continue
                orphaned_paths.append(path)

        if not orphaned_paths:
            logger.info("✅ No orphaned files found. Storage is clean.")
            return

        logger.info(f"♻️ Found {len(orphaned_paths)} orphaned files. Deleting...")
        
        # Удаляем пачками по 10, чтобы не забивать API
        batch_size = 10
        deleted_count = 0
        for i in range(0, len(orphaned_paths), batch_size):
            batch = orphaned_paths[i:i + batch_size]
            deleted_count += await delete_files(batch)
            logger.info(f"Progress: {deleted_count}/{len(orphaned_paths)}")
            await asyncio.sleep(1) # Небольшая пауза между пачками

        logger.info(f"✨ GC finished. Deleted {deleted_count} files.")

    except Exception as e:
        logger.error(f"GC failed with error: {e}", exc_info=True)
    finally:
        await close_pool()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    async def main_loop():
        while True:
            await run_storage_gc()
            logger.info("Next GC run in 24 hours...")
            await asyncio.sleep(24 * 3600)
            
    asyncio.run(main_loop())
