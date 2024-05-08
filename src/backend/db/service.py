from io import BytesIO
from pathlib import Path
import db.orm as orm
from db.models import Department, ApprovalStatus, Bid, Post, Worker, Access, WorkTime
from db.schemas import BidSchema, WorkerSchema, WorkTimeSchema, DepartmentSchema
import logging
from datetime import datetime, date
from fastapi import UploadFile
from typing import Any, Optional
from settings import get_settings


def get_worker_level_by_telegram_id(id: str) -> int:
    """
    Returns worker access level by his telegram id.

    Return `-1`, if worker doesn't exits.
    """
    worker = orm.find_worker_by_column(Worker.telegram_id, id)
    if not worker:
        return -1

    return worker.post.level


def get_workers_by_level(level: int) -> list[WorkerSchema]:
    """
    Returns all workers in database with `level` at column.
    """
    return orm.get_workers_with_post_by_column(Post.level, level)


def get_worker_department_by_telegram_id(id: str) -> DepartmentSchema:
    """
    Returns worker department by his telegram id.

    If worker not exist return `None`.
    """
    worker = orm.find_worker_by_column(Worker.telegram_id, id)

    if not worker:
        return None

    return orm.find_department_by_column(Department.id, worker.department.id)


def update_worker_tg_id_by_number(number: str, tg_id: int) -> bool:
    """
    Finds worker by his phone number and sets him telegram id.

    Returns `True`, if worker found, `False` otherwise.
    """
    worker = orm.find_worker_by_column(Worker.phone_number, number)
    if not worker:
        return False

    worker.telegram_id = tg_id
    try:
        orm.update_worker(worker)
    except Exception as e:
        logging.getLogger("uvicorn.error").error(f"update_worker error: {e}")
        return False
    return True


def get_departments_names() -> list[str]:
    """
    Returns all existed departments.
    """
    departments_raw = orm.get_departments_columns(Department.name)
    result = [column[0] for column in departments_raw]
    return result


async def create_bid(
    amount: int,
    payment_type: str,
    department: str,
    purpose: str,
    telegram_id: int,
    file: BytesIO,
    filename: str,
    kru_state: ApprovalStatus,
    owner_state: ApprovalStatus,
    accountant_cash_state: ApprovalStatus,
    accountant_card_state: ApprovalStatus,
    teller_cash_state: ApprovalStatus,
    teller_card_state: ApprovalStatus,
    agreement: Optional[str] = None,
    urgently: Optional[str] = None,
    need_document: Optional[str] = None,
    comment: Optional[str] = None,
):
    """
    Creates an bid wrapped in `BidShema` and adds it to database.
    """
    department_inst = orm.find_department_by_column(Department.name, department)

    if not department_inst:
        logging.getLogger("uvicorn.error").error(
            f"Department with name '{department}' not found"
        )
        return

    worker_inst = orm.find_worker_by_column(Worker.telegram_id, telegram_id)

    if not worker_inst:
        logging.getLogger("uvicorn.error").error(
            f"Worker with telegram id '{telegram_id}' not found"
        )
        return

    cur_date = datetime.now()
    last_bid_id = orm.get_last_bid_id()
    if not last_bid_id:
        last_bid_id = 0

    suffix = Path(filename).suffix
    filename = f"document_bid_{last_bid_id + 1}{suffix}"

    bid = BidSchema(
        amount=amount,
        payment_type=payment_type,
        department=department_inst,
        worker=worker_inst,
        purpose=purpose,
        create_date=cur_date,
        agreement=agreement,
        urgently=urgently,
        need_document=need_document,
        comment=comment,
        document=UploadFile(file=file, filename=filename),
        kru_state=kru_state,
        owner_state=owner_state,
        accountant_card_state=accountant_card_state,
        accountant_cash_state=accountant_cash_state,
        teller_card_state=teller_card_state,
        teller_cash_state=teller_cash_state,
    )

    orm.add_bid(bid)
    from bot.handlers.utils import notify_workers_by_level

    await notify_workers_by_level(level=int(Access.kru), message="У вас новая заявка!")


def get_bids_by_worker_telegram_id(id: str) -> list[BidSchema]:
    """
    Returns all bids own to worker with specified phone number.
    """
    worker = orm.find_worker_by_column(Worker.telegram_id, id)

    if not worker:
        return []

    return orm.get_bids_by_worker(worker)


def get_pending_bids_by_worker_telegram_id(id: str) -> list[BidSchema]:
    """
    Returns all bids own to worker with specified phone number.
    """
    worker = orm.find_worker_by_column(Worker.telegram_id, id)

    if not worker:
        return []

    return orm.get_pending_bids_by_worker(worker)


def get_bid_by_id(id: int) -> BidSchema:
    """
    Returns bid in database by it id.
    """
    return orm.find_bid_by_column(Bid.id, id)


def get_pending_bids_by_column(column: Any) -> list[BidSchema]:
    """
    Returns all bids in database with pending approval state at column.
    """
    return orm.get_specified_pengind_bids(column)


def get_history_bids_by_column(column: Any) -> list[BidSchema]:
    """
    Returns all bids in database past through worker with `column`.
    """
    return orm.get_specified_history_bids(column)


async def update_bid_state(bid: BidSchema, state_name: str, state: ApprovalStatus):
    """
    Updates bid state with `state_name` by specified `state`.
    """
    from bot.handlers.utils import nottify_workers_by_access

    if state_name == "kru_state":
        if state == ApprovalStatus.approved:
            bid.kru_state = ApprovalStatus.approved
            if bid.owner_state == ApprovalStatus.skipped:
                if bid.accountant_cash_state == ApprovalStatus.skipped:
                    bid.accountant_card_state = ApprovalStatus.pending_approval
                else:
                    bid.accountant_cash_state = ApprovalStatus.pending_approval
            else:
                bid.owner_state = ApprovalStatus.pending_approval
        else:
            bid.kru_state = ApprovalStatus.denied
            bid.owner_state = ApprovalStatus.skipped
            bid.accountant_card_state = ApprovalStatus.skipped
            bid.accountant_cash_state = ApprovalStatus.skipped
            bid.teller_card_state = ApprovalStatus.skipped
            bid.teller_cash_state = ApprovalStatus.skipped
    elif state_name == "owner_state":
        if state == ApprovalStatus.approved:
            bid.owner_state = ApprovalStatus.approved
            if bid.accountant_cash_state == ApprovalStatus.skipped:
                bid.accountant_card_state = ApprovalStatus.pending_approval
            else:
                bid.accountant_cash_state = ApprovalStatus.pending_approval
        else:
            bid.owner_state = ApprovalStatus.denied
            bid.accountant_card_state = ApprovalStatus.skipped
            bid.accountant_cash_state = ApprovalStatus.skipped
            bid.teller_card_state = ApprovalStatus.skipped
            bid.teller_cash_state = ApprovalStatus.skipped
    elif state_name == "accountant_card_state":
        if state == ApprovalStatus.approved:
            bid.accountant_card_state = ApprovalStatus.approved
            bid.teller_card_state = ApprovalStatus.pending_approval
        else:
            bid.accountant_card_state = ApprovalStatus.denied
            bid.teller_card_state = ApprovalStatus.skipped
    elif state_name == "accountant_cash_state":
        if state == ApprovalStatus.approved:
            bid.accountant_cash_state = ApprovalStatus.approved
            bid.teller_cash_state = ApprovalStatus.pending_approval
        else:
            bid.accountant_cash_state = ApprovalStatus.denied
            bid.teller_cash_state = ApprovalStatus.skipped
    elif state_name == "teller_card_state":
        bid.teller_card_state = ApprovalStatus.approved
    else:
        bid.teller_cash_state = ApprovalStatus.approved

    if bid.owner_state == ApprovalStatus.pending_approval:
        await nottify_workers_by_access(
            access=Access.owner, message="У вас новая заявка!"
        )
    elif bid.accountant_card_state == ApprovalStatus.pending_approval:
        await nottify_workers_by_access(
            access=Access.accountant_card, message="У вас новая заявка!"
        )
    elif bid.accountant_cash_state == ApprovalStatus.pending_approval:
        await nottify_workers_by_access(
            access=Access.accountant_cash, message="У вас новая заявка!"
        )
    elif bid.teller_card_state == ApprovalStatus.pending_approval:
        await nottify_workers_by_access(
            access=Access.teller_card, message="У вас новая заявка!"
        )
    elif bid.teller_cash_state == ApprovalStatus.pending_approval:
        await nottify_workers_by_access(
            access=Access.teller_cash, message="У вас новая заявка!"
        )

    orm.update_bid(bid)


def get_work_time_records_by_day_and_department(
    department_id: int, day: date
) -> list[WorkTimeSchema]:
    """
    Returns all work times records in database by `department_id`
    and `day`.
    """

    return orm.get_work_time_records_by_columns(
        [WorkTime.department_id, WorkTime.day],
        [department_id, day.strftime(get_settings().date_format)],
    )


def get_worker_by_id(id: int) -> WorkerSchema:
    """
    Returns worker in database with `id` at column.

    If worker not exist return `None`.
    """
    return orm.find_worker_by_column(Worker.id, id)


def get_work_time_record_by_id(wid) -> WorkTimeSchema:
    """
    Return work time record in database by `id`.

    If record not exist return `None`.
    """

    return orm.find_work_time_record_by_columns(
        [WorkTime.id],
        [id],
    )


def update_work_time_record(record: WorkTimeSchema) -> None:
    """
    Updates work time record if it exists.
    """
    orm.update_work_time(record)
