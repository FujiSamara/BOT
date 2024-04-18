from typing import Optional
from pydantic import BaseModel
import datetime

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
    address: str = ""

    company: CompanyShema

class WorkerShema(BaseShema):
    f_name: str
    l_name: str
    o_name: str
    b_date: datetime.date = datetime.date(1, 1, 1)
    phone_number: str
    telegram_id: Optional[int]

    post: PostShema

    department: DepartmentShema

class BidShema(BaseModel):
    amount: int
    payment_type: str
    department: DepartmentShema
    worker: WorkerShema
    purpose: str
    create_date: datetime.datetime

    agreement: Optional[str]
    urgently: Optional[str]
    need_document: Optional[str]
    comment: Optional[str]
# Create shemas