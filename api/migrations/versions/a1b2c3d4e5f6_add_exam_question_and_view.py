"""add exam, question and read-only views

Revision ID: a1b2c3d4e5f6
Revises: b7d22de56a11
Create Date: 2026-04-16 21:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "b7d22de56a11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


QUESTION_DETAIL_VIEW = """
CREATE VIEW v_question_detail AS
SELECT
    q.id          AS question_id,
    q.statement,
    q.area,
    q.correct,
    q.tags,
    q.created_at,
    e.id          AS exam_id,
    e.name        AS exam_name,
    e.edition     AS exam_edition,
    e.year        AS exam_year,
    e.board       AS exam_board,
    e.first_phase_date,
    e.second_phase_date
FROM question q
JOIN exam e ON e.id = q.exam_id;
"""

EXAM_STATS_VIEW = """
CREATE VIEW v_exam_stats AS
SELECT
    e.id      AS exam_id,
    e.name,
    e.edition,
    e.year,
    COALESCE(agg.total_questions, 0) AS total_questions,
    agg.questions_by_area
FROM exam e
LEFT JOIN (
    SELECT
        exam_id,
        COUNT(*) AS total_questions,
        jsonb_object_agg(area, cnt) AS questions_by_area
    FROM (
        SELECT exam_id, area, COUNT(*) AS cnt
        FROM question
        GROUP BY exam_id, area
    ) per_area
    GROUP BY exam_id
) agg ON agg.exam_id = e.id;
"""


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "exam",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("edition", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("board", sa.String(length=100), nullable=False),
        sa.Column("first_phase_date", sa.Date(), nullable=True),
        sa.Column("second_phase_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "question",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("exam_id", sa.UUID(), nullable=False),
        sa.Column("statement", sa.String(length=1500), nullable=False),
        sa.Column("area", sa.String(length=30), nullable=False),
        sa.Column("correct", sa.String(length=1), nullable=False),
        sa.Column("alternative_a", sa.String(length=1000), nullable=False),
        sa.Column("alternative_b", sa.String(length=1000), nullable=False),
        sa.Column("alternative_c", sa.String(length=1000), nullable=False),
        sa.Column("alternative_d", sa.String(length=1000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "tags",
            postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), "sqlite"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["exam_id"], ["exam.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_question_exam_id", "question", ["exam_id"])
    op.create_index("ix_question_area", "question", ["area"])

    op.execute(QUESTION_DETAIL_VIEW)
    op.execute(EXAM_STATS_VIEW)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP VIEW IF EXISTS v_exam_stats")
    op.execute("DROP VIEW IF EXISTS v_question_detail")
    op.drop_index("ix_question_area", table_name="question")
    op.drop_index("ix_question_exam_id", table_name="question")
    op.drop_table("question")
    op.drop_table("exam")
