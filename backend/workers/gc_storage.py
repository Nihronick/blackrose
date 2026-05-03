import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

from core.db import init_db, get_sessionmaker, close_pool
from models.db_models import Guide, Category
from sqlalchemy import select
from services.storage.hf_storage import hf_api, HF_DATASET_REPO, HF_PATH, delete_files

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
        import re
        
        # Регулярка для поиска URL-ов нашего хранилища
        # Ищем как в Markdown ![...](url), так и просто в тексте
        url_pattern = re.compile(r'https://huggingface\.co/datasets/[^/]+/[^/]+/resolve/main/([^"\'\s)>]+)')
        blob_pattern = re.compile(r'https://huggingface\.co/datasets/[^/]+/[^/]+/blob/main/([^"\'\s)>]+)')

        async with get_sessionmaker()() as session:
            # Гайды
            guides_result = await session.execute(select(Guide))
            for g in guides_result.scalars():
                # Проверяем иконку
                if g.icon_url: db_files.add(g.icon_url)
                
                # Проверяем массивы
                if g.photo: db_files.update(g.photo)
                if g.video: db_files.update(g.video)
                if g.document: db_files.update(g.document)
                
                # ВНИМАНИЕ: Парсим основной текст гайда!
                if g.text:
                    # Ищем все вхождения путей в тексте
                    found_paths = url_pattern.findall(g.text)
                    for p in found_paths:
                        db_files.add(p) # Добавляем путь (без префикса)
                    
                    found_blob_paths = blob_pattern.findall(g.text)
                    for p in found_blob_paths:
                        db_files.add(p)

            # Категории
            cats_result = await session.execute(select(Category))
            for c in cats_result.scalars():
                if c.icon_url: db_files.add(c.icon_url)

        # Нормализуем db_files: оставляем только относительные пути (от корня репозитория)
        # Это защитит нас от разницы в доменах/протоколах
        normalized_db_paths = set()
        for item in db_files:
            if not isinstance(item, str): continue
            
            # Если это полный URL
            if "resolve/main/" in item:
                normalized_db_paths.add(item.split("resolve/main/")[1])
            elif "blob/main/" in item:
                normalized_db_paths.add(item.split("blob/main/")[1])
            else:
                # Если это уже путь
                normalized_db_paths.add(item)

        logger.info(f"DB references {len(normalized_db_paths)} unique files.")

        # 2. Получаем список всех файлов в репозитории HF
        try:
            # Используем расширенный метод для получения метаданных (нужно время создания)
            repo_files_iter = hf_api.list_repo_tree(
                repo_id=HF_DATASET_REPO, 
                repo_type="dataset", 
                path_in_repo=HF_PATH,
                recursive=True
            )
            
            # Собираем файлы и фильтруем по времени (Grace Period: 24 часа)
            now = datetime.now()
            storage_files = []
            grace_period_count = 0
            
            for f in repo_files_iter:
                # Нам нужны только файлы
                if f.type != "file": continue
                
                # Проверяем "возраст" файла (если API отдает дату изменения)
                if hasattr(f, 'last_commit') and f.last_commit:
                    commit_date = f.last_commit.created_at
                    # Если файлу меньше 24 часов - не трогаем его
                    if (now.replace(tzinfo=commit_date.tzinfo) - commit_date).total_seconds() < 24 * 3600:
                        grace_period_count += 1
                        continue
                
                storage_files.append(f.path)
                
            logger.info(f"Storage contains {len(storage_files)} mature files. (Skipped {grace_period_count} new files via grace period)")
        except Exception as e:
            # Если папка не найдена (404), значит она пустая - это не ошибка
            if "404" in str(e) or "Entry Not Found" in str(e):
                logger.info(f"📂 Folder '{HF_PATH}' is empty or does not exist. Nothing to clean.")
                return
            logger.error(f"Failed to list HF repo files: {e}")
            return

        # 3. Сравниваем
        orphaned_paths = []
        for path in storage_files:
            if path not in normalized_db_paths:
                # Проверка: не удаляем .gitkeep или README
                if path.endswith(".gitkeep") or path.endswith("README.md"):
                    continue
                orphaned_paths.append(path)

        if not orphaned_paths:
            logger.info("✅ No orphaned files found. Storage is clean.")
            return

        logger.info(f"♻️ Found {len(orphaned_paths)} orphaned files. Deleting...")
        
        # Удаляем пачками по 10
        batch_size = 10
        deleted_count = 0
        for i in range(0, len(orphaned_paths), batch_size):
            batch = orphaned_paths[i:i + batch_size]
            deleted_count += await delete_files(batch)
            logger.info(f"Progress: {deleted_count}/{len(orphaned_paths)}")
            await asyncio.sleep(1)

        logger.info(f"✨ GC finished. Deleted {deleted_count} files.")

    except Exception as e:
        logger.error(f"GC failed with error: {e}", exc_info=True)
    finally:
        await close_pool()

    import signal

    stop_event = asyncio.Event()

    def handle_exit():
        logger.info("Received stop signal, shutting down...")
        stop_event.set()

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, handle_exit)
        except NotImplementedError:
            # Signal handling not supported on Windows
            pass

    async def main_loop():
        logger.info("GC Worker started")
        while not stop_event.is_set():
            await run_storage_gc()
            logger.info("Next GC run in 24 hours...")
            try:
                # Wait for 24 hours OR until stop_event is set
                await asyncio.wait_for(stop_event.wait(), timeout=24 * 3600)
            except asyncio.TimeoutError:
                # Normal timeout, continue to next run
                continue
        
        logger.info("GC Worker stopped gracefully")
            
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        pass
