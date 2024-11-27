from pathlib import Path
from sqlalchemy import null
from datetime import datetime, timedelta
from fastapi import UploadFile
from typing import Any, Optional

from app.infra.logging import logger

import app.infra.database.orm as orm
from app.infra.database.models import (
    Department,
    ApprovalStatus,
    TechnicalRequest,
    Worker,
)
from app.infra.database.schemas import (
    TechnicalProblemSchema,
    TechnicalRequestSchema,
    WorkerSchema,
    DocumentSchema,
)


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
        logger.error(f"Worker with telegram id {telegram_id} wasn't found")

    problem = orm.get_technical_problem_by_problem_name(problem_name=problem_name)
    if not problem:
        logger.error(f"Problem with name {problem_name} wasn't found")

    repairman = orm.get_repairman_by_department_id_and_executor_type(
        department_id=worker.department.id, executor_type=problem.executor.name
    )

    if not repairman:
        logger.error(
            f"Repairman from department id: {worker.department.id} and responsible by {problem.executor.name} wasn't found"
        )

    territorial_manager = orm.get_territorial_manager_by_department_id(
        worker.department.id
    )
    if not territorial_manager:
        logger.error(
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
        logger.error("Technical problem record wasn't created")

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
        logger.error(f"Technical problem with id {request.id} record wasn't updated")
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
    Return repairman telegram id if mark == 1 else None
    """
    cur_date = datetime.now()

    request = get_technical_request_by_id(request_id=request_id)

    request.score = mark

    if request.reopen_date:
        request.close_description = description
    else:
        request.confirmation_description = description

    if mark != 1:
        request.state = ApprovalStatus.approved
        request.close_date = cur_date
        request.acceptor_post = request.territorial_manager.post
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

            request.reopen_deadline_date = counting_date_sla(24)

    if not orm.update_technical_request_from_territorial_manager(request):
        logger.error(f"Technical problem with id {request.id} record wasn't updated")

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
        logger.error(f"Worker with full name: {repairman_full_name} wasn't found")

    if not orm.update_tech_request_executor(
        request_id=request_id, repairman_id=repairman.id
    ):
        logger.error(f"Technical request with id: {request_id} wasn't update executor")
    return repairman.telegram_id


def update_technical_request_problem(request_id: int, problem_id: int):
    if not orm.update_technical_request_problem(
        request_id=request_id, problem_id=problem_id
    ):
        logger.error(f"Technical request with id: {request_id} wasn't update problem")


def get_all_waiting_technical_requests_for_worker(
    telegram_id: int,
) -> list[TechnicalRequestSchema]:
    """
    Return all technical requests by Telegram id
    """
    try:
        worker = orm.get_workers_with_post_by_column(Worker.telegram_id, telegram_id)[0]
    except IndexError:
        logger.error(f"Worker with telegram id {telegram_id} wasn't found")
    else:
        requests = orm.get_technical_requests_by_columns(
            [TechnicalRequest.worker_id, TechnicalRequest.close_date],
            [worker.id, null()],
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
        logger.error(f"Repairman with telegram id: {telegram_id} wasn't found")
    else:
        try:
            department_id = (orm.find_departments_by_name(department_name)[0]).id
        except IndexError:
            logger.error(f"Department with name: {department_name} wasn't found")
        else:
            requests = orm.get_technical_requests_by_columns(
                [
                    TechnicalRequest.repairman_id,
                    TechnicalRequest.state,
                    TechnicalRequest.department_id,
                    TechnicalRequest.confirmation_date,
                ],
                [repairman.id, ApprovalStatus.pending, department_id, null()],
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
        logger.error(f"Repairman with telegram id: {telegram_id} wasn't found")
    else:
        try:
            department_id = (orm.find_departments_by_name(department_name)[0]).id
        except IndexError:
            logger.error(f"Department with name: {department_name} wasn't found")
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
        logger.error(
            f"Territorial manager with telegram id: {telegram_id} wasn't found"
        )
    else:
        try:
            department_id = (orm.find_departments_by_name(department_name)[0]).id
        except IndexError:
            logger.error(f"Department with name: {department_name} wasn't found")
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
        logger.error(f"Department with name {department_name} wasn't found")
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
        logger.error(f"Repairman with telegram id: {telegram_id} wasn't found")
    else:
        try:
            department_id = (orm.find_departments_by_name(department_name)[0]).id
        except IndexError:
            logger.error(f"Department with name: {department_name} wasn't found")
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
        logger.error(
            f"Territorial manager with telegram id: {telegram_id} wasn't found"
        )
    else:
        try:
            department_id = (orm.find_departments_by_name(department_name)[0]).id
        except IndexError:
            logger.error(f"Department with name: {department_name} wasn't found")
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
        logger.error(f"Worker with telegram id: {telegram_id} wasn't found")
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
        logger.error(f"Department with name {department_name} wasn't found")
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
        logger.error(f"Request with id: {request_id} wasn't founds")


def _get_departments_names_for_employee(
    telegram_id: int, worker_column: Any
) -> list[str]:
    """
    Return departments by worker telegram id and worker column id
    """
    try:
        worker = orm.get_workers_with_post_by_column(Worker.telegram_id, telegram_id)[0]
    except IndexError:
        logger.error(f"Worker with telegram id: {telegram_id} wasn't found")
    else:
        departments_names = orm.get_departments_names_by_worker_id_and_worker_column(
            worker_column=worker_column, worker_id=worker.id
        )
        return departments_names


def get_departments_names_for_repairman(
    telegram_id: int,
) -> list[str]:
    try:
        worker = orm.get_workers_with_post_by_column(Worker.telegram_id, telegram_id)[0]
    except IndexError:
        logger.error(f"Worker with telegram id: {telegram_id} wasn't found")
    else:
        return orm.get_departments_names_for_repairman(worker_id=worker.id)


def get_departments_names_for_territorial_manager(
    telegram_id: int,
) -> list[str]:
    return _get_departments_names_for_employee(
        telegram_id=telegram_id, worker_column=Department.territorial_manager_id
    )


def get_departments_names_for_chief_technician(
    telegram_id: int,
) -> list[str]:
    return _get_departments_names_for_employee(
        telegram_id=telegram_id, worker_column=Department.chief_technician_id
    )


def get_all_active_requests_in_department_for_chief_technician(
    department_name: str,
) -> list[TechnicalRequestSchema]:
    """
    Return all request in department
    """
    try:
        department_id = (orm.find_departments_by_name(department_name)[0]).id
    except IndexError:
        logger.error(f"Department with name: {department_name} wasn't found")
    else:
        requests = orm.get_all_active_requests_in_department(department_id)[:-16:-1]
        return requests


def get_all_worker_in_group(
    group_name: str,
) -> list[WorkerSchema]:
    """
    Return all workers in group
    """
    group = orm.get_group_by_name(group_name)
    if not group:
        logger.error(f"Group with name: {group_name} wasn't found")
    workers = orm.get_all_worker_in_group(group.id)
    if len(workers) == 0:
        logger.error(f"Workers with group id: {group.id} wasn't founds")
    return workers


def close_request(
    request_id: int,
    description: str,
    telegram_id: int,
) -> int:
    """
    Close request by acceptor_post
    Return creator TG id
    """
    cur_date = datetime.now()
    logger.error(12)
    acceptor_post_id = (
        orm.get_workers_with_post_by_column(Worker.telegram_id, telegram_id)[0]
    ).post.id
    tg_id = orm.close_request(
        request_id=request_id,
        description=description,
        close_date=cur_date,
        acceptor_post_id=acceptor_post_id,
    )

    if not tg_id:
        logger.error(f"Request with id: {request_id} wasn't close")

    return tg_id


def get_request_count_in_departments(
    state: ApprovalStatus, tg_id: int
) -> tuple[str, int]:
    worker_id = orm.get_workers_with_post_by_column(Worker.telegram_id, tg_id)
    if len(worker_id) == 0:
        logger.error(f"Worker with telegram id: {tg_id} not found")
    else:
        worker_id = worker_id[0].id

    return orm.get_count_req_in_departments(state, worker_id)
