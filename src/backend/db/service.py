from db.orm import (
    find_worker_by_number,
    find_worker_by_telegram_id,
    update_worker,
    get_departments_with_columns,
    find_department_by_name,
    add_bid
)
from db.models import (
    Department
)
from db.schemas import *
import logging
from datetime import datetime

def get_user_level_by_telegram_id(id: str) -> int:
    '''
    Returns user access level by his telegram id.

    Return `-1`, if user doesn't exits.
    '''
    worker = find_worker_by_telegram_id(id)
    if not worker:
        return -1

    return worker.post.level

def update_user_tg_id_by_number(number: str, tg_id: int) -> bool:
    '''
    Finds user by his phone number and sets him telegram id.
    
    Returns `True`, if user found, `False` otherwise.
    '''
    worker = find_worker_by_number(number)
    if not worker:
        return False

    worker.telegram_id = tg_id
    try:
        update_worker(worker)
    except Exception as e:
        logging.getLogger("uvicorn.error").error(f"update_worker error: {e}")
        return False
    return True

def get_departments_names() -> list[str]:
    '''
    Returns all existed departments.
    '''
    departments_raw = get_departments_with_columns(Department.name)
    result = [column[0] for column in departments_raw]
    return result

def create_bid(
    amount: int,
    payment_type: str,
    department: str,
    purpose: str,
    telegram_id: int,
    agreement: Optional[str]=None,
    urgently: Optional[str]=None,
    need_document: Optional[str]=None,
    comment: Optional[str]=None
):
    '''
    Creates an bid wrapped in `BidShema` and adds it to database.
    '''
    department_inst = find_department_by_name(department)
    
    if not department_inst:
        logging.getLogger("uvicorn.error").error(
            f"Department with name '{department}' not found"
        )
        return

    worker_inst = find_worker_by_telegram_id(telegram_id)
    
    if not worker_inst:
        logging.getLogger("uvicorn.error").error(
            f"Worker with telegram id '{telegram_id}' not found"
        )
        return

    cur_date = datetime.now()

    bid = BidShema(
        amount=amount,
        payment_type=payment_type,
        department=department_inst,
        worker=worker_inst,
        purpose=purpose,
        create_date=cur_date,
        agreement=agreement,
        urgently=urgently,
        need_document=need_document,
        comment=comment
    )

    try:
        add_bid(bid)
    except Exception as e:
        logging.getLogger("uvicorn.error").error(f"Added bid failed: {e}")