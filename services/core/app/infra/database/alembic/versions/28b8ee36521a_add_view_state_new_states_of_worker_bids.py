"""Add view state. New states of worker bids

Revision ID: 28b8ee36521a
Revises: 242dff4d09c0
Create Date: 2025-02-03 16:35:34.850200

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM
from app.infra.database.alembic.enum import update_enum

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
    "bot_bid_it_worker",
    "bot_bid_it_repairman",
    "bot_bid_it_tm",
    "bot_personal_cabinet",
    "bot_incident_monitoring",
    "bot_bid_fac_cc",
    "bot_subordinates_menu",
    "bot_worker_bid_security_coordinate",
    "bot_worker_bid_accounting_coordinate",
)

new_options = sorted(old_options + ("bot_worker_bid_iiko",))
table_columns = {"post_scopes": ["scope"]}

# revision identifiers, used by Alembic.
revision: str = "28b8ee36521a"
down_revision: Union[str, None] = "242dff4d09c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    enum = ENUM(
        "viewed",
        "pending",
        "pending_approval",
        name="viewstatus",
    )
    enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "worker_bids",
        sa.Column(
            "view_state",
            enum,
            nullable=True,
        ),
    )
    op.add_column(
        "worker_bids",
        sa.Column(
            "iiko_service_state",
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
        sa.Column("accounting_service_comment", sa.String(), nullable=True),
    )
    op.add_column(
        "worker_bids", sa.Column("iiko_service_comment", sa.String(), nullable=True)
    )
    op.add_column(
        "worker_bids",
        sa.Column("close_date", sa.DateTime(), nullable=True),
    )
    update_enum(old_options, new_options, "fujiscope", table_columns)

    op.execute(
        "UPDATE worker_bids SET view_state = 'pending_approval' WHERE state = 'pending_approval'"
    )
    op.execute(
        "UPDATE worker_bids SET iiko_service_state = 'pending' WHERE state = 'pending_approval'"
    )


def downgrade() -> None:
    op.drop_column("worker_bids", "iiko_service_comment")
    op.drop_column("worker_bids", "accounting_service_comment")
    op.drop_column("worker_bids", "iiko_service_state")
    op.drop_column("worker_bids", "view_state")
    op.drop_column("worker_bids", "close_date")

    op.execute("DROP TYPE viewstatus")
    update_enum(new_options, old_options, "fujiscope", table_columns)
