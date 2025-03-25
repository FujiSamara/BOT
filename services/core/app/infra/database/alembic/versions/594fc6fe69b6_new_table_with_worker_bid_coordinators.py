"""New table with worker bid coordinators

Revision ID: 594fc6fe69b6
Revises: 078cf572b50a
Create Date: 2025-03-24 13:52:53.493164

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "594fc6fe69b6"
down_revision: Union[str, None] = "078cf572b50a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "worker_bid_coordinators",
        sa.Column("worker_bid_id", sa.Integer(), nullable=False),
        sa.Column("coordinator_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["coordinator_id"],
            ["workers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["worker_bid_id"],
            ["worker_bids.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("worker_bid_coordinators")
