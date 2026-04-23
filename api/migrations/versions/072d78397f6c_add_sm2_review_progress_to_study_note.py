"""add_sm2_review_progress_to_study_note

Revision ID: 072d78397f6c
Revises: a9cd382310e8
Create Date: 2026-04-23 10:21:23.591989

"""
from typing import Sequence, Union
import json
from datetime import date

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '072d78397f6c'
down_revision: Union[str, Sequence[str], None] = 'a9cd382310e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add column as nullable first
    op.add_column('study_note', sa.Column('review_progress', postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'), nullable=True))
    
    # Default state for existing rows
    default_progress = {
        "ease_factor": 2.5,
        "interval_days": 0,
        "next_review_date": date.today().isoformat(),
        "card_status": 0,
        "lapsed_count": 0
    }
    
    # Update existing rows
    op.execute(f"UPDATE study_note SET review_progress = '{json.dumps(default_progress)}' WHERE review_progress IS NULL")
    
    # Set to NOT NULL
    op.alter_column('study_note', 'review_progress', nullable=False)

    # Note: Autogenerate tried to drop these indexes, but they should probably stay if they are useful for vector search/filtering.
    # op.drop_index(op.f('ix_question_area'), table_name='question')
    # op.drop_index(op.f('ix_question_exam_id'), table_name='question')
    # op.drop_index(op.f('question_embedding_hnsw_idx'), table_name='question', ...)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('study_note', 'review_progress')
