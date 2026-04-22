"""add questions list to study_note

Revision ID: f1a3b2c4d5e6
Revises: c9a4d1f3b82e
Create Date: 2026-04-21 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = "f1a3b2c4d5e6"
down_revision: Union[str, Sequence[str], None] = "c9a4d1f3b82e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "study_note",
        sa.Column(
            "questions",
            JSONB(),
            nullable=False,
            server_default="[]",
        ),
    )


def downgrade() -> None:
    op.drop_column("study_note", "questions")
