from pathlib import Path
from settings import get_settings
import db.orm as orm
from db.models import (
    BudgetRecord,
    Department,
    ApprovalStatus,
    Bid,
    Expenditure,
    FujiScope,
    Post,
    TechnicalRequest,
    Worker,
    WorkTime,
    WorkerBid,
)
from db.schemas import (
    BidRecordSchema,
    BidSchema,
    BudgetRecordSchema,
    ExpenditureSchema,
    TechnicalProblemSchema,
    TechnicalRequestSchema,
    WorkerSchema,
    WorkTimeSchema,
    DepartmentSchema,
    WorkerBidSchema,
    DocumentSchema,
    FileSchema,
)
import logging
from datetime import datetime, timedelta
from fastapi import UploadFile
from typing import Any, Optional


def get_worker_by_telegram_id(id: str) -> Optional[WorkerSchema]:
    """
    Returns worker by his telegram id.
    Return `None`, if worker doesn't exits.
    """
    return orm.find_worker_by_column(Worker.telegram_id, id)


def get_workers_by_scope(scope: FujiScope) -> list[WorkerSchema]:
    """
    Returns all workers in database by `scope`.
    """
    return orm.get_workers_with_scope(scope)


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


def get_worker_by_phone_number(number: str) -> WorkerSchema:
    """
    Finds worker by his phone number.
    """
    return orm.find_worker_by_column(Worker.phone_number, number)


async def create_bid(
    amount: int,
    payment_type: str,
    department: str,
    purpose: str,
    telegram_id: int,
    expenditure: str,
    files: list[UploadFile],
    fac_state: ApprovalStatus,
    cc_state: ApprovalStatus,
    cc_supervisor_state: ApprovalStatus,
    kru_state: ApprovalStatus,
    owner_state: ApprovalStatus,
    accountant_cash_state: ApprovalStatus,
    accountant_card_state: ApprovalStatus,
    teller_cash_state: ApprovalStatus,
    teller_card_state: ApprovalStatus,
    comment: Optional[str] = None,
):
    """
    Creates an bid wrapped in `BidSchema` and adds it to database.
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

    expenditure_inst = orm.find_expenditure_by_column(Expenditure.name, expenditure)

    if not expenditure_inst:
        logging.getLogger("uvicorn.error").error(
            f"Expenditure with name '{expenditure}' not found"
        )
        return

    cur_date = datetime.now()
    last_bid_id = orm.get_last_bid_id()
    if not last_bid_id:
        last_bid_id = 0

    documents = []
    for file in files:
        suffix = Path(file.filename).suffix
        filename = f"document_bid_{last_bid_id + 1}{suffix}"
        file.filename = filename
        documents.append(DocumentSchema(document=file))

    bid = BidSchema(
        amount=amount,
        payment_type=payment_type,
        department=department_inst,
        expenditure=expenditure_inst,
        worker=worker_inst,
        purpose=purpose,
        create_date=cur_date,
        close_date=None,
        comment=comment,
        denying_reason=None,
        documents=documents,
        fac_state=fac_state,
        cc_state=cc_state,
        cc_supervisor_state=cc_supervisor_state,
        kru_state=kru_state,
        owner_state=owner_state,
        accountant_card_state=accountant_card_state,
        accountant_cash_state=accountant_cash_state,
        teller_card_state=teller_card_state,
        teller_cash_state=teller_cash_state,
    )

    orm.add_bid(bid)


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
        notify_workers_by_scope,
        notify_worker_by_telegram_id,
    )

    match state_name:
        case "fac_state":
            bid.fac_state = state
            bid.cc_state = ApprovalStatus.pending_approval
            if state == ApprovalStatus.denied:
                bid.cc_state = ApprovalStatus.skipped
                bid.cc_supervisor_state = ApprovalStatus.skipped
                bid.kru_state = ApprovalStatus.skipped
                bid.owner_state = ApprovalStatus.skipped
                bid.accountant_card_state = ApprovalStatus.skipped
                bid.accountant_cash_state = ApprovalStatus.skipped
                bid.teller_card_state = ApprovalStatus.skipped
                bid.teller_cash_state = ApprovalStatus.skipped
        case "cc_state":
            bid.cc_state = state
            bid.cc_supervisor_state = ApprovalStatus.pending_approval
            if state == ApprovalStatus.denied:
                bid.cc_supervisor_state = ApprovalStatus.skipped
                bid.kru_state = ApprovalStatus.skipped
                bid.owner_state = ApprovalStatus.skipped
                bid.accountant_card_state = ApprovalStatus.skipped
                bid.accountant_cash_state = ApprovalStatus.skipped
                bid.teller_card_state = ApprovalStatus.skipped
                bid.teller_cash_state = ApprovalStatus.skipped
        case "cc_supervisor_state":
            bid.cc_supervisor_state = state
            bid.kru_state = ApprovalStatus.pending_approval
            if state == ApprovalStatus.denied:
                bid.kru_state = ApprovalStatus.skipped
                bid.owner_state = ApprovalStatus.skipped
                bid.accountant_card_state = ApprovalStatus.skipped
                bid.accountant_cash_state = ApprovalStatus.skipped
                bid.teller_card_state = ApprovalStatus.skipped
                bid.teller_cash_state = ApprovalStatus.skipped
        case "kru_state":
            bid.kru_state = state
            if bid.owner_state == ApprovalStatus.skipped:
                if bid.accountant_cash_state == ApprovalStatus.skipped:
                    bid.accountant_card_state = ApprovalStatus.pending_approval
                else:
                    bid.accountant_cash_state = ApprovalStatus.pending_approval
            else:
                bid.owner_state = ApprovalStatus.pending_approval
            if state == ApprovalStatus.denied:
                bid.owner_state = ApprovalStatus.skipped
                bid.accountant_card_state = ApprovalStatus.skipped
                bid.accountant_cash_state = ApprovalStatus.skipped
                bid.teller_card_state = ApprovalStatus.skipped
                bid.teller_cash_state = ApprovalStatus.skipped
        case "owner_state":
            bid.owner_state = state
            if bid.accountant_cash_state == ApprovalStatus.skipped:
                bid.accountant_card_state = ApprovalStatus.pending_approval
            else:
                bid.accountant_cash_state = ApprovalStatus.pending_approval
            if state == ApprovalStatus.denied:
                bid.accountant_card_state = ApprovalStatus.skipped
                bid.accountant_cash_state = ApprovalStatus.skipped
                bid.teller_card_state = ApprovalStatus.skipped
                bid.teller_cash_state = ApprovalStatus.skipped
        case "accountant_card_state":
            bid.accountant_card_state = state
            bid.teller_card_state = ApprovalStatus.pending_approval
            if state == ApprovalStatus.denied:
                bid.teller_card_state = ApprovalStatus.skipped
                bid.teller_cash_state = ApprovalStatus.skipped
        case "accountant_cash_state":
            bid.accountant_cash_state = state
            bid.teller_cash_state = ApprovalStatus.pending_approval
            if state == ApprovalStatus.denied:
                bid.teller_card_state = ApprovalStatus.skipped
                bid.teller_cash_state = ApprovalStatus.skipped
        case "teller_card_state":
            bid.teller_card_state = ApprovalStatus.approved
        case "teller_cash_state":
            bid.teller_cash_state = ApprovalStatus.approved

    if bid.kru_state == ApprovalStatus.pending_approval:
        await notify_workers_by_scope(
            scope=FujiScope.bot_bid_kru, message="У вас новая заявка!"
        )
    elif bid.owner_state == ApprovalStatus.pending_approval:
        await notify_workers_by_scope(
            scope=FujiScope.bot_bid_owner, message="У вас новая заявка!"
        )
    elif bid.accountant_card_state == ApprovalStatus.pending_approval:
        await notify_workers_by_scope(
            scope=FujiScope.bot_bid_accountant_card, message="У вас новая заявка!"
        )
    elif bid.accountant_cash_state == ApprovalStatus.pending_approval:
        await notify_workers_by_scope(
            scope=FujiScope.bot_bid_accountant_cash, message="У вас новая заявка!"
        )
    elif bid.teller_card_state == ApprovalStatus.pending_approval:
        await notify_workers_by_scope(
            scope=FujiScope.bot_bid_teller_card, message="У вас новая заявка!"
        )
    elif bid.teller_cash_state == ApprovalStatus.pending_approval:
        await notify_workers_by_scope(
            scope=FujiScope.bot_bid_teller_cash, message="У вас новая заявка!"
        )
    if state == ApprovalStatus.approved:
        stage = ""
        match state_name:
            case "fac_state":
                stage = "Ваша заявка согласована ЦФО!"
            case "cc_state":
                stage = "Ваша заявка согласована ЦЗ!"
            case "cc_supervisor_state":
                stage = "Ваша заявка согласована руководителем ЦЗ!"
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

    worksheet_insts: list[DocumentSchema] = []

    for index, doc in enumerate(worksheet):
        suffix = Path(doc.filename).suffix
        filename = f"worksheet_worker_bid_{last_bid_id + 1}_{index + 1}{suffix}"
        doc.filename = filename
        worksheet_inst = DocumentSchema(document=doc)
        worksheet_insts.append(worksheet_inst)

    passport_insts: list[DocumentSchema] = []

    for index, doc in enumerate(passport):
        suffix = Path(doc.filename).suffix
        filename = f"passport_worker_bid_{last_bid_id + 1}_{index + 1}{suffix}"
        doc.filename = filename
        passport_inst = DocumentSchema(document=doc)
        passport_insts.append(passport_inst)

    work_permission_insts: list[DocumentSchema] = []

    for index, doc in enumerate(work_permission):
        suffix = Path(doc.filename).suffix
        filename = f"work_permission_worker_bid_{last_bid_id + 1}_{index + 1}{suffix}"
        doc.filename = filename
        work_permission_inst = DocumentSchema(document=doc)
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


def get_file_data(file_path: str, mode: str = "sqladmin") -> FileSchema:
    """Returns file `FileSchema` with file href and name.
    - `mode`  Specifies file request source.
    """
    proto = "http"
    host = get_settings().domain
    port = get_settings().port
    if get_settings().ssl_certfile:
        proto = "https"

    filename = Path(file_path).name

    source: str = ""

    if mode == "sqladmin":
        source = "/admin"
    elif mode == "api":
        source = "/api"

    return FileSchema(
        name=filename, href=f"{proto}://{host}:{port}{source}/download?path={file_path}"
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

    from bot.handlers.utils import notify_worker_by_telegram_id, send_menu_by_scopes

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
    await send_menu_by_scopes(msg)


def get_expenditures() -> list[ExpenditureSchema]:
    """Returns all expenditures in database."""
    return orm.get_expenditures()


def create_expenditure(expenditure: ExpenditureSchema) -> None:
    """Creates expenditure"""
    if not orm.create_expenditure(expenditure):
        logging.getLogger("uvicorn.error").error("Expenditure wasn't created.")
    updated_expenditure = get_last_expenditure()
    budget_record = BudgetRecordSchema(
        expenditure=updated_expenditure,
        department=None,
        limit=None,
        last_update=None,
    )
    create_budget_record(budget_record)


def remove_expenditure(id: int) -> None:
    orm.remove_expenditure(id)


def update_expenditure(expenditure: ExpenditureSchema) -> None:
    """Updates expenditure by `ExpenditureSchema.id`"""
    if not orm.update_expenditure(expenditure):
        logging.getLogger("uvicorn.error").error("Expenditure wasn't updated.")


def get_expenditure_by_id(id: int) -> ExpenditureSchema:
    """Finds expenditure by this `id`."""
    return orm.find_expenditure_by_column(Expenditure.id, id)


def get_last_expenditure() -> ExpenditureSchema:
    """Returns last expenditure in db."""
    return orm.get_last_expenditrure()


def find_workers(record: str) -> list[WorkerSchema]:
    """Finds workers by given `record`.

    Search is carried out by f_name, l_name, o_name.
    """
    return orm.find_workers_by_name(record)


def get_budget_records() -> list[BudgetRecordSchema]:
    """Returns all budget records in database."""
    return orm.get_budget_records()


def create_budget_record(record: BudgetRecordSchema) -> None:
    """Creates budget record"""
    if not orm.create_budget_record(record):
        logging.getLogger("uvicorn.error").error("Budget record wasn't created.")


def remove_budget_record(id: int) -> None:
    orm.remove_budget_record(id)


def update_budget_record(record: BudgetRecordSchema) -> None:
    """Updates expenditure by `ExpenditureSchema.id`"""
    if not orm.update_budget_record(record):
        logging.getLogger("uvicorn.error").error("Budget record wasn't updated.")


def get_budget_record_by_id(id: int) -> BudgetRecordSchema:
    """Finds budget record by this `id`."""
    return orm.find_budget_record_by_column(BudgetRecord.id, id)


def get_last_budget_record() -> BudgetRecordSchema:
    """Returns last budget record in db."""
    return orm.get_last_budget_record()


def find_expenditures(record: str) -> list[WorkerSchema]:
    """Finds expenditures by given `record`.

    Search is carried out by name and chapter.
    """
    return orm.find_expenditures_by_name(record)


def find_department_by_name(record: str) -> list[DepartmentSchema]:
    """Finds departments by given `record`.

    Search is carried out by name.
    """
    return orm.find_departments_by_name(record)


def bid_to_bid_record(bid: BidSchema) -> BidRecordSchema:
    """Converts `BidSchema` to `BidRecordSchema`"""
    from bot.handlers.bids.utils import get_bid_state_info

    return BidRecordSchema(
        id=bid.id,
        amount=bid.amount,
        payment_type=bid.payment_type,
        department=bid.department,
        worker=bid.worker,
        close_date=bid.close_date,
        comment=bid.comment,
        create_date=bid.create_date,
        documents=[doc.document for doc in bid.documents],
        purpose=bid.purpose,
        status=get_bid_state_info(bid),
        denying_reason=bid.denying_reason,
        expenditure=bid.expenditure,
    )


def get_bid_records() -> list[BidRecordSchema]:
    """Returns all bid records in database."""
    return [bid_to_bid_record(bid) for bid in orm.get_bids()]


def get_fac_bid_records_by_fac_phone(phone: int) -> list[BidRecordSchema]:
    """Returns all fac bid records in database."""
    result = []

    for record in get_bid_records():
        if record.expenditure.fac.phone_number == phone:
            result.append(record)

    return result


def get_fac_bid_records_by_cc_phone(phone: int) -> list[BidRecordSchema]:
    """Returns all cc bid records in database."""
    result = []

    for record in get_bid_records():
        if record.expenditure.cc.phone_number == phone:
            result.append(record)

    return result


def get_fac_bid_records_by_cc_supervisor_phone(phone: int) -> list[BidRecordSchema]:
    """Returns all cc supervisor bid records in database."""
    result = []

    for record in get_bid_records():
        if record.expenditure.cc_supervisor.phone_number == phone:
            result.append(record)

    return result


def get_chapters() -> list[str]:
    """Returns list of all chapters in db"""
    expenditures = orm.get_expenditures()
    return [expenditure.chapter for expenditure in expenditures]


def get_expenditures_names() -> list[str]:
    """Returns list of all expenditure names in db"""
    expenditures = orm.get_expenditures()
    return [expenditure.name for expenditure in expenditures]


# region Technical request


def counting_date_sla(sla: int):
    deadline_date = datetime.now()
    start_work_day = 9
    end_work_day = 18

    if deadline_date.hour >= end_work_day:
        deadline_date = deadline_date.replace(hour=start_work_day + 1)
        deadline_date += timedelta(days=1)
    elif deadline_date.hour <= start_work_day:
        deadline_date = deadline_date.replace(hour=start_work_day + 1)

    weekday = deadline_date.weekday()
    if weekday > 4:  # 0 - понедельник, 6 - воскресенье
        deadline_date += timedelta(days=(7 - weekday))

    while sla > 8:
        deadline_date += timedelta(days=1)
        sla -= 9

        weekday = deadline_date.weekday()
        if weekday > 4:  # 0 - понедельник, 6 - воскресенье
            deadline_date += timedelta(days=(7 - weekday))

    deadline_date += timedelta(hours=sla)
    return deadline_date


def get_technical_problem_names() -> list[TechnicalProblemSchema]:
    return [problem.problem_name for problem in orm.get_technical_problems()]


def get_technical_problems() -> list[TechnicalProblemSchema]:
    return [problem for problem in orm.get_technical_problems()]


def get_technical_problem_by_name(problem_name) -> TechnicalProblemSchema:
    return orm.get_technical_problem_by_name(problem_name=problem_name)


def get_technical_problem_by_id(problem_id) -> TechnicalProblemSchema:
    return orm.get_technical_problem_by_id(problem_id=problem_id)


def create_technical_request(
    problem_name: str,
    description: str,
    photo_files: list[UploadFile],
    telegram_id: int,
) -> dict:
    """
    Create technical request
    Return: repairman telegram id
    """
    cur_date = datetime.now()

    last_technical_request_id = orm.get_last_technical_request_id()
    if not last_technical_request_id:
        last_technical_request_id = 0

    worker = orm.get_workers_with_post_by_column(Worker.telegram_id, telegram_id)[0]
    if not worker:
        logging.getLogger("uvicorn.error").error(
            f"Worker with telegram id {telegram_id} wasn't found"
        )

    problem = orm.get_technical_problem_by_problem_name(problem_name=problem_name)
    if not problem:
        logging.getLogger("uvicorn.error").error(
            f"Problem with name {problem_name} wasn't found"
        )

    repairman = orm.get_repairman_by_department_id_and_executor_type(
        department_id=worker.department.id, executor_type=problem.executor.name
    )

    if not repairman:
        logging.getLogger("uvicorn.error").error(
            f"Repairman from department id: {worker.department.id} and responsible by {problem.executor.name} wasn't found"
        )

    territorial_manager = orm.get_territorial_manager_by_department_id(
        worker.department.id
    )
    if not territorial_manager:
        logging.getLogger("uvicorn.error").error(
            f"Territorial manager with department id: {worker.department.id} wasn't found"
        )

    documents = []
    for index, doc in enumerate(photo_files):
        suffix = Path(doc.filename).suffix
        filename = f"photo_problem_technical_request_{last_technical_request_id + 1}_{index + 1}{suffix}"
        doc.filename = filename
        documents.append(DocumentSchema(document=doc))

    deadline_date = counting_date_sla(problem.sla)

    request = TechnicalRequestSchema(
        problem=problem,
        description=description,
        problem_photos=documents,
        state=ApprovalStatus.pending,
        open_date=cur_date,
        deadline_date=deadline_date,
        worker=worker,
        repairman=repairman,
        territorial_manager=territorial_manager,
        department=worker.department,
    )

    if not orm.create_technical_request(request):
        logging.getLogger("uvicorn.error").error(
            "Technical problem record wasn't created"
        )

    return {
        "repairman_telegram_id": repairman.telegram_id,
        "department_name": request.department.name,
    }


def update_technical_request_from_repairman(
    photo_files: list[UploadFile], request_id: int
) -> dict:
    """
    Update technical request
    Return territorial manager telegram id and department name on dictionary
    """
    cur_date = datetime.now()

    request = get_technical_request_by_id(request_id=request_id)

    if request.reopen_date:
        request.reopen_repair_date = cur_date
        for index, doc in enumerate(photo_files):
            suffix = Path(doc.filename).suffix
            filename = f"photo_repair_technical_request_{request_id}_reopen_{index + 1}{suffix}"
            doc.filename = filename
            request.repair_photos.append(DocumentSchema(document=doc))
    else:
        request.repair_date = cur_date

        documents = []
        for index, doc in enumerate(photo_files):
            suffix = Path(doc.filename).suffix
            filename = (
                f"photo_repair_technical_request_{request_id}_{index + 1}{suffix}"
            )
            doc.filename = filename
            documents.append(DocumentSchema(document=doc))

        request.repair_photos = documents

    request.state = ApprovalStatus.pending_approval

    if not orm.update_technical_request_from_repairman(request):
        logging.getLogger("uvicorn.error").error(
            f"Technical problem with id {request.id} record wasn't updated"
        )
    return_dict = {
        "territorial_manager_telegram_id": request.territorial_manager.telegram_id,
        "worker_telegram_id": request.worker.telegram_id,
        "department_name": request.department.name,
    }

    return return_dict


def update_technical_request_from_territorial_manager(
    mark: int, request_id: int, description: Optional[str]
) -> Optional[dict]:
    """
    Update technical request
    Return repairman telegram id if mark < 3 else None
    """
    cur_date = datetime.now()

    request = get_technical_request_by_id(request_id=request_id)

    request.score = mark

    if mark >= 3:
        request.state = ApprovalStatus.approved
        request.close_date = cur_date
        if request.reopen_date:
            request.reopen_confirmation_date = cur_date
        else:
            request.confirmation_date = cur_date
    else:
        if request.reopen_date:
            request.close_description = description
            request.state = ApprovalStatus.skipped
            request.close_date = cur_date
            request.reopen_confirmation_date = cur_date
        else:
            request.confirmation_description = description
            request.state = ApprovalStatus.pending
            request.confirmation_date = cur_date
            request.reopen_date = cur_date

            request.reopen_deadline_date = counting_date_sla(24)

    if not orm.update_technical_request_from_territorial_manager(request):
        logging.getLogger("uvicorn.error").error(
            f"Technical problem with id {request.id} record wasn't updated"
        )

    return {
        "repairman_telegram_id": request.repairman.telegram_id,
        "worker_telegram_id": request.worker.telegram_id,
        "department_name": request.department.name,
        "state": request.state,
    }


def update_tech_request_executor(
    request_id: int, repairman_full_name: list[str]
) -> int:
    """
    Update executor in technical request return telegram id
    """
    try:
        repairman = orm.get_workers_with_post_by_columns(
            [Worker.l_name, Worker.f_name, Worker.o_name], repairman_full_name
        )[0]
    except IndexError:
        logging.getLogger("uvicorn.error").error(
            f"Worker with full name: {repairman_full_name} wasn't found"
        )

    if not orm.update_tech_request_executor(
        request_id=request_id, repairman_id=repairman.id
    ):
        logging.getLogger("uvicorn.error").error(
            f"Technical request with id: {request_id} wasn't update executor"
        )
    return repairman.telegram_id


def update_technical_request_problem(request_id: int, problem_id: int):
    if not orm.update_technical_request_problem(
        request_id=request_id, problem_id=problem_id
    ):
        logging.getLogger("uvicorn.error").error(
            f"Technical request with id: {request_id} wasn't update problem"
        )


def get_all_waiting_technical_requests_for_worker(
    telegram_id: int,
) -> list[TechnicalRequestSchema]:
    """
    Return all technical requests by Telegram id
    """
    try:
        worker = orm.get_workers_with_post_by_column(Worker.telegram_id, telegram_id)[0]
    except IndexError:
        logging.getLogger("uvicorn.error").error(
            f"Worker with telegram id {telegram_id} wasn't found"
        )
    else:
        requests = orm.get_technical_requests_by_columns(
            [TechnicalRequest.worker_id, TechnicalRequest.close_date], [worker.id, None]
        )[:-16:-1]

    return requests


def get_all_waiting_technical_requests_for_repairman(
    telegram_id: int,
    department_name: str,
) -> list[TechnicalRequestSchema]:
    """
    Return all waiting technical requests by Telegram id for repairman
    """
    try:
        repairman = orm.get_workers_with_post_by_column(
            Worker.telegram_id, telegram_id
        )[0]
    except IndexError:
        logging.getLogger("uvicorn.error").error(
            f"Repairman with telegram id: {telegram_id} wasn't found"
        )
    else:
        try:
            department_id = (orm.find_departments_by_name(department_name)[0]).id
        except IndexError:
            logging.getLogger("uvicorn.error").error(
                f"Department with name: {department_name} wasn't found"
            )
        else:
            requests = orm.get_technical_requests_by_columns(
                [
                    TechnicalRequest.repairman_id,
                    TechnicalRequest.state,
                    TechnicalRequest.department_id,
                    TechnicalRequest.confirmation_date,
                ],
                [repairman.id, ApprovalStatus.pending, department_id, None],
            )[:-16:-1]

            return requests


def get_all_rework_technical_requests_for_repairman(
    telegram_id: int,
    department_name: str,
) -> list[TechnicalRequestSchema]:
    """
    Return all waiting technical requests by Telegram id for repairman
    """
    try:
        repairman = orm.get_workers_with_post_by_column(
            Worker.telegram_id, telegram_id
        )[0]
    except IndexError:
        logging.getLogger("uvicorn.error").error(
            f"Repairman with telegram id: {telegram_id} wasn't found"
        )
    else:
        try:
            department_id = (orm.find_departments_by_name(department_name)[0]).id
        except IndexError:
            logging.getLogger("uvicorn.error").error(
                f"Department with name: {department_name} wasn't found"
            )
        else:
            requests = orm.get_rework_tech_request(
                department_id=department_id, repairman_id=repairman.id
            )[:-16:-1]
            return requests


def get_all_waiting_technical_requests_for_territorial_manager(
    telegram_id: int,
    department_name: str,
) -> list[TechnicalRequestSchema]:
    """
    Return all waiting technical requests by Telegram id for territorial_manager
    """
    try:
        territorial_manager = orm.get_workers_with_post_by_column(
            Worker.telegram_id, telegram_id
        )[0]
    except IndexError:
        logging.getLogger("uvicorn.error").error(
            f"Territorial manager with telegram id: {telegram_id} wasn't found"
        )
    else:
        try:
            department_id = (orm.find_departments_by_name(department_name)[0]).id
        except IndexError:
            logging.getLogger("uvicorn.error").error(
                f"Department with name: {department_name} wasn't found"
            )
        else:
            requests = orm.get_technical_requests_by_columns(
                [
                    TechnicalRequest.territorial_manager_id,
                    TechnicalRequest.state,
                    TechnicalRequest.department_id,
                ],
                [
                    territorial_manager.id,
                    ApprovalStatus.pending_approval,
                    department_id,
                ],
            )[:-16:-1]

            return requests


def get_all_active_technical_requests_for_department_director(
    telegram_id: int,
    department_name: str,
) -> list[TechnicalRequestSchema]:
    """
    Return all waiting technical requests by Telegram id for department_director
    """
    try:
        department = orm.find_departments_by_name(department_name)[0]
    except IndexError:
        logging.getLogger("uvicorn.error").error(
            f"Department with name {department_name} wasn't found"
        )
    else:
        requests = orm.get_all_technical_requests_in_department(
            department_id=department.id,
            history_flag=False,
        )[:-16:-1]
        return requests


def get_all_history_technical_requests_for_repairman(
    telegram_id: int, department_name: str
) -> list[TechnicalRequestSchema]:
    """
    Return all history technical requests by Telegram id for repairman
    """
    try:
        repairman = orm.get_workers_with_post_by_column(
            Worker.telegram_id, telegram_id
        )[0]
    except IndexError:
        logging.getLogger("uvicorn.error").error(
            f"Repairman with telegram id: {telegram_id} wasn't found"
        )
    else:
        try:
            department_id = (orm.find_departments_by_name(department_name)[0]).id
        except IndexError:
            logging.getLogger("uvicorn.error").error(
                f"Department with name: {department_name} wasn't found"
            )
        else:
            requests = orm.get_technical_requests_for_repairman_history(
                repairman.id, department_id
            )[:-16:-1]

            return requests


def get_all_history_technical_requests_for_territorial_manager(
    telegram_id: int, department_name: str
) -> list[TechnicalRequestSchema]:
    """
    Return all history technical requests by Telegram id for territorial_manager
    """
    try:
        territorial_manager = orm.get_workers_with_post_by_column(
            Worker.telegram_id, telegram_id
        )[0]
    except IndexError:
        logging.getLogger("uvicorn.error").error(
            f"Territorial manager with telegram id: {telegram_id} wasn't found"
        )
    else:
        try:
            department_id = (orm.find_departments_by_name(department_name)[0]).id
        except IndexError:
            logging.getLogger("uvicorn.error").error(
                f"Department with name: {department_name} wasn't found"
            )
        else:
            requests = orm.get_technical_requests_by_columns(
                [
                    TechnicalRequest.territorial_manager_id,
                    TechnicalRequest.department_id,
                ],
                [territorial_manager.id, department_id],
                history=True,
            )[:-16:-1]

            return requests


def get_all_history_technical_requests_for_worker(
    telegram_id: int,
) -> list[TechnicalRequestSchema]:
    """
    Return history technical requests by Telegram id for worker
    """
    try:
        worker = orm.get_workers_with_post_by_column(Worker.telegram_id, telegram_id)[0]
    except IndexError:
        logging.getLogger("uvicorn.error").error(
            f"Worker with telegram id: {telegram_id} wasn't found"
        )
    else:
        requests = orm.get_technical_requests_by_columns(
            [TechnicalRequest.worker_id], [worker.id], history=True
        )[:-16:-1]

        return requests


def get_all_history_technical_requests_for_department_director(
    department_name: str,
) -> list[TechnicalRequestSchema]:
    """
    Return history technical requests by Telegram id for worker
    """
    try:
        department = orm.find_departments_by_name(department_name)[0]
    except IndexError:
        logging.getLogger("uvicorn.error").error(
            f"Department with name {department_name} wasn't found"
        )
    else:
        requests = orm.get_all_technical_requests_in_department(
            department_id=department.id,
            history_flag=True,
        )[:-16:-1]

        return requests


def get_technical_request_by_id(request_id: int) -> TechnicalRequestSchema:
    """
    Return TechnicalRequestSchema by id
    """
    try:
        request = orm.get_technical_requests_by_column(TechnicalRequest.id, request_id)[
            0
        ]
        return request
    except IndexError:
        logging.getLogger("uvicorn.error").error(
            f"Request with id: {request_id} wasn't founds"
        )


def _get_departments_for_employee(
    telegram_id: int, worker_column: Any
) -> list[DepartmentSchema]:
    """
    Return departments by worker telegram id and worker column id
    """
    try:
        worker = orm.get_workers_with_post_by_column(Worker.telegram_id, telegram_id)[0]
    except IndexError:
        logging.getLogger("uvicorn.error").error(
            f"Worker with telegram id: {telegram_id} wasn't found"
        )
    else:
        departments = orm.get_departments_by_worker_id_and_worker_column(
            worker_column=worker_column, worker_id=worker.id
        )
        return departments


def get_departments_for_repairman(
    telegram_id: int,
) -> list[DepartmentSchema]:
    departments = _get_departments_for_employee(
        telegram_id=telegram_id, worker_column=Department.chief_technician_id
    )
    if len(departments) > 0:
        return departments

    departments = _get_departments_for_employee(
        telegram_id=telegram_id, worker_column=Department.technician_id
    )
    if len(departments) > 0:
        return departments

    return _get_departments_for_employee(
        telegram_id=telegram_id, worker_column=Department.electrician_id
    )


def get_departments_for_territorial_manager(
    telegram_id: int,
) -> list[DepartmentSchema]:
    return _get_departments_for_employee(
        telegram_id=telegram_id, worker_column=Department.territorial_manager_id
    )


def get_all_departments(
    telegram_id: int,
) -> list[DepartmentSchema]:
    departments = orm.get_all_department()
    return departments


def get_all_active_requests_in_department_for_chief_technician(
    department_name: str,
) -> list[TechnicalRequestSchema]:
    """
    Return all request in department
    """
    try:
        department_id = (orm.find_departments_by_name(department_name)[0]).id
    except IndexError:
        logging.getLogger("uvicorn.error").error(
            f"Department with name: {department_name} wasn't found"
        )
    else:
        requests = orm.get_all_active_requests_in_department(department_id)[:-16:-1]
        return requests


def get_all_repairmans_in_department(
    department_name: str,
) -> list[WorkerSchema]:
    """
    Return all request in department
    """
    repairmans = orm.get_all_repairmans_in_department(department_name)
    if len(repairmans) == 0:
        logging.getLogger("uvicorn.error").error(
            f"Repairmans in department with name: {department_name} wasn't founds"
        )
    return repairmans


# endregion
