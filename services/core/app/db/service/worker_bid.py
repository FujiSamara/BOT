from pathlib import Path
from datetime import datetime
from fastapi import UploadFile

from app.infra.logging import logger

from app.db.service.extra import get_worker_by_id
import app.db.orm as orm
from app.db.models import (
    Department,
    ApprovalStatus,
    Post,
    Worker,
    WorkerBid,
)
from app.db.schemas import (
    WorkerBidSchema,
    DocumentSchema,
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

    from app.adapters.bot.handlers.utils import (
        notify_worker_by_telegram_id,
        send_menu_by_scopes,
    )

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
    if msg is not None:
        await send_menu_by_scopes(msg)


def get_worker_bid_by_id(id: int) -> WorkerBidSchema:
    """
    Returns worker bid in database by it id.
    """
    return orm.find_worker_bid_by_column(WorkerBid.id, id)


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
        logger.error(f"Department with name '{department_name}' not found")
        return

    post = orm.find_post_by_column(Post.name, post_name)
    if not post:
        logger.error(f"Post with name '{post_name}' not found")
        return

    sender = orm.find_worker_by_column(Worker.telegram_id, sender_telegram_id)
    if not sender:
        logger.error(f"Sender with telegram id '{sender_telegram_id}' not found")
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
