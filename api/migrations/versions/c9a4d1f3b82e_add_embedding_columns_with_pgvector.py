"""add embedding columns with pgvector

Revision ID: c9a4d1f3b82e
Revises: dbab6171db27
Create Date: 2026-04-18 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
from pgvector.sqlalchemy import HALFVEC
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c9a4d1f3b82e"
down_revision: Union[str, Sequence[str], None] = "dbab6171db27"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.add_column(
        "study_note",
        sa.Column("embedding", HALFVEC(3072), nullable=True),
    )
    op.add_column(
        "question",
        sa.Column("embedding", HALFVEC(3072), nullable=True),
    )

    op.execute(
        "CREATE INDEX study_note_embedding_hnsw_idx "
        "ON study_note USING hnsw (embedding halfvec_cosine_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )
    op.execute(
        "CREATE INDEX question_embedding_hnsw_idx "
        "ON question USING hnsw (embedding halfvec_cosine_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS question_embedding_hnsw_idx")
    op.execute("DROP INDEX IF EXISTS study_note_embedding_hnsw_idx")
    op.drop_column("question", "embedding")
    op.drop_column("study_note", "embedding")
