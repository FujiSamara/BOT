from typing import Optional
from pydantic import BaseModel
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
    id: int
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

    amount: int
    payment_type: str
    department: DepartmentShema
    worker: WorkerShema
    purpose: str
    create_date: datetime.datetime
    document: UploadFile

    agreement: Optional[str] = "Нет"
    urgently: Optional[str] = "Нет"
    need_document: Optional[str] = "Нет"
    comment: Optional[str]

    # States
    kru_status: ApprovalStatus
    owner_status: ApprovalStatus
    accountant_card: ApprovalStatus
    accountant_cash: ApprovalStatus
    teller_card: ApprovalStatus
    teller_cash: ApprovalStatus

# Create shemas