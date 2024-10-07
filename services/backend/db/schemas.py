from typing import Any, Optional, Type
from fastapi_storages import StorageFile
from pydantic import BaseModel, field_validator
import datetime
from pathlib import Path
from fastapi import UploadFile
from db.models import ApprovalStatus, FujiScope, Gender, PostScope, Executor
from io import BytesIO

from settings import get_settings


# region Shemas for models
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

    id: int


class PostSchema(BaseSchema):
    name: str
    level: int
    scopes: list[FujiScope]

    @field_validator("scopes", mode="before")
    @classmethod
    def upload_file_validate(cls, val):
        if isinstance(val, list):
            result = []
            for raw_scope in val:
                if isinstance(raw_scope, PostScope):
                    result.append(raw_scope.scope)

            return result
        return val


class CompanySchema(BaseSchema):
    name: str


class DepartmentSchema(BaseSchema):
    name: str
    address: Optional[str]

    company: CompanySchema


class GroupSchema(BaseSchema):
    name: str


class WorkerSchema(BaseSchema):
    f_name: str
    l_name: str
    o_name: str
    b_date: Optional[datetime.date] = datetime.date(1, 1, 1)
    phone_number: Optional[str]
    telegram_id: Optional[int]

    post: PostSchema

    department: DepartmentSchema

    gender: Optional[Gender]
    employment_date: Optional[datetime.date]
    dismissal_date: Optional[datetime.date]
    medical_records_availability: Optional[bool]
    citizenship: Optional[str]

    password: Optional[str]
    can_use_crm: Optional[bool] = False

    @field_validator("gender", mode="before")
    @classmethod
    def upload_file_validate(cls, val):
        if isinstance(val, list):
            return (val[0],)
        return val


class DocumentSchema(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True

    id: Optional[int] = -1
    document: UploadFile

    @field_validator("document", mode="before")
    @classmethod
    def upload_file_validate(cls, val):
        if isinstance(val, StorageFile):
            if Path(val.path).is_file():
                return UploadFile(val.open(), filename=val.name)
            else:
                return UploadFile(BytesIO(b"File not exist"), filename=val.name)
        return val


class BidSchema(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True

    id: Optional[int] = -1

    amount: int
    payment_type: str
    department: DepartmentSchema
    worker: WorkerSchema
    purpose: str
    create_date: datetime.datetime
    close_date: Optional[datetime.datetime]
    documents: list[DocumentSchema]

    comment: Optional[str]
    denying_reason: Optional[str]

    expenditure: "ExpenditureSchema"
    need_edm: Optional[bool]

    # States
    fac_state: ApprovalStatus
    cc_state: ApprovalStatus
    cc_supervisor_state: ApprovalStatus
    kru_state: ApprovalStatus
    owner_state: ApprovalStatus
    accountant_card_state: ApprovalStatus
    accountant_cash_state: ApprovalStatus
    teller_card_state: ApprovalStatus
    teller_cash_state: ApprovalStatus


class WorkTimeSchema(BaseModel):
    class Config:
        from_attributes = True

    id: Optional[int] = -1

    worker: Optional[WorkerSchema] = None
    department: Optional[DepartmentSchema] = None
    post: Optional[PostSchema] = None

    work_begin: Optional[str] = None
    work_end: Optional[str] = None
    day: str
    work_duration: Optional[float] = None

    rating: Optional[int] = None
    fine: Optional[int] = None


class WorkerBidSchema(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True

    id: Optional[int] = -1

    f_name: str
    l_name: str
    o_name: Optional[str]
    create_date: datetime.datetime

    post: PostSchema

    department: DepartmentSchema

    worksheet: list[DocumentSchema]

    passport: list[DocumentSchema]

    work_permission: list[DocumentSchema]

    state: ApprovalStatus

    sender: WorkerSchema

    comment: Optional[str]


class ExpenditureSchema(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True

    id: Optional[int] = -1
    name: str
    chapter: str
    create_date: Optional[datetime.datetime] = datetime.datetime.now()
    fac: WorkerSchema
    cc: WorkerSchema
    cc_supervisor: WorkerSchema
    creator: Optional[WorkerSchema] = None


class BudgetRecordSchema(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True

    id: Optional[int] = -1
    expenditure: ExpenditureSchema
    limit: Optional[float] = None
    last_update: Optional[datetime.datetime] = None
    department: Optional[DepartmentSchema] = None


class ProblemITSchema(BaseSchema):
    name: str
    category: str
    sla: float


class BidITSchema(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True

    id: Optional[int] = -1
    problem: ProblemITSchema
    problem_comment: str
    problem_photos: list[DocumentSchema]
    worker: WorkerSchema
    department: DepartmentSchema
    opening_date: datetime.datetime
    done_date: Optional[datetime.datetime] = None
    reopening_date: Optional[datetime.datetime] = None
    reopen_done_date: Optional[datetime.datetime] = None
    approve_date: Optional[datetime.datetime] = None
    reopen_approve_date: Optional[datetime.datetime] = None
    close_date: Optional[datetime.datetime] = None
    status: ApprovalStatus
    repairman: Optional[WorkerSchema] = None
    territorial_manager: Optional[WorkerSchema] = None
    mark: Optional[int] = None
    work_photos: list[DocumentSchema] = None
    work_comment: Optional[str] = None
    reopen_work_comment: Optional[str] = None


# Technical request
class TechnicalProblemSchema(BaseSchema):
    id: Optional[int] = -1
    problem_name: str
    executor: Executor
    sla: float


class TechnicalRequestSchema(BaseSchema):
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True

    id: Optional[int] = -1

    # Данные при создание
    problem: TechnicalProblemSchema
    description: str
    problem_photos: list[DocumentSchema]
    repair_photos: Optional[list[DocumentSchema]] = None

    open_date: datetime.datetime
    deadline_date: datetime.datetime

    repair_date: Optional[datetime.datetime] = None
    confirmation_date: Optional[datetime.datetime] = None
    confirmation_description: Optional[str] = None

    reopen_date: Optional[datetime.datetime] = None
    reopen_deadline_date: Optional[datetime.datetime] = None

    reopen_repair_date: Optional[datetime.datetime] = None
    reopen_confirmation_date: Optional[datetime.datetime] = None

    close_date: Optional[datetime.datetime] = None
    close_description: Optional[str] = None

    state: ApprovalStatus
    score: Optional[int] = None

    worker: WorkerSchema
    repairman: WorkerSchema
    territorial_manager: WorkerSchema
    acceptor_post: Optional[PostSchema] = None
    department: DepartmentSchema


class AccountLoginsSchema(BaseSchema):
    id: Optional[int] = -1

    worker: WorkerSchema

    cop_mail_login: Optional[str] = None

    liko_login: Optional[str] = None

    bitrix_login: Optional[str] = None

    pyrus_login: Optional[str] = None

    check_office_login: Optional[str] = None

    pbi_login: Optional[str] = None


class MaterialValuesSchema(BaseSchema):
    id: Optional[int] = -1
    worker: WorkerSchema
    item: str
    quanity: int
    price: int
    inventory_number: str
    issue_date: datetime.datetime


class SubordinationSchema(BaseSchema):
    id: Optional[int] = -1
    chief: WorkerSchema
    employee: WorkerSchema


class FileSchema(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True

    id: Optional[int] = -1

    file: UploadFile

    @field_validator("document", mode="before")
    @classmethod
    def upload_file_validate(cls, val):
        if isinstance(val, StorageFile):
            if Path(val.path).is_file():
                return UploadFile(val.open(), filename=val.name)
            else:
                return UploadFile(BytesIO(b"File not exist"), filename=val.name)
        return val

    def to_out(self, mode="api") -> "FileOutSchema":
        """Converted `FileSchema` to `FileOutSchema`"""
        proto = "http"

        host = get_settings().domain
        port = get_settings().port
        if get_settings().ssl_certfile:
            proto = "https"

        source: str = ""

        if mode == "sqladmin":
            source = "/admin"
        elif mode == "api":
            source = "/api"

        return FileOutSchema(
            name=self.file.filename,
            href=f"{proto}://{host}:{port}{source}/download?name={self.file.filename}",
            description=self.description,
        )

    description: Optional[str] = None


# endregion


# region Extended schemas for api
class FileOutSchema(BaseModel):
    name: str
    href: str
    description: Optional[str] = None


class BudgetRecordWithChapter(BudgetRecordSchema):
    chapter: str


class BidOutSchema(BaseSchema):
    """Out version of `BidSchema` for crm api"""

    amount: float
    payment_type: str
    department: DepartmentSchema
    worker: WorkerSchema
    purpose: str
    create_date: datetime.datetime
    close_date: Optional[datetime.datetime]
    documents: list[FileOutSchema]
    status: str
    comment: Optional[str]
    denying_reason: Optional[str]
    expenditure: ExpenditureSchema
    need_edm: Optional[bool]

    @field_validator("documents", mode="before")
    @classmethod
    def upload_file_validate(cls, val):
        from db import service

        if isinstance(val, list):
            result = []
            for doc in val:
                if isinstance(doc, UploadFile):
                    if hasattr(doc.file, "name"):
                        result.append(service.get_file_data(doc.filename, "api"))
            return result
        return val


class BidInSchema(BaseModel):
    """In version of `BidSchema` for crm api"""

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True

    id: Optional[int] = -1

    amount: float
    payment_type: str
    department: DepartmentSchema
    worker: Optional[WorkerSchema] = None
    purpose: str
    comment: Optional[str] = ""
    expenditure: ExpenditureSchema
    need_edm: Optional[bool]


class TalbeInfoSchema(BaseModel):
    page_count: int
    record_count: int
    all_record_count: int


# region Query schema


class OrderBySchema(BaseModel):
    column: str
    """Column name for order."""

    desc: bool = False
    """If **true** query will be ordered desc.
    **False** by default.
    """


class SearchSchema(BaseModel):
    column: str
    """Column name for search."""

    term: str
    """Term for search."""

    dependencies: list["SearchSchema"] = []
    """
    Dependencies are wrapping to one query
    and handles with `and_` statement relative to `self`.
    """

    groups: list[int] = []

    """Specifies groups at same level.
    
    All elements in one group handles by `and_` statement.
    
    All groups handles by `or_` statement.

    - Note: If group not specified then handles node by `or_` statement with another nodes.
    """


class DateSchema(BaseModel):
    """Presents date filter, which returns rows between
    `DateSchema.start` and `DateSchema.end`."""

    start: datetime.datetime
    end: datetime.datetime

    column: str
    """Column name for dating."""


class FilterSchema(BaseModel):
    column: str
    """Column name for search."""

    value: Any
    """Term for filtrate."""

    dependencies: list["FilterSchema"] = []

    groups: list[int] = []

    """Specifies groups at same level.
    
    All elements in one group handles by `or_` statement.
    
    All groups handles by `and_` statement.

    - Note: If group not specified then handles node by `and_` statement with another nodes.
    """


class QuerySchema(BaseModel):
    """Presents general query schema for working with crm tables."""

    search_query: list[SearchSchema] = []
    """List of search schemas handles with `or_` statement."""

    order_by_query: Optional[OrderBySchema] = None

    date_query: Optional[DateSchema] = None

    filter_query: list[FilterSchema] = []
    """List of filter schemas handles with `and_` statement."""


# endregion

# endregion


# Aliases for  schemas.
aliases: dict[Type[BaseModel], dict[str, str]] = {
    BidSchema: {
        "id": "ID",
        "amount": "Сумма",
        "payment_type": "Тип оплаты",
        "department": "Произовдство",
        "worker": "Работник",
        "purpose": "Цель",
        "create_date": "Дата создания",
        "close_date": "Дата закрытия",
        "comment": "Комментарий",
        "denying_reason": "Причина отказа",
        "expenditure": "Статья",
        "need_edm": "Счет в ЭДО",
    },
    ExpenditureSchema: {
        "id": "ID",
        "name": "Статья",
        "chapter": "Раздел",
        "create_date": "Дата создания",
        "fac": "ЦФО",
        "cc": "ЦЗ",
        "cc_supervisor": "Руководитель ЦЗ",
        "creator": "Создал",
    },
    WorkTimeSchema: {
        "id": "ID",
        "worker": "Работник",
        "department": "Производство",
        "post": "Должность",
        "work_begin": "Начало смены",
        "work_end": "Конец смены",
        "day": "День",
        "work_duration": "Длительность",
        "rating": "Оценка",
        "fine": "Штраф",
    },
}
