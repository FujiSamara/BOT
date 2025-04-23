"""add actual residence in worker bids

Revision ID: 5d77a8e6f5e3
Revises: 23c0a06c41c6
Create Date: 2025-04-23 09:54:50.060455

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5d77a8e6f5e3"
down_revision: Union[str, None] = "23c0a06c41c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "worker_bids", sa.Column("actual_residence", sa.String(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("worker_bids", "actual_residence")
