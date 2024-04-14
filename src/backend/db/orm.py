from db.database import Base, engine, session
from db.models import *

def create_tables():
    Base.metadata.create_all(engine)


def find_user_by_telegram_id(id: int) -> Worker:
    '''Returns user if he exist, undefined otherwise.
    '''
    with session.begin() as s:
        return s.query(Worker).filter(Worker.telegram_id == id).first()

def find_user_by_number(number: str) -> Worker:
    '''Returns user if he exist, undefined otherwise.
    '''
    with session.begin() as s:
        return s.query(Worker).filter(Worker.phone_number == number).first()
