"""add alternatives to v_question_detail

Revision ID: a2b3c4d5e6f7
Revises: f1a3b2c4d5e6
Create Date: 2026-04-21 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


revision: str = "a2b3c4d5e6f7"
down_revision: Union[str, Sequence[str], None] = "f1a3b2c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP VIEW IF EXISTS v_question_detail")
    op.execute(
        """
        CREATE VIEW v_question_detail AS
        SELECT
            q.id            AS question_id,
            q.statement,
            q.area,
            q.correct,
            q.alternative_a,
            q.alternative_b,
            q.alternative_c,
            q.alternative_d,
            q.tags,
            q.created_at,
            e.id            AS exam_id,
            e.name          AS exam_name,
            e.edition       AS exam_edition,
            e.year          AS exam_year,
            e.board         AS exam_board,
            e.first_phase_date,
            e.second_phase_date
        FROM question q
        JOIN exam e ON e.id = q.exam_id
        """
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS v_question_detail")
    op.execute(
        """
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
        JOIN exam e ON e.id = q.exam_id
        """
    )
