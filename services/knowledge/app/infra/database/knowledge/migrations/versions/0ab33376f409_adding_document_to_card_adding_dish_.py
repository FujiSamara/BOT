"""Adding document to card/Adding dish materials

Revision ID: 0ab33376f409
Revises: 442b1dffa31c
Create Date: 2025-04-01 08:53:06.625260

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0ab33376f409"
down_revision: Union[str, None] = "442b1dffa31c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dish_materials",
        sa.Column("external_id", sa.Integer(), nullable=False),
        sa.Column("dish_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("business_cards", sa.Column("document", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("business_cards", "document")
    op.drop_table("dish_materials")
