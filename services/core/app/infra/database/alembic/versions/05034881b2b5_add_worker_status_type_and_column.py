"""add worker status type and column

Revision ID: 05034881b2b5
Revises: 532c9a04a904
Create Date: 2024-12-19 20:58:31.918559

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "05034881b2b5"
down_revision: Union[str, None] = "532c9a04a904"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TYPE workerstatus AS ENUM (
            'pending_approval',
            'internship',
            'refusal_internship',
            'active',
            'process_dismissal',
            'dismissal'
        );
    """)
    op.add_column(
        "workers",
        sa.Column(
            "state",
            sa.Enum(
                "pending_approval",
                "internship",
                "refusal_internship",
                "active",
                "process_dismissal",
                "dismissal",
                name="workerstatus",
                create_type=False,
            ),
            nullable=True,
        ),
    )
    op.execute("UPDATE workers set state = 'active'")


def downgrade() -> None:
    op.drop_column("workers", "state")
    op.execute("DROP TYPE workerstatus")
