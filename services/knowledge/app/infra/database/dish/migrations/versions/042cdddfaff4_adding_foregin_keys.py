"""Adding foregin keys

Revision ID: 042cdddfaff4
Revises: 7a00aa4ed82e
Create Date: 2025-03-24 08:29:37.618867

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "042cdddfaff4"
down_revision: Union[str, None] = "7a00aa4ed82e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_foreign_key(None, "assembly_charts", "modifiers", ["modifier_id"], ["id"])
    op.create_foreign_key(None, "assembly_charts", "products", ["product_id"], ["id"])
    op.create_foreign_key(None, "modifiers", "dishes", ["dish_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint(None, "modifiers", type_="foreignkey")
    op.drop_constraint(None, "assembly_charts", type_="foreignkey")
    op.drop_constraint(None, "assembly_charts", type_="foreignkey")
