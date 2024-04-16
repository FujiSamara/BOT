from aiogram.fsm.state import StatesGroup, State

class Base(StatesGroup):
    none = State()

class Auth(StatesGroup):
    authing = State()

class BidCreating(StatesGroup):
    department = State()
    payment_amount = State()
    payment_purpose = State()
    agreement_existence = State()
    urgently = State()
    payment_system = State()
    comment = State()
