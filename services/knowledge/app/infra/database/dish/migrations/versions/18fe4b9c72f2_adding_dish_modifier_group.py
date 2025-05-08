"""Adding dish modifier group

Revision ID: 18fe4b9c72f2
Revises: 5ba27a3b9645
Create Date: 2025-05-08 12:25:50.423324

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "18fe4b9c72f2"
down_revision: Union[str, None] = "5ba27a3b9645"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ttk_modifier_groups",
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("ttk_modifiers", sa.Column("group_id", sa.Integer(), nullable=True))
    op.create_index(
        op.f("ix_ttk_modifiers_group_id"), "ttk_modifiers", ["group_id"], unique=False
    )
    op.create_index(
        op.f("ix_ttk_modifiers_product_id"),
        "ttk_modifiers",
        ["product_id"],
        unique=False,
    )
    op.create_foreign_key(
        None, "ttk_modifiers", "ttk_modifier_groups", ["group_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_ttk_modifiers_group_id", "ttk_modifiers", type_="foreignkey")
    op.drop_index(op.f("ix_ttk_modifiers_product_id"), table_name="ttk_modifiers")
    op.drop_index(op.f("ix_ttk_modifiers_group_id"), table_name="ttk_modifiers")
    op.drop_column("ttk_modifiers", "group_id")
    op.drop_table("ttk_modifier_groups")
