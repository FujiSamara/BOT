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
    Worker,
)
from app.schemas import (
    CleaningProblemSchema,
    CleaningRequestSchema,
    WorkerSchema,
    DocumentSchema,
)


def get_cleaning_problem_names() -> list[str]:
    return [problem.problem_name for problem in orm.get_cleaning_problems()]


def create_cleaning_request(
    problem_name: str,
    description: str,
    photo_files: list[UploadFile],
    telegram_id: int,
    department_name: str,
) -> bool:
    from app.adapters.bot.handlers.utils import notify_worker_by_telegram_id
    from app.adapters.bot import text

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

    problem = orm.get_cleaning_problem_by_problem_name(problem_name=problem_name)
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

    return True
