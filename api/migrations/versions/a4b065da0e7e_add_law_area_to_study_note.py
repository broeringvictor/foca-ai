"""add_law_area_to_study_note

Revision ID: a4b065da0e7e
Revises: 561f86ef3dc3
Create Date: 2026-04-23 10:52:15.381009

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4b065da0e7e'
down_revision: Union[str, Sequence[str], None] = '561f86ef3dc3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add column as nullable first
    op.add_column('study_note', sa.Column('area', sa.String(length=100), nullable=True))
    
    # Fill with default
    op.execute("UPDATE study_note SET area = 'etica_profissional' WHERE area IS NULL")
    
    # Set to NOT NULL
    op.alter_column('study_note', 'area', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('study_note', 'area')
