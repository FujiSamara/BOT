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

    op.add_column(
        "departments", sa.Column("fingerprint_device_hex", sa.VARCHAR(length=8), nullable=True)
    )
    op.create_table(
        "workers_fingerprint",
        sa.Column("worker_id", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("department_hex", sa.VARCHAR(length=8), nullable=False),
        sa.Column("cell_number", sa.Integer(), nullable=False),
        sa.Column("rfid_card", sa.VARCHAR(length=8), nullable=False),
        sa.ForeignKeyConstraint(
            ["worker_id"],
            ["workers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "fingerprint_attempt",
        sa.Column("worker_finger_or_card", sa.VARCHAR(length=12), nullable=False),
        sa.Column("department", sa.VARCHAR(length=8), nullable=False),
        sa.Column("event_dttm", sa.DATETIME, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.add_column("workers", sa.Column("biosmart_strid", sa.TEXT, nullable=True))
    op.add_column("workers", sa.Column("bs_import", sa.BOOLEAN, nullable=True))
    op.add_column("workers", sa.Column("bs_import_error", sa.TEXT, nullable=True))
    op.add_column("workers", sa.Column("bs_import_error_text", sa.TEXT, nullable=True))
    op.add_column("departments", sa.Column("biosmart_strid", sa.TEXT, nullable=True))
    op.add_column("departments", sa.Column("bs_import", sa.BOOLEAN, nullable=True))
    op.add_column("departments", sa.Column("bs_import_error", sa.TEXT, nullable=True))
    op.add_column(
        "departments", sa.Column("bs_import_error_text", sa.TEXT, nullable=True)
    )
    op.drop_column("departments", "fingerprint_device_id")
    op.drop_table("workers_fingerprint")
