from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey
from uuid import UUID

from common.sql.orm import Base


class TTKDish(Base):
    __tablename__ = "dishes"

    iiko_uuid: Mapped[UUID] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    code: Mapped[str] = mapped_column(nullable=False)
    num: Mapped[str] = mapped_column(nullable=False)
    deleted: Mapped[bool] = mapped_column(nullable=False)
    weight: Mapped[float] = mapped_column(nullable=False)
    capacity: Mapped[float] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)


class TTKDishModifier(Base):
    __tablename__ = "modifiers"

    iiko_uuid: Mapped[UUID] = mapped_column(nullable=False)
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id"), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    code: Mapped[str] = mapped_column(nullable=False)
    num: Mapped[str] = mapped_column(nullable=False)
    deleted: Mapped[bool] = mapped_column(nullable=False)
    weight: Mapped[float] = mapped_column(nullable=False)
    capacity: Mapped[float] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    defaultAmount: Mapped[float] = mapped_column(nullable=False)
    minimumAmount: Mapped[float] = mapped_column(nullable=False)
    maximumAmount: Mapped[float] = mapped_column(nullable=False)

    dish: Mapped["TTKDish"] = relationship("TTKDish", foreign_keys=[dish_id])


class TTKProduct(Base):
    __tablename__ = "products"

    iiko_uuid: Mapped[UUID] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    code: Mapped[str] = mapped_column(nullable=False)
    num: Mapped[str] = mapped_column(nullable=False)
    deleted: Mapped[bool] = mapped_column(nullable=False)


class AssemblyChart(Base):
    __tablename__ = "assembly_charts"

    iiko_uuid: Mapped[UUID] = mapped_column(nullable=False)
    modifier_id: Mapped[int] = mapped_column(ForeignKey("modifiers.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    weight: Mapped[float] = mapped_column(nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)

    modifier: Mapped["TTKDishModifier"] = relationship(
        "TTKDishModifier", foreign_keys=[modifier_id]
    )
    product: Mapped["TTKProduct"] = relationship(
        "TTKProduct", foreign_keys=[product_id]
    )
