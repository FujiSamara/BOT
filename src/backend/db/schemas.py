from typing import Optional
from fastapi_storages import StorageFile
from pydantic import BaseModel, field_validator
import datetime
from fastapi import UploadFile
from db.models import ApprovalStatus


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
