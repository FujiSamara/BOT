"""Swapping kru with cc_supervisor, renaming supervisor

Revision ID: 4a228ca5d1cd
Revises: 5da535571678
Create Date: 2024-10-15 15:05:23.615448

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

import app.db.alembic.enum as c_enum

# revision identifiers, used by Alembic.
revision: str = "4a228ca5d1cd"
down_revision: Union[str, None] = "5da535571678"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


old_options = (
    "admin",
    "crm_bid",
    "crm_budget",
    "crm_expenditure",
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
    "crm_fac_bid",
    "crm_cc_bid",
    "crm_cc_supervisor_bid",
    "bot_bid_it_worker",
    "bot_bid_it_repairman",
    "bot_bid_it_tm",
    "bot_personal_cabinet",
    "crm_my_bid",
    "crm_archive_bid",
    "crm_my_file",
)

new_options = sorted(
    (
        "admin",
        "crm_bid",
        "crm_budget",
        "crm_expenditure",
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
        "crm_fac_bid",
        "crm_cc_bid",
        "crm_paralegal_bid",
        "bot_bid_it_worker",
        "bot_bid_it_repairman",
        "bot_bid_it_tm",
        "bot_personal_cabinet",
        "crm_my_bid",
        "crm_archive_bid",
        "crm_my_file",
    )
)
table_columns = {"post_scopes": ["scope"]}


def upgrade() -> None:
    op.add_column(
        "bids",
        sa.Column(
            "paralegal_state",
            sa.Enum(
                "pending",
                "approved",
                "denied",
                "pending_approval",
                "skipped",
                "not_relevant",
                name="approvalstatus",
            ),
            nullable=False,
        ),
    )
    op.drop_column("bids", "cc_supervisor_state")
    op.add_column(
        "expenditures", sa.Column("paralegal_id", sa.Integer(), nullable=False)
    )
    op.drop_constraint(
        "expenditures_cc_supervisor_id_fkey", "expenditures", type_="foreignkey"
    )
    op.create_foreign_key(None, "expenditures", "workers", ["paralegal_id"], ["id"])
    op.drop_column("expenditures", "cc_supervisor_id")
    c_enum.update_enum(old_options, new_options, "fujiscope", table_columns)


def downgrade() -> None:
    op.add_column(
        "expenditures",
        sa.Column(
            "cc_supervisor_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
    )
    op.create_foreign_key(
        "expenditures_cc_supervisor_id_fkey",
        "expenditures",
        "workers",
        ["cc_supervisor_id"],
        ["id"],
    )
    op.drop_column("expenditures", "paralegal_id")
    op.add_column(
        "bids",
        sa.Column(
            "cc_supervisor_state",
            postgresql.ENUM(
                "approved",
                "denied",
                "not_relevant",
                "pending",
                "pending_approval",
                "skipped",
                name="approvalstatus",
            ),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_column("bids", "paralegal_state")
    c_enum.update_enum(new_options, old_options, "fujiscope", table_columns)
