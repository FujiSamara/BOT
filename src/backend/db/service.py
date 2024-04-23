from io import BytesIO
from pathlib import Path
from db.orm import (
    update_worker,
    get_departments_columns,
    add_bid,
    get_last_bid_id,
    get_bids_by_worker,
    get_pending_bids_by_worker,
    find_bid_by_column,
    find_department_by_column,
    find_worker_by_column
)
from db.models import (
    Department,
    ApprovalState
)
from db.schemas import *
from db.models import Bid, Worker, Department
import logging
from datetime import datetime
from fastapi import UploadFile

def get_user_level_by_telegram_id(id: str) -> int:
    '''
    Returns user access level by his telegram id.

    Return `-1`, if user doesn't exits.
    '''
    worker = find_worker_by_column(Worker.telegram_id, id)
    if not worker:
        return -1

    return worker.post.level

def update_user_tg_id_by_number(number: str, tg_id: int) -> bool:
    '''
    Finds worker by his phone number and sets him telegram id.
    
    Returns `True`, if user found, `False` otherwise.
    '''
    worker = find_worker_by_column(Worker.phone_number, number)
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
    departments_raw = get_departments_columns(Department.name)
    result = [column[0] for column in departments_raw]
    return result

def create_bid(
    amount: int,
    payment_type: str,
    department: str,
    purpose: str,
    telegram_id: int,
    file: BytesIO,
    filename: str,
    kru_state: ApprovalState,
    owner_state: ApprovalState,
    accountant_cash_state: ApprovalState,
    accountant_card_state: ApprovalState,
    teller_cash_state: ApprovalState,
    teller_card_state: ApprovalState,
    agreement: Optional[str]=None,
    urgently: Optional[str]=None,
    need_document: Optional[str]=None,
    comment: Optional[str]=None,
):
    '''
    Creates an bid wrapped in `BidShema` and adds it to database.
    '''
    department_inst = find_department_by_column(Department.name, department)
    
    if not department_inst:
        logging.getLogger("uvicorn.error").error(
            f"Department with name '{department}' not found"
        )
        return

    worker_inst = find_worker_by_column(Worker.telegram_id, telegram_id)
    
    if not worker_inst:
        logging.getLogger("uvicorn.error").error(
            f"Worker with telegram id '{telegram_id}' not found"
        )
        return

    cur_date = datetime.now()
    last_bid_id = get_last_bid_id()
    if not last_bid_id:
        last_bid_id = 0

    suffix = Path(filename).suffix
    filename = f"document_{last_bid_id + 1}{suffix}"

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
        comment=comment,
        document=UploadFile(file=file, filename=filename),
        kru_state=kru_state,
        owner_state=owner_state,
        accountant_card_state=accountant_card_state,
        accountant_cash_state=accountant_cash_state,
        teller_card_state=teller_card_state,
        teller_cash_state=teller_cash_state
    )

    try:
        add_bid(bid)
    except Exception as e:
        logging.getLogger("uvicorn.error").error(f"Added bid failed: {e}")

def get_bids_by_worker_telegram_id(id: str) -> list[BidShema]:
    '''
    Returns all bids own to worker with specified phone number.
    '''
    worker = find_worker_by_column(Worker.telegram_id, id)

    if not worker:
        return []
    
    return get_bids_by_worker(worker)

def get_pending_bids_by_worker_telegram_id(id: str) -> list[BidShema]:
    '''
    Returns all bids own to worker with specified phone number.
    '''
    worker = find_worker_by_column(Worker.telegram_id, id)

    if not worker:
        return []
    
    return get_pending_bids_by_worker(worker)

def get_bid_by_id(id: int) -> BidShema:
    '''
    Returns bid in database by it id.
    '''
    return find_bid_by_column(Bid.id, id)