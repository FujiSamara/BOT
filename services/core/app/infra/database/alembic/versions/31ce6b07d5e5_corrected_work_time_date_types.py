"""Corrected work time date types

Revision ID: 31ce6b07d5e5
Revises: 126cbefe665d
Create Date: 2024-10-09 15:50:42.780949

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "31ce6b07d5e5"
down_revision: Union[str, None] = "126cbefe665d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "work_times",
        "work_begin",
        existing_type=sa.VARCHAR(),
        type_=sa.DateTime(),
        existing_nullable=True,
        postgresql_using="work_begin::timestamp without time zone",
    )
    op.alter_column(
        "work_times",
        "work_end",
        existing_type=sa.VARCHAR(),
        type_=sa.DateTime(),
        existing_nullable=True,
        postgresql_using="work_end::timestamp without time zone",
    )
    op.alter_column(
        "work_times",
        "day",
        existing_type=sa.VARCHAR(),
        type_=sa.Date(),
        existing_nullable=True,
        postgresql_using="day::date",
    )


def downgrade() -> None:
    op.alter_column(
        "work_times",
        "day",
        existing_type=sa.Date(),
        type_=sa.VARCHAR(),
        existing_nullable=True,
        postgresql_using="day::varchar",
    )
    op.alter_column(
        "work_times",
        "work_end",
        existing_type=sa.DateTime(),
        type_=sa.VARCHAR(),
        existing_nullable=True,
        postgresql_using="work_end::varchar",
    )
    op.alter_column(
        "work_times",
        "work_begin",
        existing_type=sa.DateTime(),
        type_=sa.VARCHAR(),
        existing_nullable=True,
        postgresql_using="work_begin::varchar",
    )
