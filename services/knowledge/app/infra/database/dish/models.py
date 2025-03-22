from sqlalchemy.orm import mapped_column, Mapped, relationship
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
    dish_id: Mapped[int] = mapped_column(nullable=False)
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

    dish: Mapped["TTKDish"] = relationship(
        "TTKDish", back_populates="modifiers", foreign_keys=[dish_id]
    )


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
    modifier_id: Mapped[int] = mapped_column(nullable=False)
    product_id: Mapped[int] = mapped_column(nullable=False)
    weight: Mapped[float] = mapped_column(nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)

    modifier: Mapped["TTKDishModifier"] = relationship(
        "TTKDishModifier", back_populates="assembly_charts", foreign_keys=[modifier_id]
    )
    product: Mapped["TTKProduct"] = relationship(
        "TTKProduct", back_populates="assembly_charts", foreign_keys=[product_id]
    )
