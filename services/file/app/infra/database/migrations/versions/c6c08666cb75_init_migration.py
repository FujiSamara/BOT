"""Init migration

Revision ID: c6c08666cb75
Revises:
Create Date: 2025-03-09 19:38:22.374098

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c6c08666cb75"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "files",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("ext", sa.String(), nullable=True),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("bucket", sa.String(), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("files")
