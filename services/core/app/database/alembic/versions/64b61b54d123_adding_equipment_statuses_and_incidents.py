"""Adding equipment statuses and incidents

Revision ID: 64b61b54d123
Revises: f921aa0af420
Create Date: 2024-10-22 15:58:19.143659

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.database.alembic.enum as c_enum


# revision identifiers, used by Alembic.
revision: str = "64b61b54d123"
down_revision: Union[str, None] = "f921aa0af420"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "equipment_statuses",
        sa.Column("equipment_name", sa.String(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("ip_address", sa.String(), nullable=False),
        sa.Column("latency", sa.Float(), nullable=False),
        sa.Column("last_update", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "equipment_incidents",
        sa.Column("equipment_status_id", sa.Integer(), nullable=False),
        sa.Column("incident_time", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "stage",
            sa.Enum("created", "processed", "solved", name="incidentstage"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["equipment_status_id"],
            ["equipment_statuses.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("departments", sa.Column("asterisk_id", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("departments", "asterisk_id")
    op.drop_table("equipment_incidents")
    op.drop_table("equipment_statuses")
    c_enum.delete_enum("incidentstage")
