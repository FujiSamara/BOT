"""Removing document

Revision ID: f43fc7e19381
Revises: 0ab33376f409
Create Date: 2025-04-01 09:11:32.660889

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f43fc7e19381"
down_revision: Union[str, None] = "0ab33376f409"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("business_cards", "document")


def downgrade() -> None:
    op.add_column(
        "business_cards",
        sa.Column("document", sa.INTEGER(), autoincrement=False, nullable=True),
    )
