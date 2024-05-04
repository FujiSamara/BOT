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
    phone_number: str
    telegram_id: Optional[int]

    post: PostSchema

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
    document: UploadFile

    @field_validator("document", mode="before")
    @classmethod
    def upload_file_validate(cls, val):
        if isinstance(val, StorageFile):
            return UploadFile(val.open(), filename=val.name)
        return val

    agreement: Optional[str] = "Нет"
    urgently: Optional[str] = "Нет"
    need_document: Optional[str] = "Нет"
    comment: Optional[str]

    # States
    kru_state: ApprovalStatus
    owner_state: ApprovalStatus
    accountant_card_state: ApprovalStatus
    accountant_cash_state: ApprovalStatus
    teller_card_state: ApprovalStatus
    teller_cash_state: ApprovalStatus


class WorkTimeSchema(BaseSchema):
    worker: WorkerSchema
    department: DepartmentSchema

    work_begin: str
    work_end: Optional[str]
    day: str
    work_duration: float


# Create shemas
