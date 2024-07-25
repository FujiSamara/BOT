from typing import Optional
from fastapi_storages import StorageFile
from pydantic import BaseModel, field_validator
import datetime
from fastapi import UploadFile
from db.models import ApprovalStatus, Gender


# Full shemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

    id: int


class PostSchema(BaseSchema):
    name: str
    level: int


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

    post: Optional[PostSchema]

    department: DepartmentSchema

    gender: Optional[Gender]
    employment_date: Optional[datetime.date]
    dismissal_date: Optional[datetime.date]
    medical_records_availability: Optional[bool]
    citizenship: Optional[str]


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
    document: UploadFile
    document1: Optional[UploadFile]
    document2: Optional[UploadFile]

    @field_validator("document", "document1", "document2", mode="before")
    @classmethod
    def upload_file_validate(cls, val):
        if isinstance(val, StorageFile):
            return UploadFile(val.open(), filename=val.name)
        return val

    agreement: Optional[str] = "Нет"
    urgently: Optional[str] = "Нет"
    need_document: Optional[str] = "Нет"
    comment: Optional[str]
    denying_reason: Optional[str]

    # States
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

    worksheet: list["WorkerBidWorksheetSchema"]

    passport: list["WorkerBidPassportSchema"]

    work_permission: list["WorkerBidWorkPermissionSchema"]

    state: ApprovalStatus

    sender: WorkerSchema

    comment: Optional[str]


class WorkerBidDocumentSchema(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True

    id: Optional[int] = -1
    document: UploadFile

    @field_validator("document", mode="before")
    @classmethod
    def upload_file_validate(cls, val):
        if isinstance(val, StorageFile):
            return UploadFile(val.open(), filename=val.name)
        return val


class WorkerBidWorksheetSchema(WorkerBidDocumentSchema):
    pass


class WorkerBidPassportSchema(WorkerBidDocumentSchema):
    pass


class WorkerBidWorkPermissionSchema(WorkerBidDocumentSchema):
    pass


# Create shemas
class FileSchema(BaseModel):
    name: str
    href: str


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


class BudgetRecordSchema(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True

    id: Optional[int] = -1
    expenditure: ExpenditureSchema
    limit: Optional[float]
    last_update: Optional[datetime.datetime]
    department: Optional[DepartmentSchema]


class BudgetRecordWithChapter(BudgetRecordSchema):
    @field_validator("chapter", mode="before")
    @classmethod
    def upload_file_validate(cls, _):
        return cls.expenditure.chapter

    chapter: str
