"""rename and add new scopes and field in worker bid

Revision ID: 65267cafab6a
Revises: 1a089c1691f5
Create Date: 2024-12-23 17:36:44.202990

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.infra.database.alembic.enum as c_enum


# revision identifiers, used by Alembic.
revision: str = "65267cafab6a"
down_revision: Union[str, None] = "1a089c1691f5"
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
    c_enum.update_enum(old_options, new_options, "fujiscope", table_columns)
    op.add_column(
        "worker_bids",
        sa.Column(
            "security_service_state",
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


def downgrade() -> None:
    c_enum.update_enum(new_options, old_options, "fujiscope", table_columns)

    op.drop_column("worker_bids", "security_service_comment")
    op.drop_column("worker_bids", "accounting_service_state")
    op.drop_column("worker_bids", "security_service_state")
