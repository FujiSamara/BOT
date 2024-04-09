from db.database import Base
from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Annotated, List

intpk = Annotated[int, mapped_column(primary_key=True)]

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)
    level: Mapped[int] = mapped_column(CheckConstraint("level<=10 AND level>0"), nullable=False)

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)

    enterprises: Mapped[List["Enterprise"]] = relationship("Enterprise", back_populates="company")

    def __str__(self) -> str:
        return self.name

class Enterprise(Base):
    __tablename__ = "enterprises"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str]

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    company: Mapped["Company"] = relationship("Company", back_populates="enterprises")

    def __str__(self) -> str:
        return self.name

# class Post(Base):
#     __tablename__ = "posts"

#     id: Mapped[intpk]
#     name: Mapped[str] = mapped_column(nullable=False)


