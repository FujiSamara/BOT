from typing import Any
from db.database import Base, engine, session
from db.models import *
from db.schemas import *
from sqlalchemy.sql.expression import func
from sqlalchemy import or_, and_

def create_tables():
    Base.metadata.create_all(engine)

def find_worker_by_column(column: any, value: any) -> WorkerShema:
    '''
    Returns worker in database by `column` with `value`.
    If worker not exist return `None`.
    '''
    with session.begin() as s:
        raw_worker = s.query(Worker).filter(column == value).first()
        if not raw_worker:
            return None
        return WorkerShema.model_validate(raw_worker)
    
def find_department_by_column(column: any, value: any) -> DepartmentShema:
    '''
    Returns department in database by `column` with `value`.
    If department not exist return `None`.
    '''
    with session.begin() as s:
        raw_deparment = s.query(Department).filter(column == value).first()
        if not raw_deparment:
            return None
        return DepartmentShema.model_validate(raw_deparment)
    
def find_bid_by_column(column: any, value: any) -> BidShema:
    '''
    Returns bid in database by `column` with `value`.
    If bid not exist return `None`.
    '''
    with session.begin() as s:
        raw_bid = s.query(Bid).filter(column == value).first()
        if not raw_bid:
            return None
        return BidShema.model_validate(raw_bid)

    
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

def get_departments_columns(*columns: list[Any]) -> list[DepartmentShema]:
    '''
    Returns specified columns of all existed departments.
    '''
    with session.begin() as s:
        return s.query(Department).with_entities(*columns).all()
    
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

def get_pending_bids_by_worker(worker: WorkerShema) -> list[BidShema]:
    '''
    Returns all bids in database by worker.
    '''
    with session.begin() as s:
        raw_bids = s.query(Bid).filter(
            and_(
                Bid.worker_id == worker.id,
                or_(
                    Bid.accountant_card_state == ApprovalState.pending_approval,
                    Bid.accountant_cash_state == ApprovalState.pending_approval,
                    Bid.teller_card_state == ApprovalState.pending_approval,
                    Bid.teller_cash_state == ApprovalState.pending_approval,
                    Bid.kru_state == ApprovalState.pending_approval,
                    Bid.owner_state == ApprovalState.pending_approval,
                )
            )
        ).all()
        return [BidShema.model_validate(raw_bid) for raw_bid in raw_bids]
    
def get_specified_pengind_bids(pending_column) -> list[BidShema]:
    '''
    Returns all bids in database with pending approval state in `pending_column`.
    '''
    with session.begin() as s:
        raw_bids = s.query(Bid).filter(pending_column == ApprovalState.pending_approval).all()
        return [BidShema.model_validate(raw_bid) for raw_bid in raw_bids]
    
def get_specified_history_bids(pending_column) -> list[BidShema]:
    '''
    Returns all bids in database with approval or denied state in `pending_column`.
    '''
    with session.begin() as s:
        raw_bids = s.query(Bid).filter(or_(
                pending_column == ApprovalState.denied,
                pending_column == ApprovalState.approved
            )).all()
        return [BidShema.model_validate(raw_bid) for raw_bid in raw_bids]

def update_bid(bid: BidShema):
    '''Updates bid by it id.
    '''
    with session.begin() as s:
        cur_bid = s.query(Bid).filter(Bid.id == bid.id).first()
        if not cur_bid:
            return None
        
        new_worker = s.query(Worker).filter(Worker.id == bid.worker.id).first()
        if not new_worker:
            return None
        
        new_department = s.query(Department).filter(Department.id == bid.department.id).first()
        if not new_worker:
            return None

        cur_bid.amount = bid.amount
        cur_bid.payment_type = bid.payment_type
        cur_bid.purpose = bid.purpose
        cur_bid.agreement = bid.agreement
        cur_bid.urgently = bid.urgently
        cur_bid.need_document = bid.need_document
        cur_bid.comment = bid.comment
        cur_bid.create_date = bid.create_date
        cur_bid.department = new_department
        cur_bid.worker = new_worker
        cur_bid.document = bid.document
        cur_bid.kru_state = bid.kru_state
        cur_bid.owner_state = bid.owner_state
        cur_bid.accountant_card_state = bid.accountant_card_state
        cur_bid.accountant_cash_state = bid.accountant_cash_state
        cur_bid.teller_card_state = bid.teller_card_state
        cur_bid.teller_cash_state = bid.teller_cash_state