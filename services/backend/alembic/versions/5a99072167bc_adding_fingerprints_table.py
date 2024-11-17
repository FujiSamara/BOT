"""Adding fingerprints table

Revision ID: 5a99072167bc
Revises: 736d3489bf3d
Create Date: 2024-11-17 20:36:12.772563

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5a99072167bc"
down_revision: Union[str, None] = "736d3489bf3d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fingerprint_attempts",
        sa.Column("worker_finger_or_card", sa.String(), nullable=False),
        sa.Column("department", sa.String(), nullable=False),
        sa.Column("event_dttm", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "workers_fingerprints",
        sa.Column("worker_id", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("department_hex", sa.String(), nullable=False),
        sa.Column("cell_number", sa.Integer(), nullable=True),
        sa.Column("rfid_card", sa.String(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_column("companies", "biosmart_strid")
    op.drop_column("companies", "bs_import_error")
    op.drop_column("companies", "bs_import")
    op.add_column(
        "departments", sa.Column("fingerprint_device_hex", sa.String(), nullable=True)
    )
    op.drop_column("departments", "biosmart_strid")
    op.drop_column("departments", "bs_import_error")
    op.drop_column("departments", "bs_import")
    op.drop_column("departments", "bs_import_error_text")
    op.drop_column("workers", "biosmart_strid")
    op.drop_column("workers", "bs_import_error")
    op.drop_column("workers", "bs_import")
    op.drop_column("workers", "bs_import_error_text")


def downgrade() -> None:
    op.add_column(
        "workers",
        sa.Column(
            "bs_import_error_text", sa.TEXT(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "workers",
        sa.Column("bs_import", sa.BOOLEAN(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "workers",
        sa.Column("bs_import_error", sa.TEXT(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "workers",
        sa.Column("biosmart_strid", sa.TEXT(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "departments",
        sa.Column(
            "bs_import_error_text", sa.TEXT(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "departments",
        sa.Column("bs_import", sa.BOOLEAN(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "departments",
        sa.Column("bs_import_error", sa.TEXT(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "departments",
        sa.Column("biosmart_strid", sa.TEXT(), autoincrement=False, nullable=True),
    )
    op.drop_column("departments", "fingerprint_device_hex")
    op.add_column(
        "companies",
        sa.Column("bs_import", sa.BOOLEAN(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "companies",
        sa.Column("bs_import_error", sa.BOOLEAN(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "companies",
        sa.Column("biosmart_strid", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.drop_table("workers_fingerprints")
    op.drop_table("fingerprint_attempts")
