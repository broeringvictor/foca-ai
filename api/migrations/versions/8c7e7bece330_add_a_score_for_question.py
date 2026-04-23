"""add a score for question

Revision ID: 8c7e7bece330
Revises: 4b5184db3a63
Create Date: 2026-04-23 18:05:10.412710

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c7e7bece330'
down_revision: Union[str, Sequence[str], None] = '4b5184db3a63'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
