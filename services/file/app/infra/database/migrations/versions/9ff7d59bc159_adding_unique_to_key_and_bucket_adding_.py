"""Adding unique to key and bucket/Adding new fields

Revision ID: 9ff7d59bc159
Revises: c6c08666cb75
Create Date: 2025-03-10 11:45:31.517760

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9ff7d59bc159"
down_revision: Union[str, None] = "c6c08666cb75"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("files", sa.Column("created", sa.DateTime(), nullable=False))
    op.add_column("files", sa.Column("confirmed", sa.Boolean(), nullable=False))
    op.create_unique_constraint("uq_key_bucket", "files", ["key", "bucket"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_key_bucket", "files", type_="unique")
    op.drop_column("files", "confirmed")
    op.drop_column("files", "created")
