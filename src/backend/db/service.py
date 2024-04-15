from db.orm import find_worker_by_number, find_worker_by_telegram_id, update_worker
from db.shemas import *
import logging

def get_user_level_by_tg_id(id: str) -> int:
    '''
    Returns user access level by his telegram id.

    Return `-1`, if user doesn't exits.
    '''
    # TODO: Completes calling orm.
    return -1

def get_user_role_by_tg_id(id: str) -> str:
    '''
    Return user role by his telegram id.

    Return role if user exist, `None` otherwise.
    '''
    pass

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
        logging.error(f"update_worker error: {e}")
        return False
    return True
