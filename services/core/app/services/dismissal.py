from pathlib import Path
from typing import Any

from app.infra.database import orm
from app.infra.database.models import (
    ApprovalStatus,
    FujiScope,
)
from app.schemas import (
    DismissalSchema,
    DocumentSchema,
)
import logging
from datetime import datetime
from fastapi import UploadFile

from app.services import (
    get_worker_by_telegram_id,
)


async def create_dismissal_blank(
    files: list[UploadFile], dismissal_reason: str, telegram_id: str
) -> bool:
    """
    Creates an dismissal blank wrapped in `DismissalSchema` and adds it to database.
    """

    cur_date = datetime.now()

    worker = get_worker_by_telegram_id(telegram_id)
    if not worker:
        logging.getLogger("uvicorn.error").error(
            f"Worker with telegram id {telegram_id} wasn't found"
        )

    sub = orm.get_subordination_id_by_worker(worker.id)
    if not sub:
        logging.getLogger("uvicorn.error").error(
            f"Worker with telegram id {telegram_id} hasn't chief"
        )
        return False

    last_blank_num = orm.get_last_dismissal_blank_id()
    if not last_blank_num:
        last_blank_num = 0

    documents = []

    for index, file in enumerate(files):
        suffix = Path(file.filename).suffix
        filename = f"document_dismissal_{last_blank_num + 1}_{index + 1}{suffix}"
        file.filename = filename
        documents.append(DocumentSchema(document=file))

    work_times = orm.get_worker_times(worker.id)
    worked_minutes: float = float()
    fines: int = int()
    for work_time in work_times:
        if work_time.work_duration:
            worked_minutes += work_time.work_duration
        if work_time.fine:
            fines += work_time.fine

    material_values = orm.get_material_values(worker.id)
    has_material_values = False
    if len(material_values) > 0:
        for v in material_values:
            if not v.return_date:
                has_material_values = True
                break

    dismissal = DismissalSchema(
        subordination=sub,
        documents=documents,
        create_date=cur_date,
        chief_state=ApprovalStatus.pending_approval,
        kru_state=ApprovalStatus.pending,
        access_state=ApprovalStatus.pending,
        accountant_state=ApprovalStatus.pending,
        tech_state=ApprovalStatus.pending,
        fines=fines,
        worked_minutes=worked_minutes,
        has_material_values=has_material_values,
        dismissal_reason=dismissal_reason,
    )

    orm.add_dismissal(dismissal)

    await notify_chief(dismissal)

    return True


async def notify_chief(dismissal: DismissalSchema):
    from app.adapters.bot.handlers.utils import (
        notify_worker_by_telegram_id,
    )

    message = "У вас новая заявка!"
    await notify_worker_by_telegram_id(
        dismissal.subordination.chief.telegram_id, message
    )


async def notify_next_dismissal_coordinator(dismissal: DismissalSchema):
    """Notifies next dismissal coordinator with `ApprovalStatus.pending_approval`."""
    from app.adapters.bot.handlers.utils import (
        notify_workers_by_scope,
    )

    message = "У вас новая заявка!"

    if dismissal.kru_state == ApprovalStatus.pending_approval:
        await notify_workers_by_scope(
            scope=FujiScope.bot_dismissal_kru, message=message
        )
    elif dismissal.access_state == ApprovalStatus.pending_approval:
        await notify_workers_by_scope(
            scope=FujiScope.bot_dismissal_access, message=message
        )
    elif dismissal.accountant_state == ApprovalStatus.pending_approval:
        await notify_workers_by_scope(
            scope=FujiScope.bot_dismissal_accountant, message=message
        )
    elif dismissal.tech_state == ApprovalStatus.pending_approval:
        await notify_workers_by_scope(
            scope=FujiScope.bot_dismissal_tech, message=message
        )


def get_dismissal_by_id(id: int) -> DismissalSchema:
    return orm.get_dismissal_by_id(id)


def get_pending_dismissal_blanks_by_column(column: Any) -> list[DismissalSchema]:
    """
    Returns all dismissal blanks in database with pending approval state at column.
    """
    return orm.get_specified_pending_dismissal_blanks(column)


def get_pending_dismissal_blanks_for_chief(telegram_id: str) -> list[DismissalSchema]:
    chief = get_worker_by_telegram_id(telegram_id)
    return orm.get_pending_dismissal_blanks_for_chief(chief)


async def update_dismissal_by_chief(dismissal: DismissalSchema, comment: str = None):
    cur_date = datetime.now()

    dismissal.chief_approval_date = cur_date

    if dismissal.chief_state == ApprovalStatus.denied:
        dismissal.chief_comment = comment
        dismissal.close_date = cur_date
    else:
        dismissal.chief_state = ApprovalStatus.approved
        dismissal.kru_state = ApprovalStatus.pending_approval
        dismissal.access_state = ApprovalStatus.pending_approval
        dismissal.accountant_state = ApprovalStatus.pending_approval
        dismissal.tech_state = ApprovalStatus.pending_approval

    orm.update_dismissal(dismissal)

    await notify_next_dismissal_coordinator(dismissal)


def update_dismissal(
    dismissal: DismissalSchema,
    state_name: str,
    comment: str | None,
):
    cur_date = datetime.now()

    match state_name:
        case "kru_state":
            dismissal.kru_state = ApprovalStatus.approved
            dismissal.kru_comment = comment
            dismissal.kru_approval_date = cur_date
        case "access_state":
            dismissal.access_state = ApprovalStatus.approved
            dismissal.access_comment = comment
            dismissal.access_approval_date = cur_date
        case "accountant_state":
            dismissal.accountant_state = ApprovalStatus.approved
            dismissal.accountant_comment = comment
            dismissal.accountant_approval_date = cur_date
        case "tech_state":
            dismissal.tech_state = ApprovalStatus.approved
            dismissal.tech_comment = comment
            dismissal.tech_approval_date = cur_date

    orm.update_dismissal(dismissal)

    # create_xls_file(dismissal)
