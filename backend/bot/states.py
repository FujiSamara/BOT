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


# Bid IT
class BidITCreating(StatesGroup):
    department = State()
    problem = State()
    photo = State()
    comment = State()
    telegram_id = State()


# Repairman
class RepairmanBidForm(StatesGroup):
    department = State()
    photo = State()
    bid_id = State()


# Territorial manager IT
class TMForm(StatesGroup):
    department = State()
    mark = State()
    work_comment = State()


# Technical Request


class WorkerTechnicalRequestForm(StatesGroup):
    problem_name = State()
    description = State()
    photo = State()


class RepairmanTechnicalRequestForm(StatesGroup):
    department = State()
    photo_waiting = State()
    photo_rework = State()


class ChiefTechnicianTechnicalRequestForm(StatesGroup):
    department = State()
    executor = State()
    group = State()
    photo_waiting = State()
    photo_rework = State()
    description = State()


class TerritorialManagerRequestForm(StatesGroup):
    department = State()
    mark = State()
    description = State()


class DepartmentDirectorRequestForm(StatesGroup):
    department = State()
    executor = State()
    group = State()
    problem = State()
    description = State()
