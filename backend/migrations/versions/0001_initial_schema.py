"""initial schema — all tables

Revision ID: 0001
Revises:
Create Date: 2026-03-21 00:00:00.000000

Создаёт полную схему БД:
- categories, guides (с FTS tsvector + GIN индекс + trigger)
- guide_history (audit log)
- guide_tags
- guide_comments
- user_subscriptions
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── categories ────────────────────────────────────────────────
    op.create_table(
        "categories",
        sa.Column("key", sa.Text(), primary_key=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("icon_url", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
        ),
    )

    # ── guides ────────────────────────────────────────────────────
    op.create_table(
        "guides",
        sa.Column("key", sa.Text(), primary_key=True),
        sa.Column(
            "category_key",
            sa.Text(),
            sa.ForeignKey("categories.key", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("icon_url", sa.Text(), nullable=True),
        sa.Column("text", sa.Text(), server_default="''"),
        sa.Column(
            "photo",
            postgresql.ARRAY(sa.Text()),
            server_default="'{}'",
        ),
        sa.Column(
            "video",
            postgresql.ARRAY(sa.Text()),
            server_default="'{}'",
        ),
        sa.Column(
            "document",
            postgresql.ARRAY(sa.Text()),
            server_default="'{}'",
        ),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
        ),
        sa.Column("search_vec", postgresql.TSVECTOR(), nullable=True),
        sa.Column("views", sa.BigInteger(), server_default="0"),
    )

    op.create_index("idx_guides_category", "guides", ["category_key"])
    op.create_index(
        "idx_guides_fts",
        "guides",
        ["search_vec"],
        postgresql_using="gin",
    )

    # FTS trigger — обновляет search_vec при INSERT/UPDATE
    op.execute("""
        CREATE OR REPLACE FUNCTION guides_fts_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vec :=
                setweight(to_tsvector('russian', coalesce(NEW.title, '')), 'A') ||
                setweight(to_tsvector('russian', coalesce(NEW.key,   '')), 'B') ||
                setweight(to_tsvector('russian', coalesce(
                    regexp_replace(NEW.text, '<[^>]+>', '', 'g'), ''
                )), 'C');
            RETURN NEW;
        END
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE OR REPLACE TRIGGER guides_fts_trigger
        BEFORE INSERT OR UPDATE ON guides
        FOR EACH ROW EXECUTE FUNCTION guides_fts_update();
    """)

    # ── guide_history (audit log) ─────────────────────────────────
    op.create_table(
        "guide_history",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("guide_key", sa.Text(), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("changed_by", sa.BigInteger(), nullable=True),
        sa.Column(
            "changed_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
        ),
        sa.Column("snapshot", postgresql.JSONB(), nullable=True),
    )
    op.create_index("idx_guide_history_key", "guide_history", ["guide_key"])

    # ── guide_tags ────────────────────────────────────────────────
    op.create_table(
        "guide_tags",
        sa.Column(
            "guide_key",
            sa.Text(),
            sa.ForeignKey("guides.key", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tag", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("guide_key", "tag"),
    )
    op.create_index("idx_guide_tags_tag", "guide_tags", ["tag"])

    # ── guide_comments ────────────────────────────────────────────
    op.create_table(
        "guide_comments",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column(
            "guide_key",
            sa.Text(),
            sa.ForeignKey("guides.key", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.Text(), nullable=True),
        sa.Column("first_name", sa.Text(), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("idx_comments_guide", "guide_comments", ["guide_key"])

    # ── user_subscriptions ────────────────────────────────────────
    op.create_table(
        "user_subscriptions",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "category_key",
            sa.Text(),
            sa.ForeignKey("categories.key", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("user_id", "category_key"),
    )
    op.create_index("idx_subs_category", "user_subscriptions", ["category_key"])


def downgrade() -> None:
    op.drop_table("user_subscriptions")
    op.drop_table("guide_comments")
    op.drop_table("guide_tags")
    op.drop_table("guide_history")

    op.execute("DROP TRIGGER IF EXISTS guides_fts_trigger ON guides")
    op.execute("DROP FUNCTION IF EXISTS guides_fts_update()")

    op.drop_table("guides")
    op.drop_table("categories")
