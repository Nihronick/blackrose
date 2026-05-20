"""fix local_admins table — add id identity column

Revision ID: 0004
Revises: 0003
Create Date: 2026-04-04

Миграция 0003 создала local_admins с username как TEXT primary key.
ORM-модель ожидает id (Integer Identity, PK) + username (String unique).
Эта миграция приводит существующую таблицу к нужной схеме.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Проверяем, есть ли уже колонка id (если 0003 уже применялась в новом виде — пропускаем)
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='local_admins' AND column_name='id'"
    ))
    if result.fetchone():
        # id уже есть — ничего не делаем
        return

    # 1. Снять primary key с username
    op.execute("ALTER TABLE local_admins DROP CONSTRAINT IF EXISTS local_admins_pkey")

    # 2. Изменить тип username с TEXT на VARCHAR(50)
    op.alter_column("local_admins", "username",
                    existing_type=sa.Text(),
                    type_=sa.String(50),
                    nullable=False)

    # 3. Добавить id как SERIAL (identity) primary key
    op.execute("ALTER TABLE local_admins ADD COLUMN id SERIAL PRIMARY KEY")

    # 4. Добавить unique constraint на username (если не существует)
    op.execute(
        "DO $$ BEGIN "
        "IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE tablename='local_admins' AND indexname='ix_local_admins_username') "
        "THEN CREATE UNIQUE INDEX ix_local_admins_username ON local_admins(username); "
        "END IF; END $$"
    )


def downgrade() -> None:
    # Откат: убрать id, сделать username primary key снова
    op.execute("ALTER TABLE local_admins DROP COLUMN IF EXISTS id")
    op.execute("DROP INDEX IF EXISTS ix_local_admins_username")
    op.execute("ALTER TABLE local_admins ADD PRIMARY KEY (username)")
