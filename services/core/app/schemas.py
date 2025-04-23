from typing import Any, Optional, Type, TypeVar, Annotated
from fastapi_storages import StorageFile
from pydantic import BaseModel, ConfigDict, Field, field_validator, StringConstraints
import datetime
from pathlib import Path
from fastapi import UploadFile
from app.infra.database.models import (
    ApprovalStatus,
    WorkerStatus,
    FujiScope,
    Gender,
    IncidentStage,
    PostScope,
    Executor,
    ViewStatus,
)
from io import BytesIO

from app.infra.config import settings


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


SchemaT = TypeVar("SchemaT", bound=BaseSchema)


# region Schemas for models
class BaseSchemaPK(BaseSchema):
    id: int | None = -1


class DocumentSchema(BaseSchemaPK):
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


class PostSchema(BaseSchemaPK):
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


class CompanySchema(BaseSchemaPK):
    name: str


class DepartmentSchema(BaseSchemaPK):
    name: str
    address: str | None

    company: CompanySchema


class DepartmentSchemaFull(DepartmentSchema):
    territorial_manager: Optional["WorkerSchema"]


class GroupSchema(BaseSchemaPK):
    name: str


class WorkerSchema(BaseSchemaPK):
    f_name: str
    l_name: str
    o_name: str
    b_date: Optional[datetime.date] = datetime.date(1, 1, 1)
    phone_number: Optional[str]
    telegram_id: Optional[int]
    state: WorkerStatus | None = None
    post: PostSchema

    department: DepartmentSchema

    gender: Optional[Gender]
    employment_date: Optional[datetime.date]
    official_employment_date: datetime.date | None = None
    dismissal_date: Optional[datetime.date]
    official_dismissal_date: datetime.date | None = None
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

    snils: str | None = None
    inn: str | None = None
    registration: str | None = None
    actual_residence: str | None = None
    children: bool | None = None
    children_born_date: list["WorkerChildrenSchema"] = []
    military_ticket: str | None = None
    patent: str | None = None
    official_work: bool | None = None
    iiko_id: int | None = None
    actual_residence: str | None = None


class WorkerChildrenSchema(BaseSchemaPK):
    born_date: datetime.datetime


class BidSchema(BaseSchemaPK):
    amount: int
    payment_type: str
    department: DepartmentSchema
    paying_department: DepartmentSchema | None = None
    worker: WorkerSchema
    purpose: str
    create_date: datetime.datetime
    close_date: Optional[datetime.datetime]
    documents: list[DocumentSchema]

    comment: Optional[str]
    denying_reason: Optional[str]
    paying_comment: str | None = None

    expenditure: "ExpenditureSchema"
    need_edm: Optional[bool]
    activity_type: str

    # States
    fac_state: ApprovalStatus
    cc_state: ApprovalStatus
    paralegal_state: ApprovalStatus
    kru_state: ApprovalStatus
    owner_state: ApprovalStatus
    accountant_card_state: ApprovalStatus
    accountant_cash_state: ApprovalStatus
    teller_card_state: ApprovalStatus
    teller_cash_state: ApprovalStatus


class WorkTimeSchema(BaseSchemaPK):
    worker: Optional[WorkerSchema] = None
    department: Optional[DepartmentSchema] = None
    post: Optional[PostSchema] = None

    work_begin: Optional[datetime.datetime] = None
    work_end: Optional[datetime.datetime] = None
    day: Optional[datetime.date] = None
    work_duration: Optional[float] = None

    rating: Optional[int] = None
    fine: Optional[int] = None


class WorkTimeSchemaFull(WorkTimeSchema):
    photo_b64: str | None = None


class WorkerBidSchema(BaseSchemaPK):
    f_name: str
    l_name: str
    o_name: Optional[str]
    create_date: datetime.datetime
    close_date: datetime.datetime | None = None

    post: PostSchema

    department: DepartmentSchema

    birth_date: datetime.datetime | None = None
    phone_number: (
        Annotated[str, StringConstraints(min_length=11, max_length=12)] | None
    ) = None

    worksheet: list[DocumentSchema]

    passport: list[DocumentSchema]

    work_permission: list[DocumentSchema]
    view_state: ViewStatus | None = None
    state: ApprovalStatus
    security_service_state: ApprovalStatus | None = None
    accounting_service_state: ApprovalStatus | None = None
    iiko_service_state: ApprovalStatus | None = None
    financial_director_state: ApprovalStatus | None = None

    sender: WorkerSchema

    comment: str | None = None
    security_service_comment: str | None = None
    accounting_service_comment: str | None = None
    iiko_worker_id: int | None = None
    financial_director_comment: str | None = None

    official_work: bool | None = None
    employed: bool | None = None
    document_request: list["WorkerBidDocumentRequestSchema"] = []


class WorkerBidDocumentRequestSchema(BaseSchemaPK):
    sender: WorkerSchema
    worker_bid: WorkerBidSchema
    date: datetime.datetime
    message: str


class ExpenditureSchema(BaseSchemaPK):
    name: str
    chapter: str
    create_date: Optional[datetime.datetime] = datetime.datetime.now()
    fac: WorkerSchema
    cc: WorkerSchema
    paralegal: WorkerSchema
    creator: Optional[WorkerSchema] = None


class BudgetRecordSchema(BaseSchemaPK):
    expenditure: ExpenditureSchema
    limit: Optional[float] = None
    last_update: Optional[datetime.datetime] = None
    department: Optional[DepartmentSchema] = None


class ProblemITSchema(BaseSchemaPK):
    name: str
    category: str
    sla: float


class BidITSchema(BaseSchemaPK):
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


class TechnicalProblemSchema(BaseSchemaPK):
    problem_name: str
    executor: Executor
    sla: float


class TechnicalRequestSchema(BaseSchemaPK):
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
    appraiser: WorkerSchema
    acceptor_post: Optional[PostSchema] = None
    department: DepartmentSchema

    repairman_worktime: int | None = 0

    not_relevant_description: str | None = None
    not_relevant_date: datetime.datetime | None = None
    not_relevant_confirmation_date: datetime.datetime | None = None
    not_relevant_confirmation_description: str | None = None


class AccountLoginsSchema(BaseSchemaPK):
    worker: WorkerSchema

    cop_mail_login: Optional[str] = None

    liko_login: Optional[str] = None

    bitrix_login: Optional[str] = None

    pyrus_login: Optional[str] = None

    check_office_login: Optional[str] = None

    pbi_login: Optional[str] = None


class MaterialValuesSchema(BaseSchemaPK):
    worker: WorkerSchema
    item: str
    quanity: int
    price: int
    inventory_number: str
    issue_date: datetime.datetime
    return_date: Optional[datetime.datetime] = None


class SubordinationSchema(BaseSchemaPK):
    chief: WorkerSchema
    employee: WorkerSchema


class FileSchema(BaseSchemaPK):
    file: UploadFile

    @field_validator("file", mode="before")
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

        host = settings.domain
        port = settings.port
        if settings.ssl_certfile:
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


class EquipmentStatusSchema(BaseSchemaPK):
    asterisk_id: str
    status: str
    ip_address: str
    latency: float
    department: DepartmentSchemaFull
    last_update: datetime.datetime
    equipment_name: str


class EquipmentStatusSchemaIn(BaseSchemaPK):
    status: str
    ip_address: str
    latency: float


class EquipmentIncidentSchema(BaseSchemaPK):
    equipment_status: EquipmentStatusSchema
    incident_time: datetime.datetime
    status: str
    stage: IncidentStage


class ShiftDurationSchema(BaseSchema):
    worktime_id: int
    duration: float


class TimeSheetSchema(BaseSchemaPK):
    worker_fullname: str
    post_name: str
    department_name: str
    total_shifts: int
    total_hours: float
    duration_per_day: dict[datetime.date, ShiftDurationSchema | float]
    last_day: int | None = Field(exclude=True, default=None)

    def model_dump(self, **_) -> dict[str, Any]:
        data = {
            "id": self.id,
            "worker_fullname": self.worker_fullname,
            "department_name": self.department_name,
            "post_name": self.post_name,
            "total_hours": self.total_hours,
            "total_shifts": self.total_shifts,
            **{str(day): 0 for day in range(1, self.last_day + 1)},
        }

        duration_per_day = self.duration_per_day

        for date in duration_per_day:
            data[str(date.day)] = duration_per_day[date].model_dump()

        return data


class AuthClientSchema(BaseSchema):
    id: str
    secret: str

    scopes: list[str]


class CleaningProblemSchema(BaseSchemaPK):
    problem_name: str


class CleaningRequestSchema(BaseSchemaPK):
    problem: CleaningProblemSchema
    description: str
    state: ApprovalStatus
    score: int | None = None
    worker: WorkerSchema

    problem_photos: list[DocumentSchema] | None = None
    cleaning_photos: list[DocumentSchema] | None = None
    cleaner: WorkerSchema
    appraiser: WorkerSchema
    department: DepartmentSchema

    open_date: datetime.datetime
    cleaning_date: datetime.datetime | None = None

    confirmation_date: datetime.datetime | None = None
    confirmation_description: str | None = None

    reopen_date: datetime.datetime | None = None
    reopen_cleaning_date: datetime.datetime | None = None

    reopen_cleaning_date: datetime.datetime | None = None
    reopen_confirmation_date: datetime.datetime | None = None

    close_date: datetime.datetime | None = None
    close_description: str | None = None


# endregion


# region Extended schemas for api
class FileOutSchema(BaseModel):
    name: str
    href: str
    description: Optional[str] = None


class BudgetRecordWithChapter(BudgetRecordSchema):
    chapter: str


class BidOutSchema(BaseSchemaPK):
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
    activity_type: str

    @field_validator("documents", mode="before")
    @classmethod
    def upload_file_validate(cls, val):
        from app import services

        if isinstance(val, list):
            result = []
            for doc in val:
                if isinstance(doc, UploadFile):
                    if hasattr(doc.file, "name"):
                        result.append(services.get_file_data(doc.filename, "api"))
            return result
        return val


class BidInSchema(BaseSchemaPK):
    """In version of `BidSchema` for crm api"""

    amount: float
    payment_type: str
    department: DepartmentSchema
    worker: Optional[WorkerSchema] = None
    purpose: str
    comment: Optional[str] = ""
    expenditure: ExpenditureSchema
    need_edm: Optional[bool]
    activity_type: str


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
        "department": "Предприятие",
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
        "paralegal": "Юрисконсульт",
        "creator": "Создал",
    },
    WorkTimeSchema: {
        "id": "ID",
        "worker": "Работник",
        "department": "Предприятие",
        "post": "Должность",
        "work_begin": "Начало смены",
        "work_end": "Конец смены",
        "day": "День",
        "work_duration": "Длительность",
        "rating": "Оценка",
        "fine": "Штраф",
    },
    TimeSheetSchema: {
        "worker_fullname": "ФИО",
        "post_name": "Должность",
        "total_hours": "Суммарно отработано",
        "department_name": "Предприятие",
    },
}
