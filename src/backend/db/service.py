from pathlib import Path
from settings import get_settings
import db.orm as orm
from db.models import (
    Department,
    ApprovalStatus,
    Bid,
    Expenditure,
    Post,
    Worker,
    Access,
    WorkTime,
    WorkerBid,
)
from db.schemas import (
    BidSchema,
    ExpenditureSchema,
    WorkerSchema,
    WorkTimeSchema,
    DepartmentSchema,
    WorkerBidSchema,
    WorkerBidPassportSchema,
    WorkerBidWorksheetSchema,
    WorkerBidWorkPermissionSchema,
    FileSchema,
)
import logging
from datetime import datetime
from fastapi import UploadFile
from typing import Any, Optional


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
    Returns all existed departments names.
    """
    departments_raw = orm.get_departments_columns(Department.name)
    result = [column[0] for column in departments_raw]
    return result


def get_departments_ids() -> list[int]:
    """
    Returns all existed departments ids.
    """
    departments_raw = orm.get_departments_columns(Department.id)
    result = [column[0] for column in departments_raw]
    return result


async def create_bid(
    amount: int,
    payment_type: str,
    department: str,
    purpose: str,
    telegram_id: int,
    file: UploadFile,
    file1: Optional[UploadFile],
    file2: Optional[UploadFile],
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

    if file:
        suffix = Path(file.filename).suffix
        filename = f"document_bid_{last_bid_id + 1}{suffix}"
        file.filename = filename
    if file1:
        suffix = Path(file1.filename).suffix
        filename = f"document_bid_{last_bid_id + 1}_1{suffix}"
        file1.filename = filename
    if file2:
        suffix = Path(file2.filename).suffix
        filename = f"document_bid_{last_bid_id + 1}_2{suffix}"
        file2.filename = filename

    bid = BidSchema(
        amount=amount,
        payment_type=payment_type,
        department=department_inst,
        worker=worker_inst,
        purpose=purpose,
        create_date=cur_date,
        close_date=None,
        agreement=agreement,
        urgently=urgently,
        need_document=need_document,
        comment=comment,
        denying_reason=None,
        document=file,
        document1=file1,
        document2=file2,
        kru_state=kru_state,
        owner_state=owner_state,
        accountant_card_state=accountant_card_state,
        accountant_cash_state=accountant_cash_state,
        teller_card_state=teller_card_state,
        teller_cash_state=teller_cash_state,
    )

    orm.add_bid(bid)
    from bot.handlers.utils import notify_workers_by_access

    await notify_workers_by_access(access=Access.kru, message="У вас новая заявка!")


def get_bids_by_worker_telegram_id(id: str) -> list[BidSchema]:
    """
    Returns all bids own to worker with specified telegram id.
    """
    worker = orm.find_worker_by_column(Worker.telegram_id, id)

    if not worker:
        return []

    return orm.get_bids_by_worker(worker)


def get_workers_bids_by_sender_telegram_id(id: str) -> list[BidSchema]:
    """
    Returns all workers bids own to sender with specified telegram id.
    """
    sender = orm.find_worker_by_column(Worker.telegram_id, id)

    if not sender:
        return []

    return orm.get_workers_bids_by_sender(sender)


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


def get_worker_bid_by_id(id: int) -> WorkerBidSchema:
    """
    Returns worker bid in database by it id.
    """
    return orm.find_worker_bid_by_column(WorkerBid.id, id)


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
    from bot.handlers.utils import (
        notify_workers_by_access,
        notify_worker_by_telegram_id,
    )

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
        await notify_workers_by_access(
            access=Access.owner, message="У вас новая заявка!"
        )
    elif bid.accountant_card_state == ApprovalStatus.pending_approval:
        await notify_workers_by_access(
            access=Access.accountant_card, message="У вас новая заявка!"
        )
    elif bid.accountant_cash_state == ApprovalStatus.pending_approval:
        await notify_workers_by_access(
            access=Access.accountant_cash, message="У вас новая заявка!"
        )
    elif bid.teller_card_state == ApprovalStatus.pending_approval:
        await notify_workers_by_access(
            access=Access.teller_card, message="У вас новая заявка!"
        )
    elif bid.teller_cash_state == ApprovalStatus.pending_approval:
        await notify_workers_by_access(
            access=Access.teller_cash, message="У вас новая заявка!"
        )
    if state == ApprovalStatus.approved:
        stage = ""
        match state_name:
            case "kru_state":
                stage = "Ваша заявка согласована КРУ!"
            case "owner_state":
                stage = "Ваша заявка согласована собственником!"
            case "accountant_card_state":
                stage = "Ваша заявка согласована бухгалтерией!"
            case "accountant_cash_state":
                stage = "Денежные средства по вашей заявке готовы к выдачи!"
            case "teller_card_state":
                stage = "Денежные средства выданы."
            case "teller_cash_state":
                stage = "Денежные средства выданы."
            case _:
                stage = "Ваша заявка принята!"
        await notify_worker_by_telegram_id(
            bid.worker.telegram_id, f"{stage}\nНомер заявки: {bid.id}."
        )
        bid.close_date = datetime.now()
    elif state == ApprovalStatus.denied:
        await notify_worker_by_telegram_id(
            bid.worker.telegram_id,
            "Ваша заявка отклонена!\nПричина: " + bid.denying_reason,
        )
        bid.close_date = datetime.now()

    orm.update_bid(bid)


def update_bid(bid: BidSchema):
    """Updated bid in database by `bid`"""
    orm.update_bid(bid)


def get_work_time_records_by_day_and_department(
    department_id: int, day: str
) -> list[WorkTimeSchema]:
    """
    Returns all work times records in database by `department_id`
    and `day`.
    """

    return orm.get_work_time_records_by_columns(
        [WorkTime.department_id, WorkTime.day],
        [department_id, day],
    )


def get_worker_by_id(id: int) -> WorkerSchema:
    """
    Returns worker in database with `id` at column.

    If worker not exist return `None`.
    """
    return orm.find_worker_by_column(Worker.id, id)


def get_work_time_record_by_id(id: int) -> WorkTimeSchema:
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


def get_chef_by_department_id(id: int) -> WorkerSchema:
    """
    Return first owner in database by owner department`id`.

    If record not exist returns `None`.
    """
    chef_level = 6

    owners = orm.get_workers_with_post_by_columns(
        [Worker.department_id, Post.level], [id, chef_level]
    )
    if len(owners) > 0:
        return owners[0]


def get_posts_names() -> list[str]:
    """Returns all posts names in db."""
    return [post.name for post in orm.get_posts()]


def create_worker_bid(
    f_name: str,
    l_name: str,
    o_name: str,
    post_name: str,
    department_name: str,
    worksheet: list[UploadFile],
    passport: list[UploadFile],
    work_permission: list[UploadFile],
    sender_telegram_id: str,
):
    """Creates worker bid"""
    department = orm.find_department_by_column(Department.name, department_name)
    if not department:
        logging.getLogger("uvicorn.error").error(
            f"Department with name '{department_name}' not found"
        )
        return

    post = orm.find_post_by_column(Post.name, post_name)
    if not post:
        logging.getLogger("uvicorn.error").error(
            f"Post with name '{post_name}' not found"
        )
        return

    sender = orm.find_worker_by_column(Worker.telegram_id, sender_telegram_id)
    if not sender:
        logging.getLogger("uvicorn.error").error(
            f"Sender with telegram id '{sender_telegram_id}' not found"
        )
        return

    last_bid_id = orm.get_last_worker_bid_id()
    if not last_bid_id:
        last_bid_id = 0

    worksheet_insts: list[WorkerBidWorksheetSchema] = []

    for index, doc in enumerate(worksheet):
        suffix = Path(doc.filename).suffix
        filename = f"worksheet_worker_bid_{last_bid_id + 1}_{index + 1}{suffix}"
        doc.filename = filename
        worksheet_inst = WorkerBidWorksheetSchema(document=doc)
        worksheet_insts.append(worksheet_inst)

    passport_insts: list[WorkerBidPassportSchema] = []

    for index, doc in enumerate(passport):
        suffix = Path(doc.filename).suffix
        filename = f"passport_worker_bid_{last_bid_id + 1}_{index + 1}{suffix}"
        doc.filename = filename
        passport_inst = WorkerBidPassportSchema(document=doc)
        passport_insts.append(passport_inst)

    work_permission_insts: list[WorkerBidWorkPermissionSchema] = []

    for index, doc in enumerate(work_permission):
        suffix = Path(doc.filename).suffix
        filename = f"work_permission_worker_bid_{last_bid_id + 1}_{index + 1}{suffix}"
        doc.filename = filename
        work_permission_inst = WorkerBidWorkPermissionSchema(document=doc)
        work_permission_insts.append(work_permission_inst)

    worker_bid = WorkerBidSchema(
        f_name=f_name,
        l_name=l_name,
        o_name=o_name,
        post=post,
        department=department,
        worksheet=worksheet_insts,
        passport=passport_insts,
        work_permission=work_permission_insts,
        create_date=datetime.now(),
        state=ApprovalStatus.pending_approval,
        sender=sender,
        comment=None,
    )

    orm.add_worker_bid(worker_bid)


def get_file_data(file_path: str) -> FileSchema:
    """Returns file `FileSchema` with file href and name."""
    proto = "http"
    host = get_settings().domain
    port = get_settings().port
    if get_settings().ssl_certfile:
        proto = "https"

    filename = Path(file_path).name

    return FileSchema(
        name=filename, href=f"{proto}://{host}:{port}/admin/download?path={file_path}"
    )


async def update_worker_bid_state(state: ApprovalStatus, bid_id):
    """
    Updates worker bid state to specified `state` by `bid_id` if bid exist.
    """
    worker_bid = orm.find_worker_bid_by_column(WorkerBid.id, bid_id)
    if not worker_bid.comment:
        return

    if not worker_bid:
        return

    worker_bid.state = state
    orm.update_worker_bid(worker_bid)

    from bot.handlers.utils import notify_worker_by_telegram_id, send_menu_by_level

    worker = get_worker_by_id(worker_bid.sender.id)
    if not worker:
        return
    msg = None
    if state == ApprovalStatus.approved:
        msg = await notify_worker_by_telegram_id(
            worker.telegram_id, f"Кандидат согласован!\nНомер заявки: {worker_bid.id}."
        )
    elif state == ApprovalStatus.denied:
        msg = await notify_worker_by_telegram_id(
            worker.telegram_id,
            f"Кандидат не согласован!\n{worker_bid.comment}\nНомер заявки: {worker_bid.id}.",
        )
    await send_menu_by_level(msg)


def get_expenditures() -> list[ExpenditureSchema]:
    """Returns all expenditures in database."""
    return orm.get_expenditures()


def create_expenditure(expenditure: ExpenditureSchema) -> None:
    """Creates expenditure"""
    if not orm.create_expenditure(expenditure):
        logging.getLogger("uvicorn.error").error("Expenditure wasn't created.")


def remove_expenditure(id: int) -> None:
    orm.remove_expenditure(id)


def update_expenditure(expenditure: ExpenditureSchema) -> None:
    """Updates expenditure by `ExpenditureSchema.id`"""
    if not orm.update_expenditure(expenditure):
        logging.getLogger("uvicorn.error").error("Expenditure wasn't updated.")


def get_expenditure_by_id(id: int) -> ExpenditureSchema:
    """Finds expenditure by this `id`."""
    return orm.find_expenditure_by_column(Expenditure.id, id)


def find_workers(record: str) -> list[WorkerSchema]:
    """Finds workers by given `record`.

    Search is carried out by f_name, l_name, o_name.
    """
    return orm.find_workers_by_name(record)
