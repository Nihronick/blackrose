import asyncio
import os
import re
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _make_async_url(url: str) -> str:
    url = re.sub(r"^postgresql\+psycopg2://", "postgresql+asyncpg://", url)
    url = re.sub(r"^postgres://", "postgresql+asyncpg://", url)
    url = re.sub(r"^postgresql://", "postgresql+asyncpg://", url)
    # asyncpg: ssl=require, не sslmode=require
    url = url.replace("sslmode=require", "ssl=require")
    # убираем channel_binding — asyncpg не поддерживает
    url = re.sub(r"[&?]channel_binding=[^&]*", "", url)
    url = re.sub(r"\?&", "?", url)
    return url


def get_url() -> str:
    # Приоритет DIRECT_URL для миграций (Elite Best Practice)
    raw = os.environ.get("DIRECT_URL") or os.environ.get("DATABASE_URL", "")
    if not raw:
        raise RuntimeError("Ни DIRECT_URL, ни DATABASE_URL не заданы")
    return _make_async_url(raw)


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url, target_metadata=None,
        literal_binds=True, dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=None)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    url = get_url()
    connectable = create_async_engine(url, poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
