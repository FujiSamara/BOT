from uuid import UUID

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
    pending = (1,)
    approved = (2,)
    denied = (3,)
    pending_approval = (4,)
    skipped = (5,)


class Access(enum.Enum):
    kru = (6,)
    worker = (3,)
    teller_cash = (4,)
    teller_card = (5,)
    accountant_cash = (7,)
    accountant_card = (8,)
    owner = (10,)


approvalstatus = Annotated[
    ApprovalStatus, mapped_column(Enum(ApprovalStatus), default=ApprovalStatus.pending)
]


class Post(Base):
    """Должности у работников"""

    __tablename__ = "posts"

    def __str__(self) -> str:
        return self.name

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)
    salary: Mapped[float] = mapped_column(nullable=True)
    level: Mapped[int] = mapped_column(
        CheckConstraint("level<=10 AND level>0"), nullable=False
    )

    workers: Mapped[List["Worker"]] = relationship("Worker", back_populates="post")

    workers_bids: Mapped[List["Worker"]] = relationship(
        "WorkerBid", back_populates="post"
    )

    work_times: Mapped[List["WorkTime"]] = relationship(
        "WorkTime", back_populates="post"
    )


class Company(Base):
    """Компания Фуджи или Сакура"""

    __tablename__ = "companies"

    def __str__(self) -> str:
        return self.name

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)

    departments: Mapped[List["Department"]] = relationship(
        "Department", cascade="all,delete", back_populates="company"
    )

    workers: Mapped[List["Worker"]] = relationship(
        "Worker", cascade="all,delete", back_populates="company"
    )

    work_times: Mapped[List["WorkTime"]] = relationship(
        "WorkTime", back_populates="company"
    )

    # айдишник из биосмарта для определения компании
    # При заведении через админку может быть пустым до первой выгрузки табеля, после не должен быть пустым
    biosmart_strid: Mapped[str] = mapped_column(nullable=True)
    # Флаг выгрузки из биосмарта. При нормальной работе всегда должен быть false. Если true - чтото пошло не так
    bs_import: Mapped[bool] = mapped_column(nullable=True)
    # Флаг расхождения данных в биосмарте и админке. При нормальной работе всегда должен быть false. Если true - чтото пошло не так
    # Показывать в админке, чтобы админы видели ошибку, пока не сделаем уведомления
    bs_import_error: Mapped[bool] = mapped_column(nullable=True)


class Department(Base):
    """Подразделения (рестораны)"""

    __tablename__ = "departments"

    def __str__(self) -> str:
        return self.name

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=True)

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    company: Mapped["Company"] = relationship("Company", back_populates="departments")

    workers: Mapped[List["Worker"]] = relationship(
        "Worker", back_populates="department"
    )
    bids: Mapped[List["Bid"]] = relationship("Bid", back_populates="department")
    workers_bids: Mapped[List["WorkerBid"]] = relationship(
        "WorkerBid", back_populates="department"
    )

    work_times: Mapped[List["WorkTime"]] = relationship(
        "WorkTime", back_populates="department"
    )

    # айдишник из биосмарта для определения конкретного подразделения
    # При заведении через админку может быть пустым до первой выгрузки табеля, после не должен быть пустым
    biosmart_strid: Mapped[str] = mapped_column(nullable=True)
    # Флаг выгрузки из биосмарта. При нормальной работе всегда должен быть false. Если true - чтото пошло не так
    bs_import: Mapped[bool] = mapped_column(nullable=True)
    # Флаг расхождения данных в биосмарте и админке. При нормальной работе всегда должен быть false. Если true - чтото пошло не так
    # Показывать в админке, чтобы админы видели ошибку, пока не сделаем уведомления
    bs_import_error: Mapped[bool] = mapped_column(nullable=True)
    # Если прошлый флаг true, здесь будет описание ошибки
    bs_import_error_text: Mapped[str] = mapped_column(nullable=True)

    # Данные из iiko для связи с таблицей orders
    uuid: Mapped[UUID] = mapped_column(nullable=True)
    inn: Mapped[str] = mapped_column(nullable=True)
    code: Mapped[str] = mapped_column(nullable=True)


class Worker(Base):
    __tablename__ = "workers"

    def __str__(self) -> str:
        return f"{self.l_name} {self.f_name} {self.o_name}"

    id: Mapped[intpk]
    f_name: Mapped[str] = mapped_column(nullable=False)
    l_name: Mapped[str] = mapped_column(nullable=False)
    o_name: Mapped[str] = mapped_column(nullable=False)
    b_date: Mapped[datetime.date] = mapped_column(nullable=True)
    phone_number: Mapped[str] = mapped_column(nullable=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=True)

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    post: Mapped["Post"] = relationship("Post", back_populates="workers")

    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    department: Mapped["Department"] = relationship(
        "Department", back_populates="workers"
    )

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=True)
    company: Mapped["Company"] = relationship("Company", back_populates="workers")

    bids: Mapped[List["Bid"]] = relationship("Bid", back_populates="worker")
    worker_bids: Mapped[List["WorkerBid"]] = relationship(
        "WorkerBid", back_populates="sender"
    )

    work_times: Mapped[List["WorkTime"]] = relationship(
        "WorkTime", back_populates="worker"
    )

    # айдишник из биосмарта для определения конкретного рабочего
    # При заведении через админку может быть пустым до первой выгрузки табеля, после не должен быть пустым
    biosmart_strid: Mapped[str] = mapped_column(nullable=True)
    # Флаг выгрузки из биосмарта. При нормальной работе всегда должен быть false. Если true - чтото пошло не так
    bs_import: Mapped[bool] = mapped_column(nullable=True)
    # Флаг расхождения данных в биосмарте и админке. При нормальной работе всегда должен быть false. Если true - чтото пошло не так
    # Показывать в админке, чтобы админы видели ошибку, пока не сделаем уведомления
    bs_import_error: Mapped[bool] = mapped_column(nullable=True)
    # Если прошлый флаг true, здесь будет описание ошибки
    bs_import_error_text: Mapped[str] = mapped_column(nullable=True)


class Bid(Base):
    """Заявки"""

    __tablename__ = "bids"

    def __str__(self) -> str:
        return f"Заявка от {self.create_date.strftime('%H:%M %d.%m.%y')}"

    id: Mapped[intpk]
    amount: Mapped[int] = mapped_column(nullable=False)
    payment_type: Mapped[str] = mapped_column(nullable=False)
    purpose: Mapped[str] = mapped_column(nullable=False)
    agreement: Mapped[str] = mapped_column(nullable=True, default="Нет")
    urgently: Mapped[str] = mapped_column(nullable=True, default="Нет")
    need_document: Mapped[str] = mapped_column(nullable=True, default="Нет")
    comment: Mapped[str] = mapped_column(nullable=True, default="")
    denying_reason: Mapped[str] = mapped_column(nullable=True, default="")
    create_date: Mapped[datetime.datetime] = mapped_column(nullable=False)
    close_date: Mapped[datetime.datetime] = mapped_column(nullable=True)

    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    department: Mapped["Department"] = relationship("Department", back_populates="bids")

    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id"))
    worker: Mapped["Worker"] = relationship("Worker", back_populates="bids")

    document: Mapped[FileType] = mapped_column(FileType(storage=get_settings().storage))
    document1: Mapped[FileType] = mapped_column(
        FileType(storage=get_settings().storage), nullable=True
    )
    document2: Mapped[FileType] = mapped_column(
        FileType(storage=get_settings().storage), nullable=True
    )

    # States
    kru_state: Mapped[approvalstatus]
    owner_state: Mapped[approvalstatus]
    accountant_cash_state: Mapped[approvalstatus]
    accountant_card_state: Mapped[approvalstatus]
    teller_cash_state: Mapped[approvalstatus]
    teller_card_state: Mapped[approvalstatus]


class WorkerBid(Base):
    """Заявки на найм"""

    __tablename__ = "worker_bids"

    id: Mapped[intpk]

    f_name: Mapped[str] = mapped_column(nullable=False)
    l_name: Mapped[str] = mapped_column(nullable=False)
    o_name: Mapped[str] = mapped_column(nullable=False)
    create_date: Mapped[datetime.datetime] = mapped_column(nullable=False)

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    post: Mapped["Post"] = relationship("Post", back_populates="workers_bids")

    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), nullable=False
    )
    department: Mapped["Department"] = relationship(
        "Department", back_populates="workers_bids"
    )

    worksheet: Mapped[List["WorkerBidWorksheet"]] = relationship(
        "WorkerBidWorksheet", cascade="all,delete", back_populates="worker_bid"
    )

    passport: Mapped[List["WorkerBidPassport"]] = relationship(
        "WorkerBidPassport", cascade="all,delete", back_populates="worker_bid"
    )

    work_permission: Mapped[List["WorkerBidWorkPermission"]] = relationship(
        "WorkerBidWorkPermission", cascade="all,delete", back_populates="worker_bid"
    )

    state: Mapped[approvalstatus]

    sender_id: Mapped[int] = mapped_column(ForeignKey("workers.id"), nullable=False)
    sender: Mapped["Worker"] = relationship("Worker", back_populates="worker_bids")


class WorkerBidDocument(Base):
    """Общий класс для документов анкеты на найм"""

    __abstract__ = True

    id: Mapped[intpk]
    document: Mapped[FileType] = mapped_column(FileType(storage=get_settings().storage))
    worker_bid_id: Mapped[int] = mapped_column(ForeignKey("worker_bids.id"))


class WorkerBidWorksheet(WorkerBidDocument):
    """Анкеты найма"""

    __tablename__ = "worker_bids_worksheets"

    worker_bid: Mapped["WorkerBid"] = relationship(
        "WorkerBid", back_populates="worksheet"
    )


class WorkerBidPassport(WorkerBidDocument):
    """Паспортные данные заявок на найм"""

    __tablename__ = "worker_bids_passports"

    worker_bid: Mapped["WorkerBid"] = relationship(
        "WorkerBid", back_populates="passport"
    )


class WorkerBidWorkPermission(WorkerBidDocument):
    """Разрешения на работу в заявках на найм"""

    __tablename__ = "worker_work_permissions"

    worker_bid: Mapped["WorkerBid"] = relationship(
        "WorkerBid", back_populates="work_permission"
    )


class WorkTime(Base):
    """Табель работы"""

    __tablename__ = "work_times"

    id: Mapped[intpk]

    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id"))
    worker: Mapped["Worker"] = relationship("Worker", back_populates="work_times")
    salary: Mapped[int] = mapped_column(nullable=True)

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=True)
    company: Mapped["Company"] = relationship("Company", back_populates="work_times")

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    post: Mapped["Post"] = relationship("Post", back_populates="work_times")

    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    department: Mapped["Department"] = relationship(
        "Department", back_populates="work_times"
    )

    work_begin: Mapped[str] = mapped_column(nullable=True)
    work_end: Mapped[str] = mapped_column(nullable=True)
    work_duration: Mapped[float] = mapped_column(nullable=True)
    day: Mapped[str] = mapped_column(nullable=True)

    rating: Mapped[int] = mapped_column(nullable=True)
    fine: Mapped[int] = mapped_column(nullable=True)
