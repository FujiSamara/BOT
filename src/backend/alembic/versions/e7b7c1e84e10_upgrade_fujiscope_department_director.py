"""Upgrade fujiscope department director

Revision ID: e7b7c1e84e10
Revises: ce432ef44a5c
Create Date: 2024-08-15 12:16:44.870450

"""

from typing import Sequence, Union

import alembic_custom.enum as c_enum


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
)


new_options = sorted(old_options + ("bot_technical_request_department_director",))

# revision identifiers, used by Alembic.
revision: str = "e7b7c1e84e10"
down_revision: Union[str, None] = "ce432ef44a5c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    c_enum.update_enum(
        old_options, new_options, "fujiscope", ["post_scopes"], ["scope"]
    )


def downgrade() -> None:
    c_enum.update_enum(
        new_options, old_options, "fujiscope", ["post_scopes"], ["scope"]
    )
