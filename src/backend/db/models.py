from db.database import Base
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from typing import Annotated

intpk = Annotated[int, mapped_column(primary_key=True)]

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)

class Enterprise(Base):
    __tablename__ = "enterprises"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)
    address = Mapped[str]

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"))
    

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)


