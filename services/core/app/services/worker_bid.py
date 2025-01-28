from pathlib import Path
from datetime import datetime
from fastapi import UploadFile

from app.infra.logging import logger

from app.services.extra import get_worker_by_id
import app.infra.database.orm as orm
from app.infra.database.models import (
    Department,
    ApprovalStatus,
    Post,
    Worker,
    WorkerBid,
    WorkerStatus,
    FujiScope,
)
from app.schemas import (
    WorkerBidSchema,
    DocumentSchema,
    WorkerSchema,
    WorkerBidDocumentRequestSchema,
)
from aiogram.types import InlineKeyboardButton
from app.adapters.bot.kb import create_inline_keyboard
from app.adapters.bot.text import view
from app.adapters.bot.handlers.worker_bids.schemas import (
    WorkerBidCallbackData,
    BidViewMode,
)

states = {
    "security_service_state",
    "accounting_service_state",
}


def get_workers_bids_history_sender(id: str, limit: int = 15) -> list[WorkerBid]:
    """
    Returns all complete workers bids own to sender with specified telegram id.
    """
    sender = orm.find_worker_by_column(Worker.telegram_id, id)

    if not sender:
        return []

    return orm.get_workers_bids_history_sender(sender, limit)


def get_workers_bids_pending_sender(id: str, limit: int = 15) -> list[WorkerBid]:
    """
    Returns all workers bids with state ApprovalStatus.pending_approval own to sender with specified telegram id.
    """
    sender = orm.find_worker_by_column(Worker.telegram_id, id)

    if not sender:
        return []

    return orm.get_workers_bids_pending_sender(sender, limit)


async def update_worker_bid_state(state: ApprovalStatus, bid_id):
    """
    Updates worker bid state to specified `state` by `bid_id` if bid exist.
    """
    worker_bid = orm.get_worker_bid_by_column(WorkerBid.id, bid_id)
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


def create_and_add_worker(worker_bid: WorkerBidSchema) -> int | None:
    """Creates and add worker from worker bid in database.

    Returns:
        `int | None`: worker id:int if worker was created successfully else None
    """
    last_worker_id = orm.get_last_worker_id()
    passport = []
    for index, doc in enumerate(worker_bid.passport + worker_bid.work_permission):
        doc = doc.document
        suffix = Path(doc.filename).suffix
        filename = f"photo_worker_document_{last_worker_id + 1}_{index + 1}{suffix}"
        doc.filename = filename
        passport.append(DocumentSchema(document=doc))
    worker = WorkerSchema(
        f_name=worker_bid.f_name,
        l_name=worker_bid.l_name,
        o_name=worker_bid.o_name,
        b_date=worker_bid.birth_date,
        phone_number=worker_bid.phone_number,
        telegram_id=None,
        state=WorkerStatus.internship,
        post=worker_bid.post,
        department=worker_bid.department,
        gender=None,
        employment_date=datetime.now().date(),
        dismissal_date=None,
        medical_records_availability=None,
        citizenship=None,
        password=None,
        can_use_crm=False,
        documents=passport,
        snils=None,
        inn=None,
        registration=None,
        actual_residence=None,
        children=False,
        children_born_date=[],
        military_ticket=None,
        official_work=worker_bid.official_work,
    )
    if orm.add_worker(worker):
        return worker.id
    return None


async def notify_next_coordinator(bid: WorkerBidSchema):
    from app.adapters.bot.handlers.utils import notify_workers_by_scope

    state_column = None
    for state_name in states:
        if getattr(bid, state_name) == ApprovalStatus.pending_approval:
            state_column = state_name
            break
    if state_column is None:
        return

    match state_column:
        case "security_service_state":
            await notify_workers_by_scope(
                scope=FujiScope.bot_worker_bid_security_coordinate,
                message=f"Поступила новая заявка на согласование кандидата!\nНомер заявки: {bid.id}.",
                reply_markup=create_inline_keyboard(
                    InlineKeyboardButton(
                        text=view,
                        callback_data=WorkerBidCallbackData(
                            id=bid.id,
                            mode=BidViewMode.full_with_approve,
                            endpoint_name="get_pending_bid_security_service",
                        ).pack(),
                    )
                ),
            )
        case "accounting_service_state":
            await notify_workers_by_scope(
                scope=FujiScope.bot_worker_bid_accounting_coordinate,
                message=f"Поступила новая заявка на согласование кандидата!\nНомер заявки: {bid.id}.",
                reply_markup=create_inline_keyboard(
                    InlineKeyboardButton(
                        text=view,
                        callback_data=WorkerBidCallbackData(
                            id=bid.id,
                            mode=BidViewMode.full_with_approve,
                            endpoint_name="get_pending_bid_accounting_service",
                        ).pack(),
                    )
                ),
            )


async def update_worker_bid_bot(
    bid_id,
    state_column_name: str,
    state: ApprovalStatus,
    comment: str,
) -> bool:
    """
    Updates worker bid state and comment to specified `state` by `bid_id` if bid exist.
    Use only in bot
    """
    from app.adapters.bot.handlers.utils import notify_worker_by_telegram_id
    from app.adapters.bot.handlers.worker_bids.schemas import (
        CandidatesCoordinationCallbackData,
    )

    worker_bid = orm.get_worker_bid_by_column(WorkerBid.id, bid_id)

    if not worker_bid:
        logger.error(f"Worker bid with id: {bid_id} not found.")
        return False
    if (
        getattr(worker_bid, state_column_name + "_state")
        != ApprovalStatus.pending_approval
    ):
        return
    if state == ApprovalStatus.denied:
        worker_bid.state = state

    match state_column_name:
        case "security_service":
            stage = "службой безопасности"
            worker_bid.security_service_state = state
            worker_bid.security_service_comment = comment
            if state == ApprovalStatus.approved:
                worker_bid.accounting_service_state = ApprovalStatus.pending_approval
            else:
                worker_bid.accounting_service_state = ApprovalStatus.skipped
        case "accounting_service":
            stage = "бухгалтерией"
            worker_bid.accounting_service_state = state
            worker_bid.state = state
            worker_bid.comment = comment
        case _:
            logger.error("State for worker bid not found")

    orm.update_worker_bid(worker_bid)

    if worker_bid.state == ApprovalStatus.approved:
        worker_id = create_and_add_worker(worker_bid)
        if worker_id is None:
            logger.error(f"Worker from worker bid id: {worker_bid.id} wasn't create")

        territorial_manager = orm.get_territorial_manager_by_department_id(
            department_id=worker_bid.department.id
        )
        if territorial_manager is None:
            logger.error(
                f"Territorial manager in department with id: {worker_bid.department.id} wasn't found"
            )

        await notify_worker_by_telegram_id(
            id=territorial_manager.telegram_id,
            message="У Вас новый сотрудник на стажировке",
            reply_markup=create_inline_keyboard(
                InlineKeyboardButton(
                    text=view,
                    callback_data=CandidatesCoordinationCallbackData(
                        id=worker_id,
                        page=0,
                        endpoint_name="show_worker",
                    ).pack(),
                ),
            ),
        )

    worker = get_worker_by_id(worker_bid.sender.id)
    if not worker:
        logger.error(f"Worker with id: {worker_bid.sender.id} not found.")
        return False

    if state == ApprovalStatus.approved:
        await notify_worker_by_telegram_id(
            id=worker.telegram_id,
            message=f"Кандидат согласован {stage}!\nНомер заявки: {worker_bid.id}.",
            reply_markup=create_inline_keyboard(
                InlineKeyboardButton(
                    text=view,
                    callback_data=WorkerBidCallbackData(
                        id=bid_id,
                        mode=BidViewMode.full,
                        endpoint_name="bid",
                    ).pack(),
                ),
            ),
        )
        await notify_next_coordinator(bid=worker_bid)
    elif state == ApprovalStatus.denied:
        await notify_worker_by_telegram_id(
            id=worker.telegram_id,
            message=f"Кандидат не согласован {stage}!\n{comment}\nНомер заявки: {worker_bid.id}.",
            reply_markup=create_inline_keyboard(
                InlineKeyboardButton(
                    text=view,
                    callback_data=WorkerBidCallbackData(
                        id=bid_id,
                        mode=BidViewMode.full,
                        endpoint_name="bid",
                    ).pack(),
                ),
            ),
        )

    return True


def get_worker_bid_by_id(id: int) -> WorkerBidSchema:
    """
    Returns worker bid in database by it id.
    """
    return orm.get_worker_bid_by_column(WorkerBid.id, id)


async def create_worker_bid(
    f_name: str,
    l_name: str,
    o_name: str,
    post_name: str,
    department_name: str,
    worksheet: list[UploadFile],
    passport: list[UploadFile],
    work_permission: list[UploadFile],
    sender_telegram_id: str,
    birth_date: datetime,
    phone_number: str,
    official_work: bool,
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
        id=last_bid_id + 1,
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
        security_service_state=ApprovalStatus.pending_approval,
        accounting_service_state=ApprovalStatus.pending,
        security_service_comment=None,
        sender=sender,
        comment=None,
        birth_date=birth_date,
        phone_number=phone_number,
        official_work=official_work,
    )

    if not orm.add_worker_bid(worker_bid):
        logger.error(f"Worker bid with data: {worker_bid} wasn't create")
    await notify_next_coordinator(worker_bid)


def get_pending_approval_bids(state_column) -> list[WorkerBidSchema] | None:
    return orm.find_worker_bids_by_column(state_column, ApprovalStatus.pending_approval)


def get_subordinates(tg_id: int, limit: int, offset: int) -> tuple[WorkerSchema]:
    chief = orm.get_workers_with_post_by_column(Worker.telegram_id, tg_id)
    if chief == []:
        logger.error(f"Worker with id {chief} wasn't found")
    chief = chief[0]
    workers = orm.get_subordinates_in_departments(chief_id=chief.id)
    workers += orm.get_subordinates(chief_id=chief.id)
    return tuple(workers)[offset * limit : (offset + 1) * limit]


def search_subordinate(tg_id: int, l_name: str) -> int | None:
    chief = orm.get_workers_with_post_by_column(Worker.telegram_id, tg_id)
    if chief == []:
        logger.error(f"Worker with id {chief} wasn't found")
    chief = chief[0]

    worker = orm.get_subordinates(chief_id=chief.id, l_name=l_name)
    if worker != []:
        return worker[0].id

    worker = orm.get_subordinates_in_departments(chief_id=chief.id, l_name=l_name)
    if worker != []:
        return worker[0].id

    return None


def update_worker_state(worker_id: int, state: WorkerStatus) -> bool:
    from app.adapters.bot.handlers.utils import notify_workers_by_scope
    from app.adapters.bot.kb import create_inline_keyboard
    from app.adapters.bot.text import view
    from aiogram.types import InlineKeyboardButton
    from app.adapters.bot.handlers.worker_bids.schemas import (
        CandidatesCoordinationCallbackData,
    )

    worker = get_worker_by_id(worker_id)
    if worker is None:
        return False
    if worker.state == WorkerStatus.internship and (
        state == WorkerStatus.active or state == WorkerStatus.refusal_internship
    ):
        notify_workers_by_scope(
            scope=FujiScope.bot_worker_bid_accounting_coordinate,
            message=f"Сотрудник {worker.l_name} {worker.f_name} {worker.o_name}.\nid сотрудника {worker.id}\
                \n{'Отказался от стажировки' if state == WorkerStatus.refusal_internship else 'Прошёл стажировку'}",
            reply_markup=create_inline_keyboard(
                InlineKeyboardButton(
                    text=view,
                    callback_data=CandidatesCoordinationCallbackData(
                        id=worker.id,
                        endpoint_name="show_worker_notification",
                    ).pack(),
                )
            ),
        )
    worker.state = state
    orm.update_worker(worker)
    return True


async def update_worker_bid_documents(
    bid_id: int,
    files: list[UploadFile],
) -> bool:
    """Add new documents from sender.

    Returns:
    `bool`: True if documents upload otherwise False
    """
    from app.adapters.bot.handlers.utils import notify_workers_by_scope

    if files == []:
        return False

    if orm.get_worker_bid_by_column(WorkerBid.id, bid_id) is None:
        return False

    documents: list[DocumentSchema] = []

    last_index = orm.get_last_index_worker_documents(bid_id)
    for index, doc in enumerate(files):
        suffix = Path(doc.filename).suffix
        filename = f"passport_worker_bid_{bid_id}_{last_index + index + 1}{suffix}"
        doc.filename = filename
        document = DocumentSchema(document=doc)
        documents.append(document)

    if orm.update_worker_bid_documents(
        bid_id=bid_id,
        documents=documents,
    ):
        await notify_workers_by_scope(
            FujiScope.bot_worker_bid_accounting_coordinate,
            message=f"Добавлены новые документы к заявке согласования кандидата.\nНомер заявки: {bid_id}.",
            reply_markup=create_inline_keyboard(
                InlineKeyboardButton(
                    text=view,
                    callback_data=WorkerBidCallbackData(
                        id=bid_id,
                        mode=BidViewMode.full_with_approve,
                        endpoint_name="get_pending_bid_accounting_service",
                    ).pack(),
                ),
            ),
        )
        return True
    return False


def get_worker_bid_documents_requests(
    bid_id: int,
) -> list[WorkerBidDocumentRequestSchema]:
    return orm.get_worker_bid_documents_requests(bid_id)


async def add_worker_bids_documents_requests(
    bid_id: int, tg_id: int, message: str
) -> bool:
    from app.adapters.bot.handlers.utils import notify_worker_by_telegram_id

    sender_id = orm.get_workers_with_post_by_column(Worker.telegram_id, tg_id)
    if sender_id == []:
        return False
    sender_id = sender_id[0].id

    worker_bid = orm.get_worker_bid_by_column(WorkerBid.id, bid_id)
    if worker_bid is None:
        return False

    if not orm.add_worker_bids_documents_requests(
        sender_id=sender_id,
        bid_id=bid_id,
        date=datetime.now(),
        message=message,
    ):
        return False

    await notify_worker_by_telegram_id(
        worker_bid.sender.telegram_id,
        message=f"Бухгалтерия запрашивает документы для согласования кандидата.\nНомер заявки {bid_id}",
        reply_markup=create_inline_keyboard(
            InlineKeyboardButton(
                text=view,
                callback_data=WorkerBidCallbackData(
                    id=bid_id,
                    mode=BidViewMode.full_with_update,
                    endpoint_name="bid",
                ).pack(),
            )
        ),
    )

    return True
