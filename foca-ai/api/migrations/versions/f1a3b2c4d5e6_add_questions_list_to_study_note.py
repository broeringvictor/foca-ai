"""add questions list to study_note

Revision ID: f1a3b2c4d5e6
Revises: dbab6171db27
Create Date: 2026-04-21 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f1a3b2c4d5e6"
down_revision: Union[str, Sequence[str], None] = "dbab6171db27"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "study_note",
        sa.Column(
            "questions",
            postgresql.JSONB(),
            nullable=False,
            server_default="[]",
        ),
    )


def downgrade() -> None:
    op.drop_column("study_note", "questions")
