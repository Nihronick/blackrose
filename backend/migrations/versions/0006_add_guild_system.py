"""add guild system tables

Revision ID: 0006
Revises: 0005
Create Date: 2026-08-07
"""

from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Guilds table
    op.create_table(
        "guilds",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False, unique=True),
        sa.Column("icon_url", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("max_members", sa.Integer(), server_default="20", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
    )

    # 2. Guild members table
    op.create_table(
        "guild_members",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("guild_id", sa.Integer(), sa.ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("nickname", sa.Text(), nullable=False),
        sa.Column("rank", sa.Integer(), server_default="1", nullable=False),
        sa.Column("rank_confirmed", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("stage", sa.Integer(), server_default="0", nullable=False),
        sa.Column("guild_role", sa.Text(), server_default="'guild_member'", nullable=False),
        sa.Column("status", sa.Text(), server_default="'active'", nullable=False),
        sa.Column("status_note", sa.Text(), nullable=True),
        sa.Column("approved", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("approved_by", sa.BigInteger(), nullable=True),
        sa.Column("joined_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_guild_members_user_id", "guild_members", ["user_id"], unique=True)
    op.create_index("ix_guild_members_guild_rank", "guild_members", ["guild_id", "rank"])

    # 3. Guild join requests table
    op.create_table(
        "guild_join_requests",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("guild_id", sa.Integer(), sa.ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("nickname", sa.Text(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), server_default="'pending'", nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("resolved_by", sa.BigInteger(), nullable=True),
        sa.Column("resolved_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )

    # 4. Guild statuses table
    op.create_table(
        "guild_statuses",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("guild_id", sa.Integer(), sa.ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False),
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("color", sa.Text(), server_default="'gray'", nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
    )
    op.create_index("ix_guild_statuses_guild_key", "guild_statuses", ["guild_id", "key"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_guild_statuses_guild_key")
    op.drop_table("guild_statuses")
    op.drop_table("guild_join_requests")
    op.drop_index("ix_guild_members_guild_rank")
    op.drop_index("ix_guild_members_user_id")
    op.drop_table("guild_members")
    op.drop_table("guilds")
