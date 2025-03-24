from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey

from common.sql.orm import Base


class Division(Base):
    __tablename__ = "divisions"

    name: Mapped[str] = mapped_column(nullable=False)
    path: Mapped[str] = mapped_column(nullable=False, unique=True)

    def __str__(self):
        return self.name


class DishDivision(Base):
    __tablename__ = "dish_divisions"

    dish_id: Mapped[int] = mapped_column(nullable=False)
    division_id: Mapped[int] = mapped_column(ForeignKey("divisions.id"), nullable=False)


class BusinessCard(Base):
    __tablename__ = "business_cards"

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)

    division_id: Mapped[int] = mapped_column(ForeignKey("divisions.id"), nullable=False)

    division: Mapped[Division] = relationship(Division, foreign_keys=[division_id])
    materials: Mapped[list["BusinessCardMaterial"]] = relationship(
        "BusinessCardMaterial"
    )


class BusinessCardMaterial(Base):
    __tablename__ = "business_card_materials"

    external_id: Mapped[int] = mapped_column(nullable=False)
    card_id: Mapped[int] = mapped_column(
        ForeignKey("business_cards.id"), nullable=False
    )
