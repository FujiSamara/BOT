from aiogram.fsm.state import StatesGroup, State


class Base(StatesGroup):
    none = State()
    bid = State()


class Auth(StatesGroup):
    authing = State()


# Bid
class BidCreating(StatesGroup):
    department = State()
    payment_amount = State()
    payment_purpose = State()
    agreement_existence = State()
    urgently = State()
    need_document = State()
    comment = State()
    document = State()


class BidCoordination(StatesGroup):
    comment = State()


# Rate
class RateForm(StatesGroup):
    rating = State()
    fine = State()
