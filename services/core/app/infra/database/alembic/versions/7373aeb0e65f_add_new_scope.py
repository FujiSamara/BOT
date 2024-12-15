"""Add new scope

Revision ID: 7373aeb0e65f
Revises: ee854959eb78
Create Date: 2024-12-15 14:35:54.808794

"""

from typing import Sequence, Union

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
    "bot_technical_request_territorial_manager",
    "bot_technical_request_department_director",
    "bot_bid_it_worker",
    "bot_bid_it_repairman",
    "bot_bid_it_tm",
    "bot_personal_cabinet",
    "bot_incident_monitoring",
    "bot_bid_fac_cc",
)

table_columns = {"post_scopes": ["scope"]}
new_options = sorted(old_options + ("bot_coordinate_worker_bid",))

table_columns = {"post_scopes": ["scope"]}

# revision identifiers, used by Alembic.
revision: str = "7373aeb0e65f"
down_revision: Union[str, None] = "ee854959eb78"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    c_enum.update_enum(old_options, new_options, "fujiscope", table_columns)


def downgrade() -> None:
    c_enum.update_enum(new_options, old_options, "fujiscope", table_columns)
