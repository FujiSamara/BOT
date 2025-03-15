"""Adding auth client

Revision ID: 4dab59de1936
Revises: d68cb5ee9b19
Create Date: 2025-03-15 07:58:42.754504

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4dab59de1936"
down_revision: Union[str, None] = "d68cb5ee9b19"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "auth_clients",
        sa.Column("secret", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("auth_clients")
