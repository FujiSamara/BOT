"""Adding auth client with scopes

Revision ID: 61f97eb76077
Revises: d68cb5ee9b19
Create Date: 2025-03-15 08:25:04.772264

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "61f97eb76077"
down_revision: Union[str, None] = "d68cb5ee9b19"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "auth_clients",
        sa.Column("client_id", sa.String(), nullable=False),
        sa.Column("secret", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_auth_clients_client_id"), "auth_clients", ["client_id"], unique=False
    )
    op.create_table(
        "auth_client_scopes",
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["auth_clients.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("auth_client_scopes")
    op.drop_index(op.f("ix_auth_clients_client_id"), table_name="auth_clients")
    op.drop_table("auth_clients")
