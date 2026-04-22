"""increase study_note content limit to 20000

Revision ID: b7d22de56a11
Revises: 6ff5dee3e1b5
Create Date: 2026-04-16 21:15:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7d22de56a11"
down_revision: Union[str, Sequence[str], None] = "041957e4dad4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "study_note",
        "content",
        existing_type=sa.String(length=5000),
        type_=sa.String(length=20000),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "study_note",
        "content",
        existing_type=sa.String(length=20000),
        type_=sa.String(length=5000),
        existing_nullable=True,
    )

