"""Init migration

Revision ID: 9337505fdbeb
Revises:
Create Date: 2025-03-22 12:38:22.954528

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9337505fdbeb"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "divisions",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "business_cards",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("division_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["division_id"],
            ["divisions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "dish_divisions",
        sa.Column("dish_id", sa.Integer(), nullable=False),
        sa.Column("division_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["division_id"],
            ["divisions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "business_card_materials",
        sa.Column("external_id", sa.Integer(), nullable=False),
        sa.Column("card_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["card_id"],
            ["business_cards.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("business_card_materials")
    op.drop_table("dish_divisions")
    op.drop_table("business_cards")
    op.drop_table("divisions")
