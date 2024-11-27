"""Adding monitoring scope

Revision ID: 5797fcce91fa
Revises: 64b61b54d123
Create Date: 2024-10-24 10:21:25.622194

"""

from typing import Sequence, Union

import app.db.alembic.enum as c_enum


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
    "crm_paralegal_bid",
    "bot_bid_it_worker",
    "bot_bid_it_repairman",
    "bot_bid_it_tm",
    "bot_personal_cabinet",
    "crm_my_bid",
    "crm_archive_bid",
    "crm_my_file",
)

new_options = sorted((*old_options, "bot_incident_monitoring"))
table_columns = {"post_scopes": ["scope"]}


# revision identifiers, used by Alembic.
revision: str = "5797fcce91fa"
down_revision: Union[str, None] = "64b61b54d123"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    c_enum.update_enum(old_options, new_options, "fujiscope", table_columns)


def downgrade() -> None:
    c_enum.update_enum(new_options, old_options, "fujiscope", table_columns)
