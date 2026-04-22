"""create a entity base for consistency

Revision ID: 041957e4dad4
Revises: 6ff5dee3e1b5
Create Date: 2026-04-16 11:33:28.685392

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "041957e4dad4"
down_revision: Union[str, Sequence[str], None] = "6ff5dee3e1b5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("users", "create_at", new_column_name="created_at")
    op.alter_column("users", "modified_at", new_column_name="updated_at")


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("users", "created_at", new_column_name="create_at")
    op.alter_column("users", "updated_at", new_column_name="modified_at")
