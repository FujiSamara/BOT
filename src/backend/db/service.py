from db.orm import (
    find_worker_by_number,
    find_worker_by_telegram_id,
    update_worker,
    get_departments_with_columns
)
from db.models import (
    Department
)
from db.shemas import *
import logging

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