"""translate law area values to portuguese and widen column

Revision ID: e0678cb7be9e
Revises: a1b2c3d4e5f6
Create Date: 2026-04-17 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e0678cb7be9e"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Old English value -> new Portuguese value. Mirrors LawArea enum.
_AREA_EN_TO_PT: dict[str, str] = {
    "constitutional": "direito_constitucional",
    "human_rights": "direitos_humanos",
    "ethics": "etica_profissional",
    "philosophy_of_law": "filosofia_do_direito",
    "international": "direito_internacional",
    "tax": "direito_tributario",
    "administrative": "direito_administrativo",
    "environmental": "direito_ambiental",
    "civil": "direito_civil",
    "consumer": "direito_do_consumidor",
    "child_and_adolescent": "eca",
    "business": "direito_empresarial",
    "criminal": "direito_penal",
    "civil_procedure": "direito_processual_civil",
    "criminal_procedure": "direito_processual_penal",
    "labor": "direito_do_trabalho",
    "labor_procedure": "direito_processual_do_trabalho",
    "social_security": "direito_previdenciario",
    "financial": "direito_financeiro",
}


def _rebuild_question_detail_view() -> None:
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
        JOIN exam e ON e.id = q.exam_id;
        """
    )


def upgrade() -> None:
    """Widen area column to 40 chars and migrate values from EN to PT."""
    # The view depends on `question.area`, so we drop it before altering the column.
    op.execute("DROP VIEW IF EXISTS v_question_detail")

    op.alter_column(
        "question",
        "area",
        existing_type=sa.String(length=30),
        type_=sa.String(length=40),
        existing_nullable=False,
    )

    for old_value, new_value in _AREA_EN_TO_PT.items():
        op.execute(
            sa.text("UPDATE question SET area = :new WHERE area = :old").bindparams(
                new=new_value, old=old_value
            )
        )

    _rebuild_question_detail_view()


def downgrade() -> None:
    """Revert Portuguese values back to English and shrink column to 30 chars."""
    op.execute("DROP VIEW IF EXISTS v_question_detail")

    for old_value, new_value in _AREA_EN_TO_PT.items():
        op.execute(
            sa.text("UPDATE question SET area = :old WHERE area = :new").bindparams(
                old=old_value, new=new_value
            )
        )

    op.alter_column(
        "question",
        "area",
        existing_type=sa.String(length=40),
        type_=sa.String(length=30),
        existing_nullable=False,
    )

    _rebuild_question_detail_view()
