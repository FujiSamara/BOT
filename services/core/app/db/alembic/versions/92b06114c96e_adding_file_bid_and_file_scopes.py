"""Adding file bid and file scopes

Revision ID: 92b06114c96e
Revises: 4749aedb1134
Create Date: 2024-10-05 11:46:31.757692

"""

from typing import Sequence, Union

import db.alembic.enum as c_enum


# revision identifiers, used by Alembic.
revision: str = "92b06114c96e"
down_revision: Union[str, None] = "4749aedb1134"
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
)

new_options = sorted(old_options + ("crm_my_bid", "crm_archive_bid", "crm_my_file"))
table_columns = {"post_scopes": ["scope"]}


def upgrade() -> None:
    c_enum.update_enum(old_options, new_options, "fujiscope", table_columns)


def downgrade() -> None:
    c_enum.update_enum(new_options, old_options, "fujiscope", table_columns)
