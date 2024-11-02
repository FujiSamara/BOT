"""Adding bid coordinators

Revision ID: 5d23f201dfea
Revises: 913d252cca48
Create Date: 2024-11-01 15:01:35.528568

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5d23f201dfea"
down_revision: Union[str, None] = "913d252cca48"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bid_coordinators",
        sa.Column("bid_id", sa.Integer(), nullable=False),
        sa.Column("coordinator_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["bid_id"],
            ["bids.id"],
        ),
        sa.ForeignKeyConstraint(
            ["coordinator_id"],
            ["workers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("bid_coordinators")
