"""Widen status column from String(20) to String(30)

Revision ID: 0003abcd0003
Revises: 0002abcd0002
Create Date: 2026-03-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0003abcd0003"
down_revision: Union[str, None] = "0002abcd0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "uploads",
        "status",
        existing_type=sa.String(20),
        type_=sa.String(30),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "uploads",
        "status",
        existing_type=sa.String(30),
        type_=sa.String(20),
        existing_nullable=False,
    )
