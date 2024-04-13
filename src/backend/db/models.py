from db.database import Base
from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Annotated, List

intpk = Annotated[int, mapped_column(primary_key=True)]

class Role(Base):
    __tablename__ = "roles"

    def __str__(self) -> str:
        return f"{self.name}: {self.level}"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)
    level: Mapped[int] = mapped_column(CheckConstraint("level<=10 AND level>0"), nullable=False)

    posts: Mapped[List["Post"]] = relationship("Post", cascade="all,delete", back_populates="role")

class Post(Base):
    __tablename__ = "posts"

    def __str__(self) -> str:
        return self.name

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    role: Mapped["Role"] = relationship("Role", back_populates="posts")

    workers: Mapped[List["Worker"]] = relationship("Worker", back_populates="post")

class Company(Base):
    __tablename__ = "companies"

    def __str__(self) -> str:
        return self.name

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)

    departments: Mapped[List["Department"]] = relationship("Department", cascade="all,delete", back_populates="company")

class Department(Base):
    __tablename__ = "departments"

    def __str__(self) -> str:
        return self.name

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str]

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    company: Mapped["Company"] = relationship("Company", back_populates="departments")

    workers: Mapped[List["Worker"]] = relationship("Worker", back_populates="department")

class Worker(Base):
    __tablename__ = "workers"

    def __str__(self) -> str:
        return f"{self.worker_l_name} {self.worker_f_name} {self.worker_o_name}"

    worker_id: Mapped[intpk]
    worker_f_name: Mapped[str] = mapped_column(nullable=False)
    worker_l_name: Mapped[str] = mapped_column(nullable=False)
    worker_o_name: Mapped[str] = mapped_column(nullable=False)
    phone_number: Mapped[str] = mapped_column(nullable=False)
    telegram_id: Mapped[int]

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    post: Mapped["Post"] = relationship("Post", back_populates="workers")

    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    department: Mapped["Department"] = relationship("Department", back_populates="workers")