"""cleaning request tables

Revision ID: 23c0a06c41c6
Revises: 5ce7a56ae4a7
Create Date: 2025-01-07 12:50:20.411469

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM
from app.infra.config import settings
import fastapi_storages

import app.infra.database.alembic.enum as c_enum

old_options = (
    "admin",
    "crm_bid",
    "crm_budget",
    "crm_expenditure",
    "crm_fac_cc_bid",
    "crm_paralegal_bid",
    "crm_my_bid",
    "crm_archive_bid",
    "crm_my_file",
    "crm_bid_readonly",
    "crm_worktime",
    "crm_accountant_card_bid",
    "bot_bid_create",
    "bot_bid_kru",
    "bot_bid_owner",
    "bot_bid_teller_cash",
    "bot_bid_teller_card",
    "bot_bid_accountant_cash",
    "bot_bid_accountant_card",
    "bot_rate",
    "bot_worker_bid",
    "bot_technical_request_worker",
    "bot_technical_request_repairman",
    "bot_technical_request_chief_technician",
    "bot_technical_request_appraiser",
    "bot_technical_request_department_director",
    "bot_technical_request_extensive_director",
    "bot_bid_it_worker",
    "bot_bid_it_repairman",
    "bot_bid_it_tm",
    "bot_personal_cabinet",
    "bot_incident_monitoring",
    "bot_bid_fac_cc",
    "bot_coordinate_worker_bid",
    "bot_worker_bid_security_coordinate",
    "bot_worker_bid_accounting_coordinate",
    "bot_worker_bid_iiko",
)
new_options = sorted(
    old_options
    + (
        "bot_cleaning_request_cleaner",
        "bot_cleaning_request_appraiser",
    )
)
table_columns = {"post_scopes": ["scope"]}

# revision identifiers, used by Alembic.
revision: str = "23c0a06c41c6"
down_revision: Union[str, None] = "5ce7a56ae4a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    c_enum.update_enum(old_options, new_options, "fujiscope", table_columns)

    op.create_table(
        "cleaning_problems",
        sa.Column("problem_name", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("problem_name"),
    )
    op.create_table(
        "cleaning_requests",
        sa.Column("problem_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column(
            "state",
            ENUM(
                "pending",
                "approved",
                "denied",
                "pending_approval",
                "skipped",
                "not_relevant",
                name="approvalstatus",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("cleaner_id", sa.Integer(), nullable=False),
        sa.Column("worker_id", sa.Integer(), nullable=False),
        sa.Column("appraiser_id", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("open_date", sa.DateTime(), nullable=False),
        sa.Column("cleaning_date", sa.DateTime(), nullable=True),
        sa.Column("confirmation_date", sa.DateTime(), nullable=True),
        sa.Column("confirmation_description", sa.String(), nullable=True),
        sa.Column("reopen_date", sa.DateTime(), nullable=True),
        sa.Column("reopen_cleaning_date", sa.DateTime(), nullable=True),
        sa.Column("reopen_confirmation_date", sa.DateTime(), nullable=True),
        sa.Column("close_date", sa.DateTime(), nullable=True),
        sa.Column("close_description", sa.String(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cleaner_id"],
            ["workers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
        ),
        sa.ForeignKeyConstraint(
            ["problem_id"],
            ["cleaning_problems.id"],
        ),
        sa.ForeignKeyConstraint(
            ["appraiser_id"],
            ["workers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["worker_id"],
            ["workers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cleaning_requests_photos_work",
        sa.Column(
            "document",
            fastapi_storages.integrations.sqlalchemy.FileType(storage=settings.storage),
            nullable=False,
        ),
        sa.Column("cleaning_request_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cleaning_request_id"],
            ["cleaning_requests.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cleaning_requests_problem_photos",
        sa.Column(
            "document",
            fastapi_storages.integrations.sqlalchemy.FileType(storage=settings.storage),
            nullable=False,
        ),
        sa.Column("cleaning_request_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cleaning_request_id"],
            ["cleaning_requests.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("departments", sa.Column("cleaner_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "departments_cleaner_id_fkey", "departments", "workers", ["cleaner_id"], ["id"]
    )


def downgrade() -> None:
    c_enum.update_enum(new_options, old_options, "fujiscope", table_columns)

    op.drop_constraint("departments_cleaner_id_fkey", "departments", type_="foreignkey")
    op.drop_column("departments", "cleaner_id")
    op.drop_table("cleaning_requests_problem_photos")
    op.drop_table("cleaning_requests_photos_work")
    op.drop_table("cleaning_requests")
    op.drop_table("cleaning_problems")
