"""Add scope for update restaurant menu

Revision ID: aaf81d52603c
Revises: 1fb43aa474af
Create Date: 2025-02-17 13:13:39.007776

"""

from typing import Sequence, Union
from app.infra.database.alembic.enum import update_enum


# revision identifiers, used by Alembic.
revision: str = "aaf81d52603c"
down_revision: Union[str, None] = "1fb43aa474af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
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
    "bot_technical_request_extensive_director",
    "bot_bid_it_worker",
    "bot_bid_it_repairman",
    "bot_bid_it_tm",
    "bot_personal_cabinet",
    "bot_incident_monitoring",
    "bot_bid_fac_cc",
    "bot_subordinates_menu",
    "bot_worker_bid_security_coordinate",
    "bot_worker_bid_accounting_coordinate",
    "bot_worker_bid_iiko",
    "bot_technical_request_department_director",
)
new_options = sorted(old_options + ("bot_change_restaurant_menu",))

table_columns = {"post_scopes": ["scope"]}


def upgrade() -> None:
    update_enum(old_options, new_options, "fujiscope", table_columns)


def downgrade() -> None:
    update_enum(new_options, old_options, "fujiscope", table_columns)
