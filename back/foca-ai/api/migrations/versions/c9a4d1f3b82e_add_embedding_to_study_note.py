"""add embedding column to study_note

Revision ID: c9a4d1f3b82e
Revises: dbab6171db27
Create Date: 2026-04-22 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import HALFVEC

revision: str = "c9a4d1f3b82e"
down_revision: Union[str, Sequence[str], None] = "f1a3b2c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    op.add_column("study_note", sa.Column("embedding", HALFVEC(3072), nullable=True))


def downgrade() -> None:
    op.drop_column("study_note", "embedding")
