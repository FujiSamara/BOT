from uuid import UUID

from db.database import Base
from sqlalchemy import ForeignKey, CheckConstraint, BigInteger, Enum
from fastapi_storages.integrations.sqlalchemy import FileType
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Annotated, List, Optional
import datetime
from settings import get_settings
import enum


class ApprovalStatus(enum.Enum):
    pending = (1,)
    approved = (2,)
    denied = (3,)
    pending_approval = (4,)
    skipped = (5,)
    not_relevant = (6,)


class Gender(enum.Enum):
    man = (1,)
    woman = (2,)


class FujiScope(enum.Enum):
    admin = 1
    # CRM
    crm_bid = 2
    crm_budget = 3
    crm_expenditure = 4
    crm_fac_bid = 18
    crm_cc_bid = 19
    crm_cc_supervisor_bid = 20
    # BOT
    bot_bid_create = 5
    bot_bid_kru = 6
    bot_bid_owner = 7
    bot_bid_teller_cash = 8
    bot_bid_teller_card = 9
    bot_bid_accountant_cash = 10
    bot_bid_accountant_card = 11
    bot_rate = 12
    bot_worker_bid = 13
    bot_technical_request_worker = 14
    bot_technical_request_repairman = 15
    bot_technical_request_chief_technician = 16
    bot_technical_request_territorial_manager = 17
    bot_technical_request_department_director = 21
    bot_bid_it_worker = 22
    bot_bid_it_repairman = 23
    bot_bid_it_tm = 24
    bot_dismissal = 25


class DepartmentType(enum.Enum):
    dark_store = (1,)
    restaurant = (2,)
    fast_casual = (3,)


class Executor(enum.Enum):
    technician = (1,)
    chief_technician = (2,)
    electrician = (3,)


approvalstatus = Annotated[
    ApprovalStatus, mapped_column(Enum(ApprovalStatus), default=ApprovalStatus.pending)
]


class PostScope(Base):
    """Доступы у должности"""

    __tablename__ = "post_scopes"

    def __str__(self) -> str:
        return self.scope.name

    scope: Mapped[FujiScope] = mapped_column(Enum(FujiScope), nullable=False)

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    post: Mapped["Post"] = relationship("Post", back_populates="scopes")


class Post(Base):
    """Должности у работников"""

    __tablename__ = "posts"

    def __str__(self) -> str:
        return self.name

    name: Mapped[str] = mapped_column(nullable=False)
    salary: Mapped[float] = mapped_column(nullable=True)
    level: Mapped[int] = mapped_column(
        CheckConstraint("level<=10 AND level>0"), nullable=False
    )  # deprecated

    workers: Mapped[List["Worker"]] = relationship("Worker", back_populates="post")

    workers_bids: Mapped[List["Worker"]] = relationship(
        "WorkerBid", back_populates="post"
    )

    work_times: Mapped[List["WorkTime"]] = relationship(
        "WorkTime", back_populates="post"
    )

    scopes: Mapped[List["PostScope"]] = relationship("PostScope", back_populates="post")

    acceptor_technical_request: Mapped[List["TechnicalRequest"]] = relationship(
        "TechnicalRequest",
        back_populates="acceptor_post",
    )


class Company(Base):
    """Компания Фуджи или Сакура"""

    __tablename__ = "companies"

    def __str__(self) -> str:
        return self.name

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

    name: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=True)
    city: Mapped[str] = mapped_column(nullable=True)
    type: Mapped[DepartmentType] = mapped_column(Enum(DepartmentType), nullable=True)
    opening_date: Mapped[datetime.datetime] = mapped_column(nullable=True)
    closing_date: Mapped[datetime.datetime] = mapped_column(nullable=True)
    area: Mapped[float] = mapped_column(nullable=True)

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    company: Mapped["Company"] = relationship("Company", back_populates="departments")

    workers: Mapped[List["Worker"]] = relationship(
        "Worker", back_populates="department", foreign_keys="Worker.department_id"
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

    territorial_manager_id: Mapped[int] = mapped_column(
        ForeignKey("workers.id"), nullable=True
    )
    territorial_manager: Mapped["Worker"] = relationship(
        "Worker", foreign_keys=[territorial_manager_id]
    )

    territorial_brand_chef_id: Mapped[int] = mapped_column(
        ForeignKey("workers.id"), nullable=True
    )
    territorial_brand_chef: Mapped["Worker"] = relationship(
        "Worker", foreign_keys=[territorial_brand_chef_id]
    )

    delivery_manager_id: Mapped[int] = mapped_column(
        ForeignKey("workers.id"), nullable=True
    )
    delivery_manager: Mapped["Worker"] = relationship(
        "Worker", foreign_keys=[delivery_manager_id]
    )

    territorial_director_id: Mapped[int] = mapped_column(
        ForeignKey("workers.id"), nullable=True
    )
    territorial_director: Mapped["Worker"] = relationship(
        "Worker", foreign_keys=[territorial_director_id]
    )

    chief_technician_id: Mapped[int] = mapped_column(
        ForeignKey("workers.id"), nullable=True
    )
    chief_technician: Mapped["Worker"] = relationship(
        "Worker", foreign_keys=[chief_technician_id]
    )

    technician_id: Mapped[int] = mapped_column(ForeignKey("workers.id"), nullable=True)
    technician: Mapped["Worker"] = relationship("Worker", foreign_keys=[technician_id])

    electrician_id: Mapped[int] = mapped_column(ForeignKey("workers.id"), nullable=True)
    electrician: Mapped["Worker"] = relationship(
        "Worker", foreign_keys=[electrician_id]
    )

    budget_records: Mapped[List["BudgetRecord"]] = relationship(
        "BudgetRecord", back_populates="department"
    )

    it_repairman_id: Mapped[int] = mapped_column(
        ForeignKey("workers.id"), nullable=True
    )
    it_repairman: Mapped["Worker"] = relationship(
        "Worker", foreign_keys=[it_repairman_id]
    )

    # Мобилка
    dm_id: Mapped[UUID] = mapped_column(nullable=True)
    person_max_orders: Mapped[int] = mapped_column(nullable=True)
    max_close_order_distance: Mapped[int] = mapped_column(nullable=True)
    orders_collect_time: Mapped[int] = mapped_column(nullable=True)

    technical_requests: Mapped[List["TechnicalRequest"]] = relationship(
        "TechnicalRequest", back_populates="department"
    )
    bids_it: Mapped[List["BidIT"]] = relationship("BidIT", back_populates="department")


class Group(Base):
    """Отделы"""

    def __str__(self) -> str:
        return self.name

    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    workers: Mapped["Worker"] = relationship(
        "Worker",
        back_populates="group",
        foreign_keys="Worker.group_id",
        cascade="all,delete",
    )


class Worker(Base):
    __tablename__ = "workers"

    def __str__(self) -> str:
        return f"{self.l_name} {self.f_name} {self.o_name}"

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
        "Department", back_populates="workers", foreign_keys=[department_id]
    )

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=True)
    group: Mapped["Group"] = relationship(
        "Group", back_populates="workers", foreign_keys=[group_id]
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

    facs: Mapped[List["Expenditure"]] = relationship(
        "Expenditure", back_populates="fac", foreign_keys="Expenditure.fac_id"
    )
    ccs: Mapped[List["Expenditure"]] = relationship(
        "Expenditure", back_populates="cc", foreign_keys="Expenditure.cc_id"
    )
    cc_supervisors: Mapped[List["Expenditure"]] = relationship(
        "Expenditure",
        back_populates="cc_supervisor",
        foreign_keys="Expenditure.cc_supervisor_id",
    )
    expenditures: Mapped[List["Expenditure"]] = relationship(
        "Expenditure",
        back_populates="creator",
        foreign_keys="Expenditure.creator_id",
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

    gender: Mapped[Gender] = mapped_column(Enum(Gender), nullable=True)
    employment_date: Mapped[datetime.date] = mapped_column(nullable=True)
    dismissal_date: Mapped[datetime.date] = mapped_column(nullable=True)
    medical_records_availability: Mapped[bool] = mapped_column(nullable=True)
    citizenship: Mapped[str] = mapped_column(nullable=True)

    password: Mapped[str] = mapped_column(nullable=True)
    can_use_crm: Mapped[bool] = mapped_column(nullable=True, default=False)

    # Поля мобилки
    dm_id: Mapped[UUID] = mapped_column(nullable=True)
    dm_device_id: Mapped[str] = mapped_column(nullable=True)
    dm_add_info: Mapped[str] = mapped_column(nullable=True)

    worker_technical_requests: Mapped[List["TechnicalRequest"]] = relationship(
        "TechnicalRequest",
        foreign_keys="[TechnicalRequest.worker_id]",
        back_populates="worker",
    )
    repairman_technical_requests: Mapped[List["TechnicalRequest"]] = relationship(
        "TechnicalRequest",
        foreign_keys="[TechnicalRequest.repairman_id]",
        back_populates="repairman",
    )
    territorial_manager_technical_requests: Mapped[List["TechnicalRequest"]] = (
        relationship(
            "TechnicalRequest",
            foreign_keys="[TechnicalRequest.territorial_manager_id]",
            back_populates="territorial_manager",
        )
    )

    bids_it: Mapped[List["BidIT"]] = relationship(
        "BidIT", back_populates="worker", foreign_keys="[BidIT.worker_id]"
    )
    repairman_it: Mapped[List["BidIT"]] = relationship(
        "BidIT", back_populates="repairman", foreign_keys="[BidIT.repairman_id]"
    )
    territorial_manager_it: Mapped[List["BidIT"]] = relationship(
        "BidIT",
        back_populates="territorial_manager",
        foreign_keys="[BidIT.territorial_manager_id]",
    )


class Bid(Base):
    """Заявки"""

    __tablename__ = "bids"

    def __str__(self) -> str:
        return f"Заявка от {self.create_date.strftime('%H:%M %d.%m.%y')}"

    amount: Mapped[int] = mapped_column(nullable=False)
    payment_type: Mapped[str] = mapped_column(nullable=False)
    purpose: Mapped[str] = mapped_column(nullable=False)
    comment: Mapped[str] = mapped_column(nullable=True, default="")
    denying_reason: Mapped[str] = mapped_column(nullable=True, default="")
    create_date: Mapped[datetime.datetime] = mapped_column(nullable=False)
    close_date: Mapped[datetime.datetime] = mapped_column(nullable=True)
    # Electronic document management
    need_edm: Mapped[bool] = mapped_column(nullable=True)

    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    department: Mapped["Department"] = relationship("Department", back_populates="bids")

    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id"))
    worker: Mapped["Worker"] = relationship("Worker", back_populates="bids")

    expenditure_id: Mapped[int] = mapped_column(ForeignKey("expenditures.id"))
    expenditure: Mapped["Expenditure"] = relationship(
        "Expenditure", back_populates="bids"
    )

    documents: Mapped[List["BidDocument"]] = relationship(
        "BidDocument", cascade="all,delete"
    )

    # States
    fac_state: Mapped[approvalstatus]
    cc_state: Mapped[approvalstatus]
    cc_supervisor_state: Mapped[approvalstatus]
    kru_state: Mapped[approvalstatus]
    owner_state: Mapped[approvalstatus]
    accountant_cash_state: Mapped[approvalstatus]
    accountant_card_state: Mapped[approvalstatus]
    teller_cash_state: Mapped[approvalstatus]
    teller_card_state: Mapped[approvalstatus]


class BidDocument(Base):
    """Документы заявок на платежи"""

    __tablename__ = "bids_documents"

    document: Mapped[FileType] = mapped_column(FileType(storage=get_settings().storage))
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id"))
    bid: Mapped["Bid"] = relationship("Bid", back_populates="documents")


class WorkerBid(Base):
    """Заявки на найм"""

    __tablename__ = "worker_bids"

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

    comment: Mapped[str] = mapped_column(nullable=True, default="")


class WorkerBidDocument(Base):
    """Общий класс для документов анкеты на найм"""

    __abstract__ = True

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

    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id"))
    worker: Mapped["Worker"] = relationship("Worker", back_populates="work_times")

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
    salary: Mapped[int] = mapped_column(nullable=True)


class Expenditure(Base):
    """Статьи"""

    __tablename__ = "expenditures"

    name: Mapped[str] = mapped_column(nullable=False)
    chapter: Mapped[str] = mapped_column(nullable=False)
    create_date: Mapped[datetime.datetime] = mapped_column(nullable=False)

    # financial responsibility center
    fac_id: Mapped[int] = mapped_column(ForeignKey("workers.id"))
    fac: Mapped["Worker"] = relationship(
        "Worker", back_populates="facs", foreign_keys=[fac_id]
    )

    # cost center
    cc_id: Mapped[int] = mapped_column(ForeignKey("workers.id"))
    cc: Mapped["Worker"] = relationship(
        "Worker", back_populates="ccs", foreign_keys=[cc_id]
    )

    # cost center supervisor
    cc_supervisor_id: Mapped[int] = mapped_column(ForeignKey("workers.id"))
    cc_supervisor: Mapped["Worker"] = relationship(
        "Worker", back_populates="cc_supervisors", foreign_keys=[cc_supervisor_id]
    )

    creator_id: Mapped[int] = mapped_column(ForeignKey("workers.id"))
    creator: Mapped["Worker"] = relationship(
        "Worker", back_populates="expenditures", foreign_keys=[creator_id]
    )

    budget_records: Mapped[List["BudgetRecord"]] = relationship(
        "BudgetRecord",
        back_populates="expenditure",
        cascade="all,delete",
        foreign_keys="BudgetRecord.expenditure_id",
    )

    bids: Mapped[List["Bid"]] = relationship(
        "Bid",
        back_populates="expenditure",
        cascade="all,delete",
        foreign_keys="Bid.expenditure_id",
    )


class BudgetRecord(Base):
    """Записи в бюджете"""

    __tablename__ = "budget_records"

    expenditure_id: Mapped[int] = mapped_column(ForeignKey("expenditures.id"))
    expenditure: Mapped["Expenditure"] = relationship(
        "Expenditure", back_populates="budget_records"
    )
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), nullable=True
    )
    department: Mapped["Department"] = relationship(
        "Department", back_populates="budget_records"
    )

    limit: Mapped[float] = mapped_column(nullable=True)
    last_update: Mapped[datetime.datetime] = mapped_column(nullable=True)


class ProblemIT(Base):
    """Проблемы c компьютерами"""

    __tablename__ = "problems_it"

    def __str__(self) -> str:
        return self.name

    name: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[str] = mapped_column(nullable=False)
    sla: Mapped[float] = mapped_column(nullable=False)

    bids_it: Mapped[list["BidIT"]] = relationship("BidIT", back_populates="problem")


class BidITDocument(Base):
    """Общий класс для документов заявок в IT отдел"""

    __abstract__ = True

    document: Mapped[FileType] = mapped_column(FileType(storage=get_settings().storage))
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids_it.id"))


class BidITWorkerDocument(BidITDocument):
    """Документы заявок заявителей в IT отдел"""

    __tablename__ = "bids_it_documents_worker"

    bid_it: Mapped["BidIT"] = relationship("BidIT", back_populates="problem_photos")


class BidITRepairmanDocument(BidITDocument):
    """Документы специалистов IT отдела о выполненной работе"""

    __tablename__ = "bids_it_documents_repairman"

    bid_it: Mapped["BidIT"] = relationship("BidIT", back_populates="work_photos")


class BidIT(Base):
    """Заявки в IT отдел"""

    __tablename__ = "bids_it"

    problem_comment: Mapped[str] = mapped_column(nullable=False)
    work_comment: Mapped[str] = mapped_column(nullable=True)
    reopen_work_comment: Mapped[str] = mapped_column(nullable=True)

    problem_photos: Mapped[List["BidITWorkerDocument"]] = relationship(
        "BidITWorkerDocument", cascade="all,delete", back_populates="bid_it"
    )
    work_photos: Mapped[List["BidITRepairmanDocument"]] = relationship(
        "BidITRepairmanDocument", cascade="all,delete", back_populates="bid_it"
    )

    problem_id: Mapped[int] = mapped_column(
        ForeignKey("problems_it.id"), nullable=False
    )
    problem: Mapped["ProblemIT"] = relationship(
        "ProblemIT", back_populates="bids_it", foreign_keys=[problem_id]
    )

    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id"), nullable=False)
    worker: Mapped["Worker"] = relationship(
        "Worker", back_populates="bids_it", foreign_keys=[worker_id]
    )

    repairman_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("workers.id"), nullable=True
    )
    repairman: Mapped["Worker"] = relationship(
        "Worker", back_populates="repairman_it", foreign_keys=[repairman_id]
    )

    territorial_manager_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("workers.id"), nullable=True
    )
    territorial_manager: Mapped["Worker"] = relationship(
        "Worker",
        back_populates="territorial_manager_it",
        foreign_keys=[territorial_manager_id],
    )

    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), nullable=False
    )
    department: Mapped["Department"] = relationship(
        "Department", back_populates="bids_it", foreign_keys=[department_id]
    )

    status: Mapped[approvalstatus]
    mark: Mapped[int] = mapped_column(nullable=True)

    opening_date: Mapped[datetime.datetime] = mapped_column(nullable=False)
    done_date: Mapped[datetime.datetime] = mapped_column(nullable=True)
    reopening_date: Mapped[datetime.datetime] = mapped_column(nullable=True)
    approve_date: Mapped[datetime.datetime] = mapped_column(nullable=True)
    close_date: Mapped[datetime.datetime] = mapped_column(nullable=True)
    reopen_done_date: Mapped[datetime.datetime] = mapped_column(nullable=True)
    reopen_approve_date: Mapped[datetime.datetime] = mapped_column(nullable=True)


# region Technical Request
class Problem(Base):
    __abstract__ = True

    problem_name: Mapped[str] = mapped_column(nullable=False, unique=True)

    def __str__(self):
        return self.problem_name


class TechnicalProblem(Problem):
    """Виды технических проблем"""

    __tablename__ = "technical_problems"

    executor: Mapped[Executor] = mapped_column(Enum(Executor), nullable=False)
    sla: Mapped[int] = mapped_column(nullable=False)
    requests: Mapped[list["TechnicalRequest"]] = relationship(
        "TechnicalRequest", back_populates="problem"
    )


class TechnicalRequestDocument(Base):
    """Общий класс для документов у заявок на тех. ремонт"""

    __abstract__ = True

    document: Mapped[FileType] = mapped_column(FileType(storage=get_settings().storage))
    technical_request_id: Mapped[int] = mapped_column(
        ForeignKey("technical_requests.id")
    )


class TechnicalRequestProblemPhoto(TechnicalRequestDocument):
    """Фото поломок для тех заявок"""

    __tablename__ = "technical_requests_problem_photos"

    technical_request: Mapped["TechnicalRequest"] = relationship(
        "TechnicalRequest", back_populates="problem_photos"
    )


class TechnicalRequestRepairPhoto(TechnicalRequestDocument):
    """Фото ремонта для тех заявок"""

    __tablename__ = "technical_requests_repair_photos"

    technical_request: Mapped["TechnicalRequest"] = relationship(
        "TechnicalRequest", back_populates="repair_photos"
    )


class TechnicalRequest(Base):
    """Технические заявки"""

    __tablename__ = "technical_requests"

    problem_id: Mapped[int] = mapped_column(ForeignKey("technical_problems.id"))
    problem: Mapped["TechnicalProblem"] = relationship(
        "TechnicalProblem", back_populates="requests"
    )

    description: Mapped[str] = mapped_column(nullable=False)

    problem_photos: Mapped[List["TechnicalRequestProblemPhoto"]] = relationship(
        "TechnicalRequestProblemPhoto",
        cascade="all,delete",
        back_populates="technical_request",
    )

    repair_photos: Mapped[List["TechnicalRequestRepairPhoto"]] = relationship(
        "TechnicalRequestRepairPhoto",
        cascade="all,delete",
        back_populates="technical_request",
    )

    state: Mapped[approvalstatus]
    score: Mapped[int] = mapped_column(
        CheckConstraint("(score>0 AND score<6) OR NULL"), nullable=True
    )

    open_date: Mapped[datetime.datetime] = mapped_column(nullable=False)
    deadline_date: Mapped[datetime.datetime] = mapped_column(nullable=False)

    repair_date: Mapped[datetime.datetime] = mapped_column(nullable=True)
    confirmation_date: Mapped[datetime.datetime] = mapped_column(nullable=True)
    confirmation_description: Mapped[str] = mapped_column(nullable=True)

    reopen_date: Mapped[datetime.datetime] = mapped_column(nullable=True)
    reopen_deadline_date: Mapped[datetime.datetime] = mapped_column(nullable=True)

    reopen_repair_date: Mapped[datetime.datetime] = mapped_column(nullable=True)
    reopen_confirmation_date: Mapped[datetime.datetime] = mapped_column(nullable=True)

    close_date: Mapped[datetime.datetime] = mapped_column(nullable=True)
    close_description: Mapped[str] = mapped_column(nullable=True)

    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id"), nullable=False)
    worker: Mapped["Worker"] = relationship(
        "Worker", back_populates="worker_technical_requests", foreign_keys=[worker_id]
    )

    repairman_id: Mapped[int] = mapped_column(ForeignKey("workers.id"), nullable=False)
    repairman: Mapped["Worker"] = relationship(
        "Worker",
        back_populates="repairman_technical_requests",
        foreign_keys=[repairman_id],
    )

    territorial_manager_id: Mapped[int] = mapped_column(
        ForeignKey("workers.id"), nullable=False
    )
    territorial_manager: Mapped["Worker"] = relationship(
        "Worker",
        back_populates="territorial_manager_technical_requests",
        foreign_keys=[territorial_manager_id],
    )

    acceptor_post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=True)
    acceptor_post: Mapped["Post"] = relationship(
        "Post",
        back_populates="acceptor_technical_request",
        foreign_keys=[acceptor_post_id],
    )

    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), nullable=False
    )
    department: Mapped["Department"] = relationship(
        "Department", back_populates="technical_requests", foreign_keys=[department_id]
    )


# endregion
