"""add space in question.statement

Revision ID: 906848201681
Revises: b42494b3ff19
Create Date: 2026-04-23 19:23:29.831482

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '906848201681'
down_revision: Union[str, Sequence[str], None] = 'b42494b3ff19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
