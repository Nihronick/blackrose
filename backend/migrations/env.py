"""
Alembic env.py — синхронный режим через psycopg2.
asyncpg используется в runtime приложения, но Alembic CLI работает синхронно.

Установка:
    pip install alembic psycopg2-binary

Применить миграции:
    cd backend
    alembic upgrade head

Создать новую миграцию:
    alembic revision --autogenerate -m "описание изменения"

Откатить последнюю:
    alembic downgrade -1
"""

import os
import re
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _make_sync_url(url: str) -> str:
    """asyncpg:// → psycopg2:// для Alembic CLI."""
    url = re.sub(r"^postgresql\+asyncpg://", "postgresql+psycopg2://", url)
    url = re.sub(r"^postgres://", "postgresql+psycopg2://", url)
    url = re.sub(r"^postgresql://", "postgresql+psycopg2://", url)
    return url


def get_url() -> str:
    raw = os.environ.get("DATABASE_URL", "")
    if not raw:
        raise RuntimeError("DATABASE_URL не задан")
    return _make_sync_url(raw)


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=None,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = get_url()
    connectable = create_engine(url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=None)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
