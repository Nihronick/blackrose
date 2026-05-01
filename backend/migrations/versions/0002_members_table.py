"""members table — dynamic user whitelist

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-28

Заменяет статический ALLOWED_USERS из env на таблицу в БД.
ALLOWED_USERS в env продолжает работать как fallback (bootstrapping).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "members",
        sa.Column("user_id", sa.BigInteger(), primary_key=True),
        sa.Column("username", sa.Text(), nullable=True),
        sa.Column("first_name", sa.Text(), nullable=True),
        sa.Column("role", sa.Text(), server_default="'member'"),  # member | admin
        sa.Column("added_by", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
        ),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
    )
    op.create_index("ix_members_active", "members", ["is_active"])


def downgrade() -> None:
    op.drop_index("ix_members_active")
    op.drop_table("members")
