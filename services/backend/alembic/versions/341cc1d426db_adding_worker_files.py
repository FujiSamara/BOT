"""Adding worker files

Revision ID: 341cc1d426db
Revises: 92b06114c96e
Create Date: 2024-10-07 09:36:16.730712

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

import fastapi_storages
from settings import get_settings


# revision identifiers, used by Alembic.
revision: str = "341cc1d426db"
down_revision: Union[str, None] = "92b06114c96e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "files",
        sa.Column(
            "file",
            fastapi_storages.integrations.sqlalchemy.FileType(
                storage=get_settings().storage
            ),
            nullable=False,
        ),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "worker_files",
        sa.Column("file_id", sa.Integer(), nullable=False),
        sa.Column("worker_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["file_id"],
            ["files.id"],
        ),
        sa.ForeignKeyConstraint(
            ["worker_id"],
            ["workers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("worker_files")
    op.drop_table("files")
