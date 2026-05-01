"""extend password_hash length

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-01 18:22:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0005'
down_revision: Union[str, None] = '0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Change column length from 128 to 256
    op.alter_column('local_admins', 'password_hash',
               existing_type=sa.String(length=128),
               type_=sa.String(length=256),
               existing_nullable=False)


def downgrade() -> None:
    # Revert column length from 256 to 128
    op.alter_column('local_admins', 'password_hash',
               existing_type=sa.String(length=256),
               type_=sa.String(length=128),
               existing_nullable=False)
