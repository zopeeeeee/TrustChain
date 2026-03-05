"""Add error_message column to uploads table

Revision ID: 0002abcd0002
Revises: 0001abcd0001
Create Date: 2026-03-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0002abcd0002"
down_revision: Union[str, None] = "0001abcd0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("uploads", sa.Column("error_message", sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column("uploads", "error_message")
