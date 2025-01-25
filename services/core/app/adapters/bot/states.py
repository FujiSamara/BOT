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
    edm = State()
    activity_type = State()
    search = State()


class BidCoordination(StatesGroup):
    comment = State()
    paying_comment = State()
    department = State()
    search = State()


class CandidatesCoordination(StatesGroup):
    state = State()
    l_name = State()


class WorkerBidCreating(StatesGroup):
    f_name = State()
    l_name = State()
    o_name = State()
    post = State()
    department = State()
    birth_year = State()
    birth_month = State()
    birth_day = State()
    phone_number = State()
    worksheet = State()
    passport = State()
    work_permission = State()


class WorkerBidCoordination(StatesGroup):
    comment = State()


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
    photo_work = State()
    photo_rework = State()
    bid_id = State()


# Territorial manager IT
class TMForm(StatesGroup):
    department = State()
    mark = State()
    work_comment = State()


# Technical Request


class WorkerDepartmentRequestForm(StatesGroup):
    problem_group = State()
    problem_name = State()
    description = State()
    photo = State()
    department = State()


class ExecutorDepartmentRequestForm(StatesGroup):
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


class AppraiserRequestForm(StatesGroup):
    department = State()
    mark = State()
    description = State()


class DepartmentDirectorRequestForm(StatesGroup):
    department = State()
    executor = State()
    group = State()
    problem = State()
    description = State()


# Personal Cabinet form
class PersonalCabinet(StatesGroup):
    department = State()
    menu = State()
