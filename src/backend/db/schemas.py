from typing import Optional
from fastapi_storages import StorageFile
from pydantic import BaseModel, field_validator
import datetime
from fastapi import UploadFile
from db.models import ApprovalStatus

# Full shemas
class BaseShema(BaseModel):
    class Config:
        from_attributes = True
    id: int

class PostShema(BaseShema):
    name: str
    level: int

class CompanyShema(BaseShema):
    name: str

class DepartmentShema(BaseShema):
    name: str
    address: Optional[str]

    company: CompanyShema

class WorkerShema(BaseShema):
    f_name: str
    l_name: str
    o_name: str
    b_date: Optional[datetime.date] = datetime.date(1, 1, 1)
    phone_number: str
    telegram_id: Optional[int]

    post: PostShema

    department: DepartmentShema

class BidShema(BaseModel):
    class Config:
        arbitrary_types_allowed=True

    id: Optional[int]

    amount: int
    payment_type: str
    department: DepartmentShema
    worker: WorkerShema
    purpose: str
    create_date: datetime.datetime
    document: UploadFile

    @field_validator("document", mode="before")
    @classmethod
    def upload_file_validate(cls, val):
        if isinstance(val, StorageFile):
            return UploadFile(val.open())
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

# Create shemas