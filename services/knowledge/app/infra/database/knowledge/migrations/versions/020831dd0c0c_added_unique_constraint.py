"""Added unique constraint

Revision ID: 020831dd0c0c
Revises: 9337505fdbeb
Create Date: 2025-03-24 08:57:28.351327

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "020831dd0c0c"
down_revision: Union[str, None] = "9337505fdbeb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(None, "divisions", ["path"])


def downgrade() -> None:
    op.drop_constraint(None, "divisions", type_="unique")
