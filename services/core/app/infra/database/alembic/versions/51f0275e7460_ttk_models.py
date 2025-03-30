"""iiko tkk models

Revision ID: 51f0275e7460
Revises: 594fc6fe69b6
Create Date: 2025-03-28 11:02:53.493164

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID  # Используется для UUID


# revision identifiers, used by Alembic.
revision: str = "51f0275e7460"
down_revision: Union[str, None] = "594fc6fe69b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Создание таблицы ttk_groups
    op.create_table(
        "ttk_groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("iiko_uuid", UUID(), unique=True, nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("code", sa.String(), nullable=True),
        sa.Column("image", sa.String(), nullable=True),
        sa.Column("order", sa.Integer(), nullable=True),
    )

    # Создание таблицы ttk_categories
    op.create_table(
        "ttk_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("iiko_uuid", UUID(), unique=True, nullable=False),
        sa.Column("title", sa.String(), nullable=True),
    )

    # Создание таблицы ttk_products
    op.create_table(
        "ttk_products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("iiko_uuid", UUID(), unique=True, nullable=False),
        sa.Column(
            "group_id", sa.Integer(), sa.ForeignKey("ttk_groups.id"), nullable=True
        ),
        sa.Column("group_uuid", UUID(), nullable=True),
        sa.Column(
            "category_id",
            sa.Integer(),
            sa.ForeignKey("ttk_categories.id"),
            nullable=True,
        ),
        sa.Column("category_uuid", UUID(), nullable=True),
        sa.Column("image", sa.String(), nullable=True),
        sa.Column("order", sa.Integer(), nullable=True),
        sa.Column("code", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("fat", sa.Float(), nullable=True),
        sa.Column("proteins", sa.Float(), nullable=True),
        sa.Column("carbohydrates", sa.Float(), nullable=True),
        sa.Column("energy", sa.Float(), nullable=True),
        sa.Column("full_fat", sa.Float(), nullable=True),
        sa.Column("full_proteins", sa.Float(), nullable=True),
        sa.Column("full_carbohydrates", sa.Float(), nullable=True),
        sa.Column("full_energy", sa.Float(), nullable=True),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
    )

    # Создание таблицы ttk_modifiers
    op.create_table(
        "ttk_modifiers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("iiko_uuid", UUID(), unique=True, nullable=False),
        sa.Column(
            "product_id", sa.Integer(), sa.ForeignKey("ttk_products.id"), nullable=True
        ),
        sa.Column("product_uuid", UUID(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("code", sa.String(), nullable=True),
        sa.Column("num", sa.String(), nullable=True),
        sa.Column("deleted", sa.Boolean(), nullable=True),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("capacity", sa.Float(), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("default_amount", sa.Float(), nullable=True),
        sa.Column("minimum_amount", sa.Float(), nullable=True),
        sa.Column("maximum_amount", sa.Float(), nullable=True),
    )

    # Создание таблицы ttk_ingredients
    op.create_table(
        "ttk_ingredients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("iiko_uuid", UUID(), unique=True, nullable=False),
        sa.Column("code", sa.String(), nullable=True),
        sa.Column("num", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
    )

    # Создание таблицы ttk_assembly_charts
    op.create_table(
        "ttk_assembly_charts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("iiko_uuid", UUID(), unique=True, nullable=False),
        sa.Column(
            "modifier_id",
            sa.Integer(),
            sa.ForeignKey("ttk_modifiers.id"),
            nullable=True,
        ),
        sa.Column(
            "product_id", sa.Integer(), sa.ForeignKey("ttk_products.id"), nullable=False
        ),
        sa.Column(
            "ingredient_id",
            sa.Integer(),
            sa.ForeignKey("ttk_ingredients.id"),
            nullable=False,
        ),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("amount", sa.Float(), nullable=True),
    )


def downgrade():
    # Откат изменений: сначала удаляем таблицы, которые зависят от других
    op.drop_table("ttk_assembly_charts")
    op.drop_table("ttk_modifiers")
    op.drop_table("ttk_products")
    op.drop_table("ttk_categories")
    op.drop_table("ttk_groups")
