"""Added activity type

Revision ID: f963192e4698
Revises: 4a228ca5d1cd
Create Date: 2024-10-15 18:02:58.905650

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f963192e4698"
down_revision: Union[str, None] = "4a228ca5d1cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("bids", sa.Column("activity_type", sa.String(), nullable=False))


def downgrade() -> None:
    op.drop_column("bids", "activity_type")
