"""rename scope bot_technical_request_department_director

Revision ID: f6ce218627c2
Revises: 28b8ee36521a
Create Date: 2025-02-05 15:40:40.321929

"""

from typing import Sequence, Union
from app.infra.database.alembic.enum import rename_enum

# revision identifiers, used by Alembic.
revision: str = "f6ce218627c2"
down_revision: Union[str, None] = "28b8ee36521a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    rename_enum(
        "bot_technical_request_department_director",
        "bot_technical_request_extensive_director",
        "fujiscope",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    rename_enum(
        "bot_technical_request_extensive_director",
        "bot_technical_request_department_director",
        "fujiscope",
    )
