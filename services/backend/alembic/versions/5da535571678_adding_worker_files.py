"""Adding worker files

Revision ID: 5da535571678
Revises: 31ce6b07d5e5
Create Date: 2024-10-07 15:08:54.080002

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import fastapi_storages

from settings import get_settings


# revision identifiers, used by Alembic.
revision: str = "5da535571678"
down_revision: Union[str, None] = "31ce6b07d5e5"
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
        "post_files",
        sa.Column("file_id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["file_id"],
            ["files.id"],
        ),
        sa.ForeignKeyConstraint(
            ["post_id"],
            ["posts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("post_files")
    op.drop_table("files")
