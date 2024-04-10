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

    posts: Mapped[List["Post"]] = relationship("Post", cascade="all,delete", back_populates="role")

    def __str__(self) -> str:
        return f"{self.name}, level: {self.level}"

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    role: Mapped["Role"] = relationship("Role", back_populates="posts")

    employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="post")

    def __str__(self) -> str:
        return self.name

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)

    enterprises: Mapped[List["Enterprise"]] = relationship("Enterprise", cascade="all,delete", back_populates="company")

    def __str__(self) -> str:
        return self.name

class Enterprise(Base):
    __tablename__ = "enterprises"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str]

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    company: Mapped["Company"] = relationship("Company", back_populates="enterprises")

    employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="enterprise")

    def __str__(self) -> str:
        return self.name

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    patronymic: Mapped[str] = mapped_column(nullable=False)
    phone_number: Mapped[str] = mapped_column(nullable=False)

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    post: Mapped["Post"] = relationship("Post", back_populates="employees")

    enterprise_id: Mapped[int] = mapped_column(ForeignKey("enterprises.id"))
    enterprise: Mapped["Enterprise"] = relationship("Enterprise", back_populates="employees")