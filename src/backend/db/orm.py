from typing import Any
from db.database import Base, engine, session
from db.models import *
from db.shemas import *

def create_tables():
    Base.metadata.create_all(engine)


def find_worker_by_telegram_id(id: int) -> WorkerShema:
    '''Returns user if he exist, `None` otherwise.
    '''
    with session.begin() as s:
        worker = s.query(Worker).filter(Worker.telegram_id == id).first()
        if worker:
            return WorkerShema.model_validate(worker)
        return None

def find_worker_by_number(number: str) -> WorkerShema:
    '''Returns user if he exist, `None` otherwise.
    '''
    with session.begin() as s:
        worker = s.query(Worker).filter(Worker.phone_number == number).first()
        if worker:
            return WorkerShema.model_validate(worker)
        return None

def update_worker(worker: WorkerShema):
    '''Updates worker by his id.
    '''
    with session.begin() as s:
        cur_worker = s.query(Worker).filter(Worker.id == worker.id).first()
        if not cur_worker:
            return None
        cur_worker.b_date = worker.b_date
        cur_worker.f_name = worker.f_name
        cur_worker.l_name = worker.l_name
        cur_worker.o_name = worker.o_name
        cur_worker.phone_number = worker.phone_number
        cur_worker.telegram_id = worker.telegram_id

def get_departments_with_columns(*columns: list[Any]) -> list[DepartmentShema]:
    '''
    Returns all existed departments with specified columns.
    '''
    with session.begin() as s:
        return s.query(Department).with_entities(*columns).all()