"""add embedding columns to study_note and question

Revision ID: c9a4d1f3b82e
Revises: dbab6171db27
Create Date: 2026-04-22 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import HALFVEC

revision: str = "c9a4d1f3b82e"
down_revision: Union[str, Sequence[str], None] = "dbab6171db27"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Add embedding to study_note
    op.add_column("study_note", sa.Column("embedding", HALFVEC(3072), nullable=True))

    # Add embedding to question
    op.add_column("question", sa.Column("embedding", HALFVEC(3072), nullable=True))

    # Create indexes for vector similarity search
    op.execute(
        "CREATE INDEX IF NOT EXISTS study_note_embedding_hnsw_idx "
        "ON study_note USING hnsw (embedding halfvec_cosine_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS question_embedding_hnsw_idx "
        "ON question USING hnsw (embedding halfvec_cosine_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS question_embedding_hnsw_idx")
    op.execute("DROP INDEX IF EXISTS study_note_embedding_hnsw_idx")
    op.drop_column("question", "embedding")
    op.drop_column("study_note", "embedding")
