from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey
from uuid import UUID

from common.sql.orm import Base


class TTKGroup(Base):
    __tablename__ = "ttk_groups"

    title: Mapped[str] = mapped_column(nullable=False)

    image: Mapped[str] = mapped_column(nullable=False)
    iiko_uuid: Mapped[UUID] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column(nullable=False)
    code: Mapped[str] = mapped_column(nullable=False)
    order: Mapped[int] = mapped_column(nullable=False)


# Extra table for compatibility
class TTKCategory(Base):
    __tablename__ = "ttk_categories"

    iiko_uuid: Mapped[UUID] = mapped_column(unique=True)
    title: Mapped[str] = mapped_column(nullable=False)


class TTKProduct(Base):
    __tablename__ = "ttk_products"

    title: Mapped[str] = mapped_column(nullable=False)
    image: Mapped[str] = mapped_column(nullable=False)

    iiko_uuid: Mapped[UUID] = mapped_column(unique=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("ttk_groups.id"), nullable=False)
    group_uuid: Mapped[UUID] = mapped_column(nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("ttk_categories.id"), nullable=False
    )
    category_uuid: Mapped[UUID] = mapped_column(nullable=False)
    order: Mapped[int] = mapped_column(nullable=False)
    code: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    fat: Mapped[float] = mapped_column(nullable=False)
    proteins: Mapped[float] = mapped_column(nullable=False)
    carbohydrates: Mapped[float] = mapped_column(nullable=False)
    energy: Mapped[float] = mapped_column(nullable=False)
    full_fat: Mapped[float] = mapped_column(nullable=False)
    full_proteins: Mapped[float] = mapped_column(nullable=False)
    full_carbohydrates: Mapped[float] = mapped_column(nullable=False)
    full_energy: Mapped[float] = mapped_column(nullable=False)
    weight: Mapped[float] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)


class TTKDishModifier(Base):
    __tablename__ = "ttk_modifiers"

    product_id: Mapped[int] = mapped_column(
        ForeignKey("ttk_products.id"), nullable=False
    )

    iiko_uuid: Mapped[UUID] = mapped_column(unique=True)
    product_uuid: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    code: Mapped[str] = mapped_column(nullable=False)
    num: Mapped[str] = mapped_column(nullable=False)
    deleted: Mapped[bool] = mapped_column(nullable=False)
    weight: Mapped[float] = mapped_column(nullable=False)
    capacity: Mapped[float] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    default_amount: Mapped[float] = mapped_column(nullable=False)
    minimum_amount: Mapped[float] = mapped_column(nullable=False)
    maximum_amount: Mapped[float] = mapped_column(nullable=False)


class TTKIngredient(Base):
    __tablename__ = "ttk_ingredients"

    title: Mapped[str] = mapped_column(nullable=False)

    iiko_uuid: Mapped[UUID] = mapped_column(unique=True)
    code: Mapped[str] = mapped_column(nullable=False)
    num: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)


class TTKAssemblyChart(Base):
    __tablename__ = "ttk_assembly_charts"

    modifier_id: Mapped[int] = mapped_column(
        ForeignKey("ttk_modifiers.id"), nullable=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("ttk_products.id"), nullable=False
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ttk_ingredients.id"), nullable=False
    )
    amount: Mapped[float] = mapped_column(nullable=False)

    iiko_uuid: Mapped[UUID] = mapped_column(unique=True)
    weight: Mapped[float] = mapped_column(nullable=False)
