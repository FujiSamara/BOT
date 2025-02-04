"""Adding photo to worktimes

Revision ID: 8f7576485253
Revises: a65c0aec8dfb
Create Date: 2024-10-29 00:18:42.756878

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8f7576485253"
down_revision: Union[str, None] = "a65c0aec8dfb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("work_times", sa.Column("photo_b64", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("work_times", "photo_b64")
