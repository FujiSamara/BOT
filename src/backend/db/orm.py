from typing import Any
from db.database import Base, engine, session
from db.models import *
from db.schemas import *
from sqlalchemy.sql.expression import func

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
    
def find_department_by_name(name: str) -> DepartmentShema:
    '''
    Finds and returns department by `name`.
    '''
    with session.begin() as s:
        department = s.query(Department).filter(Department.name == name).first()
        if department:
            return DepartmentShema.model_validate(department)
        else:
            return None

def get_last_bid_id() -> int:
    '''
    Returns last bid id in database.
    '''
    with session.begin() as s:
        return s.query(func.max(Bid.id)).first()[0]


def add_bid(bid: BidShema):
    '''
    Adds `bid` to database.
    '''
    with session.begin() as s:
        worker = s.query(Worker).filter(Worker.id == bid.worker.id).first()
        department = s.query(Department).filter(Department.id == bid.department.id).first()

        bid = Bid(
            amount=bid.amount,
            payment_type=bid.payment_type,
            purpose=bid.purpose,
            agreement=bid.agreement,
            urgently=bid.urgently,
            need_document=bid.need_document,
            comment=bid.comment,
            create_date=bid.create_date,
            department=department,
            worker=worker,
            document=bid.document,
            kru_state=bid.kru_state,
            owner_state=bid.owner_state,
            accountant_card_state=bid.accountant_card_state,
            accountant_cash_state=bid.accountant_cash_state,
            teller_card_state=bid.teller_card_state,
            teller_cash_state=bid.teller_cash_state
        )

        s.add(bid)

def get_bids_by_worker(worker: WorkerShema) -> list[BidShema]:
    '''
    Returns all bids in database by worker.
    '''
    with session.begin() as s:
        raw_bids = s.query(Bid).filter(Bid.worker_id == worker.id).all()
        return [BidShema.model_validate(raw_bid) for raw_bid in raw_bids]