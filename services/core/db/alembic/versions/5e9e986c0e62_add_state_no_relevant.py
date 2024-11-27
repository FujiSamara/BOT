"""Add state no_relevant

Revision ID: 5e9e986c0e62
Revises: b194833559b0
Create Date: 2024-08-22 16:03:25.004534

"""

from typing import Sequence, Union
from db.alembic.enum import update_enum

name = "approvalstatus"
table_columns = {
    "bids": [
        "cc_supervisor_state",
        "cc_state",
        "fac_state",
        "teller_card_state",
        "teller_cash_state",
        "accountant_card_state",
        "accountant_cash_state",
        "owner_state",
        "kru_state",
    ],
    "technical_requests": ["state"],
    "worker_bids": ["state"],
}

old_options = (
    "pending",
    "approved",
    "denied",
    "pending_approval",
    "skipped",
)
new_options = sorted(old_options + ("not_relevant",))

# revision identifiers, used by Alembic.
revision: str = "5e9e986c0e62"
down_revision: Union[str, None] = "b194833559b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    update_enum(
        old=old_options,
        new=new_options,
        name=name,
        table_columns=table_columns,
    )


def downgrade() -> None:
    update_enum(
        old=new_options,
        new=old_options,
        name=name,
        table_columns=table_columns,
    )
