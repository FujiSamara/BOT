"""Add edo field to bid

Revision ID: aaa237c15607
Revises: 2a657d82bfc9
Create Date: 2024-09-07 15:48:47.654867

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "aaa237c15607"
down_revision: Union[str, None] = "2a657d82bfc9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("bids", sa.Column("need_edm", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("bids", "need_edm")
