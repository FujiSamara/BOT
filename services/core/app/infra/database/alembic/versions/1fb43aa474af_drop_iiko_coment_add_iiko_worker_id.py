"""drop iiko coment add iiko_worker_id

Revision ID: 1fb43aa474af
Revises: f8875a2f4074
Create Date: 2025-02-10 11:42:30.620540

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1fb43aa474af"
down_revision: Union[str, None] = "f8875a2f4074"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "worker_bids", sa.Column("iiko_worker_id", sa.Integer(), nullable=True)
    )
    op.drop_column("worker_bids", "iiko_service_comment")
    op.add_column("workers", sa.Column("iiko_id", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("workers", "iiko_id")
    op.add_column(
        "worker_bids",
        sa.Column(
            "iiko_service_comment", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.drop_column("worker_bids", "iiko_worker_id")
