from pathlib import Path
from sqlalchemy import null
from datetime import datetime
from fastapi import UploadFile

from app.infra.logging import logger

import app.infra.database.orm as orm
from app.infra.database.models import (
    CleaningRequest,
    ApprovalStatus,
    Worker,
)
from app.schemas import (
    CleaningRequestSchema,
    DocumentSchema,
)


# region Worker


def get_cleaning_problem_names() -> list[str]:
    return [problem.problem_name for problem in orm.get_cleaning_problems()]


async def create_cleaning_request(
    problem_name: str,
    description: str,
    photo_files: list[UploadFile],
    telegram_id: int,
    department_name: str,
) -> bool:
    from app.adapters.bot.handlers.utils import notify_worker_by_telegram_id
    from app.adapters.bot import text as t

    """
    Create cleaning request
    Return: bool
    """
    cur_date = datetime.now()

    last_cleaning_request_id = orm.get_last_cleaning_request_id()
    if not last_cleaning_request_id:
        last_cleaning_request_id = 0

    department = orm.find_departments_by_name(department_name)
    if department == []:
        logger.error(f"Department with name: {department_name} wasn't found")
    department = department[0]

    worker = orm.get_workers_with_post_by_column(Worker.telegram_id, telegram_id)[0]
    if worker is None:
        logger.error(f"Worker with telegram id {telegram_id} wasn't found")

    problem = orm.get_cleaning_problem_by_problem_name(name=problem_name)
    if problem is None:
        logger.error(f"Problem with name {problem_name} wasn't found")

    cleaner = orm.get_cleaner_in_department(department_id=department.id)
    if cleaner is None:
        logger.error(f"Cleaner from department id: {department.id} wasn't found")

    territorial_manager = orm.get_territorial_manager_by_department_id(department.id)
    if territorial_manager is None:
        logger.error(
            f"Territorial manager with department id: {department.id} wasn't found"
        )

    documents = []
    for index, doc in enumerate(photo_files):
        suffix = Path(doc.filename).suffix
        filename = f"photo_problem_cleaning_request_{last_cleaning_request_id + 1}_{index + 1}{suffix}"
        doc.filename = filename
        documents.append(DocumentSchema(document=doc))

    request = CleaningRequestSchema(
        problem=problem,
        description=description,
        problem_photos=documents,
        state=ApprovalStatus.pending,
        open_date=cur_date,
        worker=worker,
        cleaner=cleaner,
        territorial_manager=territorial_manager,
        department=department,
    )

    if not orm.create_cleaning_request(request):
        logger.error("Cleaning request record wasn't created")
        return False

    await notify_worker_by_telegram_id(
        id=cleaner.telegram_id,
        message=t.notification_cleaner
        + f"\n На производстве: {request.department.name}",
    )

    return True


def get_all_history_cleaning_requests_for_worker(tg_id: int):
    worker = orm.get_workers_with_post_by_column(Worker.telegram_id, tg_id)
    if worker == []:
        logger.error()
    worker = worker[0]
    return orm.get_all_history_cleaning_requests_for_worker(worker_id=worker.id)


def get_all_waiting_cleaning_requests_for_worker(tg_id: int):
    worker = orm.get_workers_with_post_by_column(Worker.telegram_id, tg_id)
    if worker == []:
        logger.error()
    worker = worker[0]
    return orm.get_all_waiting_cleaning_requests_for_worker(worker_id=worker.id)


# endregion
# region Cleaner


def get_departments_names_for_cleaner(tg_id: int) -> list[str]:
    cleaner = orm.get_workers_with_post_by_column(Worker.telegram_id, tg_id)
    if cleaner == []:
        return []
    cleaner = cleaner[0]
    return orm.get_departments_names_for_cleaner(cleaner_id=cleaner.id)


def get_all_history_cleaning_requests_for_cleaner(
    tg_id: int, department_name: str, limit: int = 15
) -> list[CleaningRequestSchema]:
    try:
        cleaner = orm.get_workers_with_post_by_column(Worker.telegram_id, tg_id)[0]
    except IndexError:
        logger.error(f"Repairman with telegram id: {tg_id} wasn't found")
    else:
        try:
            department_id = (orm.find_departments_by_name(department_name)[0]).id
        except IndexError:
            logger.error(f"Department with name: {department_name} wasn't found")
        else:
            requests = orm.get_last_cleaning_requests_by_columns(
                and_col=[
                    CleaningRequest.cleaner_id,
                    CleaningRequest.department_id,
                ],
                and_val=[
                    cleaner.id,
                    department_id,
                ],
                or_col=[
                    CleaningRequest.state,
                    CleaningRequest.state,
                    CleaningRequest.state,
                    CleaningRequest.state,
                    CleaningRequest.state,
                ],
                or_val=[
                    ApprovalStatus.approved,
                    ApprovalStatus.denied,
                    ApprovalStatus.pending_approval,
                    ApprovalStatus.not_relevant,
                    ApprovalStatus.skipped,
                ],
            )

            return requests


def get_all_waiting_cleaning_requests_for_cleaner(
    tg_id: int, department_name: str
) -> list[CleaningRequestSchema]:
    try:
        cleaner = orm.get_workers_with_post_by_column(Worker.telegram_id, tg_id)[0]
    except IndexError:
        logger.error(f"Repairman with telegram id: {tg_id} wasn't found")
    else:
        try:
            department_id = (orm.find_departments_by_name(department_name)[0]).id
        except IndexError:
            logger.error(f"Department with name: {department_name} wasn't found")
        else:
            requests = orm.get_last_cleaning_requests_by_columns(
                [
                    CleaningRequest.cleaner_id,
                    CleaningRequest.department_id,
                    CleaningRequest.state,
                    CleaningRequest.cleaning_date,
                ],
                [
                    cleaner.id,
                    department_id,
                    ApprovalStatus.pending,
                    null(),
                ],
            )

            return requests


def get_all_rework_cleaning_requests_for_cleaner(
    tg_id: int, department_name: str
) -> list[CleaningRequestSchema]:
    try:
        cleaner = orm.get_workers_with_post_by_column(Worker.telegram_id, tg_id)[0]
    except IndexError:
        logger.error(f"Repairman with telegram id: {tg_id} wasn't found")
    else:
        try:
            department_id = (orm.find_departments_by_name(department_name)[0]).id
        except IndexError:
            logger.error(f"Department with name: {department_name} wasn't found")
        else:
            requests = orm.get_all_rework_cleaning_requests_for_cleaner(
                cleaner.id,
                department_id,
            )

            return requests


def get_cleaning_request_by_id(request_id: int) -> CleaningRequestSchema:
    return orm.get_cleaning_request_by_id(request_id)


async def update_cleaning_request_from_cleaner(
    photo_files: list[UploadFile], request_id: int
):
    """
    Update cleaning request
    Notifies territorial manager, chief technician and request of the request #TODO поправить текст
    """

    from app.adapters.bot.handlers.utils import notify_worker_by_telegram_id
    from app.adapters.bot import text

    cur_date = datetime.now()

    request: CleaningRequestSchema = get_cleaning_request_by_id(request_id=request_id)

    if request.reopen_date:
        request.reopen_cleaning_date = cur_date
        for index, doc in enumerate(photo_files):
            suffix = Path(doc.filename).suffix
            filename = f"photo_cleaning_request_{request_id}_reopen_{index + 1}{suffix}"
            doc.filename = filename
            request.cleaning_photos.append(DocumentSchema(document=doc))
    else:
        request.cleaning_date = cur_date

        documents = []
        for index, doc in enumerate(photo_files):
            suffix = Path(doc.filename).suffix
            filename = f"photo_cleaning_request_{request_id}_{index + 1}{suffix}"
            doc.filename = filename
            documents.append(DocumentSchema(document=doc))

        request.cleaning_photos = documents

    request.state = ApprovalStatus.pending_approval

    if not orm.update_cleaning_request_from_cleaner(request):
        logger.error(f"Cleaning problem with id {request.id} record wasn't updated")
        return False
    else:
        await notify_worker_by_telegram_id(
            id=request.territorial_manager.telegram_id,
            message=text.notification_territorial_manager_CR,
        )
        await notify_worker_by_telegram_id(
            id=request.worker.telegram_id, message=text.notification_worker_CR
        )
    return True


# endregion
# region Territorial manager


def get_all_history_cleaning_requests_for_territorial_manager(
    tg_id: int,
    department_name: str,
):
    territorial_manager = orm.get_workers_with_post_by_column(Worker.telegram_id, tg_id)
    if territorial_manager == []:
        logger.error(f"Worker with id {tg_id} wasn't found")
    territorial_manager = territorial_manager[0]
    department_id = orm.find_departments_by_name(department_name)
    if department_id is None:
        logger.error(f"Department with name: {department_name} wasn't found")
    department_id = department_id[0].id

    requests = orm.get_last_cleaning_requests_by_columns(
        and_col=[
            CleaningRequest.territorial_manager_id,
            CleaningRequest.department_id,
        ],
        and_val=[
            territorial_manager.id,
            department_id,
        ],
        or_col=[
            CleaningRequest.state,
            CleaningRequest.state,
            CleaningRequest.state,
            CleaningRequest.state,
            CleaningRequest.state,
        ],
        or_val=[
            ApprovalStatus.approved,
            ApprovalStatus.denied,
            ApprovalStatus.pending,
            ApprovalStatus.not_relevant,
            ApprovalStatus.skipped,
        ],
    )
    return requests


def get_all_waiting_cleaning_requests_for_territorial_manager(
    tg_id: int,
    department_name: str,
):
    territorial_manager = orm.get_workers_with_post_by_column(Worker.telegram_id, tg_id)
    if territorial_manager == []:
        logger.error(f"Worker with id {tg_id} wasn't found")
    territorial_manager = territorial_manager[0]
    department_id = orm.find_departments_by_name(department_name)
    if department_id == []:
        logger.error(f"Department with name: {department_name} wasn't found")
    department_id = department_id[0].id

    requests = orm.get_last_cleaning_requests_by_columns(
        and_col=[
            CleaningRequest.territorial_manager_id,
            CleaningRequest.department_id,
            CleaningRequest.state,
        ],
        and_val=[
            territorial_manager.id,
            department_id,
            ApprovalStatus.pending_approval,
        ],
    )
    return requests


async def update_cleaning_request_from_territorial_manager(
    mark: int,
    description: str,
    request_id: int,
) -> bool:
    from app.adapters.bot.handlers.utils import notify_worker_by_telegram_id
    from app.adapters.bot import text

    request = orm.get_cleaning_request_by_id(request_id=request_id)
    if request is None:
        logger.error(f"Cleaning request with id: {request_id} wasn't found")
        return False
    cur_date = datetime.now()

    if request.reopen_date:
        request.close_description = description
    else:
        request.confirmation_description = description

    if mark != 1:
        request.state = ApprovalStatus.approved
        request.close_date = cur_date
        if request.reopen_date:
            request.reopen_confirmation_date = cur_date
        else:
            request.confirmation_date = cur_date
    else:
        if request.reopen_date:
            request.state = ApprovalStatus.skipped
            request.close_date = cur_date
            request.reopen_confirmation_date = cur_date
        else:
            request.state = ApprovalStatus.pending
            request.confirmation_date = cur_date
            request.reopen_date = cur_date

    if not orm.update_cleaning_request_from_territorial_manager(request):
        logger.error(f"Technical problem with id {request.id} record wasn't updated")
        return False
    else:
        if mark == 1 and request.state == ApprovalStatus.pending:
            await notify_worker_by_telegram_id(
                id=request.cleaner.telegram_id,
                message=text.notification_cleaner_reopen
                + f"\nНа производстве: {request.department.name}",
            )
        await notify_worker_by_telegram_id(
            id=request.worker.telegram_id, message=text.notification_worker_CR
        )

    return True


# endregion
