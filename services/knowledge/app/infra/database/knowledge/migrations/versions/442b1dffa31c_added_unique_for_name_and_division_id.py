"""Added unique for name and division id

Revision ID: 442b1dffa31c
Revises: 020831dd0c0c
Create Date: 2025-03-24 12:51:20.545889

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "442b1dffa31c"
down_revision: Union[str, None] = "020831dd0c0c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(None, "business_cards", ["name", "division_id"])


def downgrade() -> None:
    op.drop_constraint(None, "business_cards", type_="unique")
