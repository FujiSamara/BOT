from typing import Optional
from fastapi_storages import StorageFile
from pydantic import BaseModel, field_validator
import datetime
from pathlib import Path
from fastapi import UploadFile
from db.models import ApprovalStatus, FujiScope, Gender, PostScope, Executor
from io import BytesIO
import logging


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
                logging.getLogger("uvicorn.error").warning(
                    f"File with path: {val.path} not exist"
                )
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


class WorkTimeSchema(BaseSchema):
    worker: Optional[WorkerSchema]
    department: Optional[DepartmentSchema]
    post: Optional[PostSchema]

    work_begin: Optional[str]
    work_end: Optional[str]
    day: str
    work_duration: float

    rating: Optional[int]
    fine: Optional[int]


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
    department: DepartmentSchema


# endregion


# region Extended schemas for api
class FileSchema(BaseModel):
    name: str
    href: str


class BudgetRecordWithChapter(BudgetRecordSchema):
    chapter: str


class BidRecordSchema(BaseSchema):
    """Shortened version of `BidSchema` for crm api"""

    amount: float
    payment_type: str
    department: DepartmentSchema
    worker: WorkerSchema
    purpose: str
    create_date: datetime.datetime
    close_date: Optional[datetime.datetime]
    documents: list[FileSchema]
    status: str
    comment: Optional[str]
    denying_reason: Optional[str]
    expenditure: ExpenditureSchema

    @field_validator("documents", mode="before")
    @classmethod
    def upload_file_validate(cls, val):
        from db import service

        if isinstance(val, list):
            result = []
            for doc in val:
                if isinstance(doc, UploadFile):
                    if hasattr(doc.file, "name"):
                        result.append(service.get_file_data(doc.file.name, "api"))
                else:
                    return val
            return result
        return val


# endregion
