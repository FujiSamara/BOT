"""Remove biosmart add finger print

Revision ID: 2a657d82bfc9
Revises: 2a657d82bfc9
Create Date: 2024-10-21 11:47:07.951017

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fa37ee60dc4f"
down_revision: Union[str, None] = "2a657d82bfc9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("workers", "biosmart_strid")
    op.drop_column("workers", "bs_import")
    op.drop_column("workers", "bs_import_error")
    op.drop_column("workers", "bs_import_error_text")
    op.drop_column("departments", "biosmart_strid")
    op.drop_column("departments", "bs_import")
    op.drop_column("departments", "bs_import_error")
    op.drop_column("departments", "bs_import_error_text")

    op.add_column("workers", sa.Column("fingerprint_card", sa.VARCHAR(16), nullable=True))
    op.add_column("workers", sa.Column("fingerprint_finger_cell", sa.INTEGER, nullable=True))
    op.add_column("departments", sa.Column("fingerprint_device_id", sa.INTEGER, nullable=True))


def downgrade() -> None:
    op.add_column("workers", sa.Column("biosmart_strid", sa.TEXT, nullable=True))
    op.add_column("workers", sa.Column("bs_import", sa.BOOLEAN, nullable=True))
    op.add_column("workers", sa.Column("bs_import_error", sa.TEXT, nullable=True))
    op.add_column("workers", sa.Column("bs_import_error_text", sa.TEXT, nullable=True))
    op.add_column("departments", sa.Column("biosmart_strid", sa.TEXT, nullable=True))
    op.add_column("departments", sa.Column("bs_import", sa.BOOLEAN, nullable=True))
    op.add_column("departments", sa.Column("bs_import_error", sa.TEXT, nullable=True))
    op.add_column("departments", sa.Column("bs_import_error_text", sa.TEXT, nullable=True))

    op.drop_column("workers", "fingerprint_card")
    op.drop_column("workers", "fingerprint_finger_cell")
    op.drop_column("departments", "fingerprint_device_id")
