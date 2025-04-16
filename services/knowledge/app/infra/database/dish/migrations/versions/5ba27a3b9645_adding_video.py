"""Adding video

Revision ID: 5ba27a3b9645
Revises: 4cc98e61461f
Create Date: 2025-04-01 08:52:07.672541

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5ba27a3b9645"
down_revision: Union[str, None] = "4cc98e61461f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("ttk_products", sa.Column("video", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("ttk_products", "video")
