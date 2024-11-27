from pathlib import Path
from datetime import datetime
from fastapi import UploadFile

from app.infra.logging import logger

from app.services.extra import (
    find_department_by_name,
    get_worker_by_telegram_id,
    get_worker_department_by_telegram_id,
)
import app.database.orm as orm
from app.database.models import (
    Department,
    ApprovalStatus,
    Worker,
    ProblemIT,
    BidIT,
)
from app.database.schemas import (
    DocumentSchema,
    ProblemITSchema,
    BidITSchema,
)


def get_problems_it_types() -> list[str]:
    """
    Returns all existed IT problems types.
    """
    problems: list[ProblemITSchema] = orm.get_problems_it_columns()
    return [problem.name for problem in problems]


def get_problems_it_schema() -> list[ProblemITSchema]:
    """
    Returns all existed IT problems types with ids.
    """
    return orm.get_problems_it_columns()


def get_history_bids_it_by_worker_telegram_id(id: str) -> list[BidITSchema]:
    """
    Returns history bids IT own to worker with specified telegram id.
    """
    worker = orm.find_worker_by_column(Worker.telegram_id, id)

    if not worker:
        return []

    return orm.get_history_bids_it_for_worker(worker)


def get_bid_it_by_id(id: int) -> BidITSchema:
    """
    Returns bid IT in database by it id.
    """
    return orm.find_bid_it_by_column(BidIT.id, id)


def create_bid_it(
    problem_id: str,
    comment: str,
    files: list[UploadFile],
    telegram_id: int,
):
    """
    Creates an bid IT wrapped in `BidITShema` and adds it to database.
    """

    cur_date = datetime.now()
    problem_inst = orm.find_problem_it_by_id(ProblemIT.id, problem_id)
    worker_inst = orm.find_worker_by_column(Worker.telegram_id, telegram_id)

    if not worker_inst:
        logger.error(f"Worker with telegram id '{telegram_id}' not found")
        return

    department = get_worker_department_by_telegram_id(telegram_id)
    department_inst = orm.find_department_by_column(Department.name, department.name)

    if not department_inst:
        logger.error(f"Department with name '{department}' not found")
        return

    last_bid_it_id = orm.get_last_bid_it_id()
    if not last_bid_it_id:
        last_bid_it_id = 0

    documents = []

    for index, file in enumerate(files):
        suffix = Path(file.filename).suffix
        filename = f"document_bid_IT_worker{last_bid_it_id}_{index + 1}{suffix}"
        file.filename = filename
        documents.append(DocumentSchema(document=file))

    bid_it = BidITSchema(
        problem=problem_inst,
        problem_comment=comment,
        problem_photos=documents,
        worker=worker_inst,
        department=department_inst,
        opening_date=cur_date,
        status=ApprovalStatus.pending,
    )

    orm.add_bid_it(bid_it)


def get_pending_bids_it_by_worker_telegram_id(id: int) -> list[BidITSchema]:
    """
    Returns pending bids IT own to worker with specified telegram id.
    """
    worker = orm.find_worker_by_column(Worker.telegram_id, id)

    if not worker:
        return []

    return orm.get_pending_bids_it_by_worker(worker)


def get_departments_names_by_repairman_telegram_id(telegram_id: int) -> list[str]:
    """
    Returns departments names for repairman by id.
    """
    repairman = get_worker_by_telegram_id(telegram_id)
    departments_raw = orm.find_departments_by_column(
        Department.it_repairman_id, repairman.id
    )
    result = [department.name for department in departments_raw]
    return result


def update_bid_it_rm(bid_id: int, files: UploadFile):
    """
    Updates an bid IT wrapped in `BidITShema` and adds it to database.
    """

    bid = orm.get_bid_it_by_id(bid_id)

    cur_date = datetime.now()

    part = ""
    if bid.reopening_date:
        bid.reopen_done_date = cur_date
        part = "_reopen_"
    else:
        bid.done_date = cur_date

    documents = []
    for index, file in enumerate(files):
        suffix = Path(file.filename).suffix
        filename = f"document_bid_IT_repairman{part}{bid_id}_{index + 1}{suffix}"
        file.filename = filename
        documents.append(DocumentSchema(document=file))

    bid.work_photos = documents
    bid.status = ApprovalStatus.pending_approval

    orm.update_bid_it_rm(bid)


def get_departments_names_by_tm_telegram_id(telegram_id: int) -> list[str]:
    """
    Returns departments names for TM by telegram id.
    """
    tm = get_worker_by_telegram_id(telegram_id)
    departments_raw = orm.find_departments_by_column(
        Department.territorial_manager_id, tm.id
    )
    result = [department.name for department in departments_raw]
    return result


def update_bid_it_tm(bid_id: int, mark: int, work_comment: str | None):
    """
    Updates an bid IT wrapped in `BidITShema` and adds it to database.
    """

    bid = orm.get_bid_it_by_id(bid_id)

    cur_date = datetime.now()
    bid.mark = mark
    bid.approve_date = cur_date

    if bid.reopening_date:
        if mark in range(1, 3):
            bid.status = ApprovalStatus.skipped
            bid.reopen_work_comment = work_comment
            bid.reopen_approve_date = cur_date
            bid.close_date = cur_date
        else:
            bid.status = ApprovalStatus.approved
            bid.reopen_approve_date = cur_date
            bid.close_date = cur_date
    else:
        if mark in range(1, 3):
            bid.reopening_date = cur_date
            bid.work_comment = work_comment
            bid.status = ApprovalStatus.denied
        else:
            bid.status = ApprovalStatus.approved
            bid.close_date = cur_date

    orm.update_bid_it_tm(bid)


def get_pending_bids_it_by_repairman(
    telegram_id: str, department_name: str
) -> list[BidITSchema]:
    """
    Returns all pending bids IT own to worker with specified telegram id.
    """
    worker = orm.find_worker_by_column(Worker.telegram_id, telegram_id)

    if not worker:
        return []

    department_list = find_department_by_name(department_name)
    if len(department_list) == 0:
        return None

    department = department_list[0]

    bids = orm.get_bids_it_by_repairman_with_status(
        worker, department, ApprovalStatus.pending
    )

    return bids


def get_denied_bids_it_by_repairman(
    telegram_id: str, department_name: str
) -> list[BidITSchema]:
    """
    Returns all denied bids IT own to worker with specified telegram id.
    """
    worker = orm.find_worker_by_column(Worker.telegram_id, telegram_id)

    if not worker:
        return []

    department_list = find_department_by_name(department_name)
    if len(department_list) == 0:
        return None

    department = department_list[0]

    bids = orm.get_bids_it_by_repairman_with_status(
        worker, department, ApprovalStatus.denied
    )

    return bids


def get_history_bids_it_by_repairman(
    telegram_id: str, department_name: str
) -> list[BidITSchema]:
    """
    Returns all history bids IT own to repairman with specified telegram id.
    """
    repairman = orm.find_worker_by_column(Worker.telegram_id, telegram_id)

    if not repairman:
        return []

    department_list = find_department_by_name(department_name)
    if len(department_list) == 0:
        return None

    department = department_list[0]

    bids = orm.get_history_bids_it_for_repairman(repairman, department)

    return bids


def get_pending_bids_it_for_territorial_manager(
    telegram_id: str, department_name: str
) -> list[BidITSchema]:
    """
    Returns all pending bids IT own to territorial manager with specified telegram id.
    """
    tm = orm.find_worker_by_column(Worker.telegram_id, telegram_id)

    if not tm:
        return []

    department_list = find_department_by_name(department_name)
    if len(department_list) == 0:
        return None

    department = department_list[0]

    bids = orm.get_pending_bids_it_for_territorial_manager(tm, department)

    return bids


def get_history_bids_it_for_territorial_manager(
    telegram_id: str, department_name: str
) -> list[BidITSchema]:
    """
    Returns all history bids IT own to territorial manager with specified telegram id.
    """
    tm = orm.find_worker_by_column(Worker.telegram_id, telegram_id)

    if not tm:
        return []

    department_list = find_department_by_name(department_name)
    if len(department_list) == 0:
        return None

    department = department_list[0]

    bids = orm.get_history_bids_it_for_territorial_manager(tm, department)

    return bids


def get_repairman_telegram_id_by_department(department_name: str) -> int:
    repairman = orm.find_repairman_it_by_department(department_name)
    if repairman is None:
        return None
    return repairman.telegram_id
