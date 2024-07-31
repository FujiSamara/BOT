from aiogram.fsm.state import StatesGroup, State


class Base(StatesGroup):
    none = State()
    bid = State()


class Auth(StatesGroup):
    authing = State()


# Bid
class BidCreating(StatesGroup):
    department = State()
    expenditure_chapter = State()
    expenditure = State()
    payment_amount = State()
    payment_purpose = State()
    comment = State()
    documents = State()


class BidCoordination(StatesGroup):
    comment = State()


class WorkerBidCreating(StatesGroup):
    f_name = State()
    l_name = State()
    o_name = State()
    post = State()
    department = State()
    worksheet = State()
    passport = State()
    work_permission = State()


# Rate
class RateForm(StatesGroup):
    rating = State()
    fine = State()
