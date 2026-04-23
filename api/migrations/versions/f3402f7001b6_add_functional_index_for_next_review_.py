"""add functional index for next_review_date

Revision ID: f3402f7001b6
Revises: 8c7e7bece330
Create Date: 2026-04-23 18:12:37.813313

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3402f7001b6'
down_revision: Union[str, Sequence[str], None] = '8c7e7bece330'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQL for functional indexes in PostgreSQL
    op.execute(
        sa.text(
            "CREATE INDEX idx_study_note_next_review ON study_note ((review_progress->>'next_review_date'))"
        )
    )
    op.execute(
        sa.text(
            "CREATE INDEX idx_study_question_next_review ON study_question ((review_progress->>'next_review_date'))"
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP INDEX idx_study_note_next_review"))
    op.execute(sa.text("DROP INDEX idx_study_question_next_review"))
