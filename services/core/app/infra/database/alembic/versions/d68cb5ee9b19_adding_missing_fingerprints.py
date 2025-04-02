"""Adding missing fingerprints

Revision ID: d68cb5ee9b19
Revises: aaf81d52603c
Create Date: 2025-03-15 07:56:31.499050

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d68cb5ee9b19"
down_revision: Union[str, None] = "aaf81d52603c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_foreign_key(
        None, "workers_fingerprints", "departments", ["department_id"], ["id"]
    )
    op.create_foreign_key(
        None, "workers_fingerprints", "workers", ["worker_id"], ["id"]
    )
    op.drop_column("workers_fingerprints", "department_hex")


def downgrade() -> None:
    op.add_column(
        "workers_fingerprints",
        sa.Column("department_hex", sa.VARCHAR(), autoincrement=False, nullable=False),
    )
    op.drop_constraint(
        "workers_fingerprints_worker_id_fkey",
        "workers_fingerprints",
        type_="foreignkey",
    )
    op.drop_constraint(
        "workers_fingerprints_department_id_fkey",
        "workers_fingerprints",
        type_="foreignkey",
    )
