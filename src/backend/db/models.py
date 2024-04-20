from db.database import Base
from sqlalchemy import ForeignKey, CheckConstraint, BigInteger, Enum
from fastapi_storages.integrations.sqlalchemy import FileType
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Annotated, List
import datetime
from settings import get_settings
import enum

intpk = Annotated[int, mapped_column(primary_key=True)]

class ApprovalStatus(enum.Enum):
    pending = 1,
    approved = 2,
    denied = 3,
    pending_approval = 4,
    skipped = 5,

approvalstate = Annotated[ApprovalStatus, mapped_column(Enum(ApprovalStatus), default=ApprovalStatus.pending)]


class Post(Base):
    __tablename__ = "posts"

    def __str__(self) -> str:
        return self.name

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)
    level: Mapped[int] = mapped_column(CheckConstraint("level<=10 AND level>0"), nullable=False)

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
    address: Mapped[str] = mapped_column(nullable=True)

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    company: Mapped["Company"] = relationship("Company", back_populates="departments")

    workers: Mapped[List["Worker"]] = relationship("Worker", back_populates="department")
    bids: Mapped[List["Bid"]] = relationship("Bid", back_populates="department")

class Worker(Base):
    __tablename__ = "workers"

    def __str__(self) -> str:
        return f"{self.l_name} {self.f_name} {self.o_name}"

    id: Mapped[intpk]
    f_name: Mapped[str] = mapped_column(nullable=False)
    l_name: Mapped[str] = mapped_column(nullable=False)
    o_name: Mapped[str] = mapped_column(nullable=False)
    b_date: Mapped[datetime.date] = mapped_column(nullable=True)
    phone_number: Mapped[str] = mapped_column(nullable=False)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=True)

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    post: Mapped["Post"] = relationship("Post", back_populates="workers")

    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    department: Mapped["Department"] = relationship("Department", back_populates="workers")

    bids: Mapped[List["Bid"]] = relationship("Bid", back_populates="worker")

class Bid(Base):
    __tablename__ = "bids"

    def __str__(self) -> str:
        return f"Заявка от {self.create_date}"

    id: Mapped[intpk]
    amount: Mapped[int] = mapped_column(nullable=False)
    payment_type: Mapped[str] = mapped_column(nullable=False)
    purpose: Mapped[str] = mapped_column(nullable=False)
    agreement: Mapped[str] = mapped_column(nullable=True, default="Нет")
    urgently: Mapped[str] = mapped_column(nullable=True, default="Нет")
    need_document: Mapped[str] = mapped_column(nullable=True, default="Нет")
    comment: Mapped[str] = mapped_column(nullable=True, default="")
    create_date: Mapped[datetime.datetime] = mapped_column(nullable=False)

    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    department: Mapped["Department"] = relationship("Department", back_populates="bids")

    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id"))
    worker: Mapped["Worker"] = relationship("Worker", back_populates="bids")

    document: Mapped[FileType] = mapped_column(FileType(storage=get_settings().storage))

    # States
    kru_state: Mapped[approvalstate]
    owner_state: Mapped[approvalstate]
    accountant_cash: Mapped[approvalstate]
    accountant_card: Mapped[approvalstate]
    teller_cash: Mapped[approvalstate]
    teller_card: Mapped[approvalstate]

