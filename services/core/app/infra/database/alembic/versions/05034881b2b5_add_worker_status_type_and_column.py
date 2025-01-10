"""add in worker new columns
And new relationship tables

Revision ID: 05034881b2b5
Revises: 532c9a04a904
Create Date: 2024-12-19 20:58:31.918559

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM
import fastapi_storages
from app.infra.config import settings
import app.infra.database.alembic.enum as c_enum

# revision identifiers, used by Alembic.
revision: str = "05034881b2b5"
down_revision: Union[str, None] = "7373aeb0e65f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


old_options = (
    "admin",
    # CRM
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
    # BOT
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
    "bot_technical_request_territorial_manager",
    "bot_technical_request_department_director",
    "bot_bid_it_worker",
    "bot_bid_it_repairman",
    "bot_bid_it_tm",
    "bot_personal_cabinet",
    "bot_incident_monitoring",
    "bot_bid_fac_cc",
    "bot_subordinates_menu",
)

table_columns = {"post_scopes": ["scope"]}
new_options = sorted(
    old_options
    + (
        "bot_worker_bid_security_coordinate",
        "bot_worker_bid_accounting_coordinate",
    )
)


def upgrade() -> None:
    op.add_column("worker_bids", sa.Column("birth_date", sa.DateTime(), nullable=True))
    op.add_column(
        "worker_bids", sa.Column("phone_number", sa.String(length=12), nullable=True)
    )
    enum = ENUM(
        "pending_approval",
        "internship",
        "refusal_internship",
        "active",
        "process_dismissal",
        "dismissal",
        name="workerstatus",
    )
    enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "workers",
        sa.Column(
            "state",
            enum,
            nullable=True,
        ),
    )
    op.execute("UPDATE workers set state = 'active'")

    op.create_table(
        "worker_children",
        sa.Column("worker_id", sa.Integer(), nullable=False),
        sa.Column("born_date", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["worker_id"], ["workers.id"], name="worker_id"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "workers_passports",
        sa.Column("worker_id", sa.Integer(), nullable=False),
        sa.Column(
            "document",
            fastapi_storages.integrations.sqlalchemy.FileType(settings.storage),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["worker_id"], ["workers.id"], name="worker_id"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("workers", sa.Column("snils", sa.String(), nullable=True))
    op.add_column("workers", sa.Column("inn", sa.String(), nullable=True))
    op.add_column("workers", sa.Column("registration", sa.String(), nullable=True))
    op.add_column("workers", sa.Column("actual_residence", sa.String(), nullable=True))
    op.add_column("workers", sa.Column("children", sa.Boolean(), nullable=True))
    op.add_column("workers", sa.Column("military_ticket", sa.String(), nullable=True))
    op.execute("UPDATE workers SET children = false")

    c_enum.update_enum(old_options, new_options, "fujiscope", table_columns)
    op.add_column(
        "worker_bids",
        sa.Column(
            "security_service_state",
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
            nullable=True,
        ),
    )
    op.add_column(
        "worker_bids",
        sa.Column(
            "accounting_service_state",
            sa.Enum(
                "pending",
                "approved",
                "denied",
                "pending_approval",
                "skipped",
                "not_relevant",
                name="approvalstatus",
            ),
            nullable=True,
        ),
    )
    op.add_column(
        "worker_bids", sa.Column("security_service_comment", sa.String(), nullable=True)
    )

    op.add_column(
        "workers", sa.Column("official_employment_date", sa.Date(), nullable=True)
    )
    op.add_column(
        "workers", sa.Column("official_dismissal_date", sa.Date(), nullable=True)
    )
    op.add_column("workers", sa.Column("patent", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("worker_bids", "birth_date")

    op.drop_column("workers", "state")
    op.execute("DROP TYPE workerstatus")

    op.drop_column("workers", "military_ticket")
    op.drop_column("workers", "children")
    op.drop_column("workers", "actual_residence")
    op.drop_column("workers", "registration")
    op.drop_column("workers", "inn")
    op.drop_column("workers", "snils")
    op.drop_table("workers_passports")
    op.drop_table("worker_children")

    c_enum.update_enum(new_options, old_options, "fujiscope", table_columns)
    op.drop_column("worker_bids", "security_service_comment")
    op.drop_column("worker_bids", "accounting_service_state")
    op.drop_column("worker_bids", "security_service_state")

    op.drop_column("workers", "patent")
    op.drop_column("workers", "official_dismissal_date")
    op.drop_column("workers", "official_employment_date")
