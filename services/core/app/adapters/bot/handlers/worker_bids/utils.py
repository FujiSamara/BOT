from app.schemas import WorkerBidSchema
from app.infra.database.models import ApprovalStatus, ViewStatus
from app.infra.config import settings
from aiogram.utils.markdown import hbold
from app.services import (
    get_worker_by_id,
    get_worker_bid_documents_requests,
    get_worker_bid_coordinators,
)
from app.infra.database.models import FujiScope
from app.adapters.bot.handlers.utils import notify_workers_by_scope
from typing import Any
from aiogram.types import InlineKeyboardButton
from app.adapters.bot.handlers.worker_bids.schemas import (
    WorkerBidCallbackData,
    WorkerBidPagesCallbackData,
    BidViewMode,
)


def get_full_worker_bid_info(bid: WorkerBidSchema) -> str:
    stage = ""

    if bid.state == ApprovalStatus.pending_approval:
        stage = "Ожидает согласования"
    elif bid.state == ApprovalStatus.approved:
        stage = "Согласована"
    else:
        stage = "Отказано"

    bid_info = f"""{hbold("Номер заявки")}: {bid.id}
{hbold("Фамилия")}: {bid.l_name}
{hbold("Имя")}: {bid.f_name}
{hbold("Отчество")}: {bid.o_name}
{hbold("Дата рождения")}: {bid.birth_date.strftime(settings.date_format) if bid.birth_date is not None else "Отсутствует"}
{hbold("Номер телефона")}: {bid.phone_number if bid.phone_number is not None else "Отсутствует"}
{hbold("Предприятие")}: {bid.department.name}
{hbold("Документы")}: Прикреплены к сообщению.
{hbold("Должность")}: {bid.post.name}
{hbold("Статус")}: {stage}
{hbold("Официальное трудоустройство")}: {"Да" if bid.official_work else "Нет"}
{hbold("Уже трудоустроен")}: {"Да" if bid.employed else "Нет"}

{hbold("Данные заявителя")}
{hbold("Фамилия")}: {bid.sender.l_name}
{hbold("Имя")}: {bid.sender.f_name}
{hbold("Отчество")}: {bid.sender.o_name}
{hbold("Номер телефона")}: {bid.sender.phone_number if bid.sender.phone_number is not None else "Отсутствует"}
"""
    coordinators = get_worker_bid_coordinators(bid.id)

    bid_info += "\nСогласовали:"
    if (
        bid.accounting_service_comment is not None
        and bid.accounting_service_comment != ""
    ):
        if len(coordinators) > 0:
            bid_info += f"\n{coordinators[0].l_name} {coordinators[0].f_name}: {bid.accounting_service_comment}"
        else:
            bid_info += f"\Кадровый учёт: {bid.accounting_service_comment}"

    if bid.security_service_comment is not None and bid.security_service_comment != "":
        if len(coordinators) > 1:
            bid_info += f"\n{coordinators[1].l_name} {coordinators[1].f_name}: {bid.security_service_comment}"
        else:
            bid_info += f"\nСлужба безопасности: {bid.security_service_comment}"

    if (
        bid.financial_director_comment is not None
        and bid.financial_director_comment != ""
    ):
        if len(coordinators) > 2:
            bid_info += f"\n{coordinators[2].l_name} {coordinators[2].f_name}: {bid.financial_director_comment}"
        else:
            bid_info += f"\nФинансовый директор: {bid.financial_director_comment}"

    if bid.iiko_service_state == ApprovalStatus.approved:
        bid_info += f"\n{coordinators[-1].l_name} {coordinators[-1].f_name}: Табельный номер {bid.iiko_worker_id}"

    if bid.state == ApprovalStatus.denied:
        bid_info += f"Отказано \n{coordinators[-1].l_name} {coordinators[-1].f_name} по причине {bid.comment}"

    documents_requests = get_worker_bid_documents_requests(bid.id)
    if documents_requests != []:
        bid_info += f"\n\n{hbold('История запросов на дополнение документов')}"
        for documents_request in documents_requests:
            bid_info += f"\n{documents_request.sender.l_name} "
            if documents_request.sender.f_name is not None:
                bid_info += f"{documents_request.sender.f_name[0]}. "
            if documents_request.sender.l_name is not None:
                bid_info += f"{documents_request.sender.l_name[0]}."
            bid_info += f": {documents_request.message}"

    return bid_info


def get_worker_bid_list_info(bid: WorkerBidSchema) -> str:
    return (
        f"{bid.id}: {bid.l_name} " + f"{bid.create_date.strftime(settings.date_format)}"
    )


async def notify_accounting(worker_id: int):
    worker = get_worker_by_id(worker_id)
    notify_workers_by_scope(
        FujiScope.bot_worker_bid_accounting_coordinate,
        message=f"{worker.l_name} {worker.f_name} {worker.o_name} успешно прошёл стажировку",
    )


def get_worker_pending_bids_btns(
    state_column: Any,
    buttons: list[InlineKeyboardButton],
    name: str,
    page_callback_data: WorkerBidPagesCallbackData,
):
    from app.services import get_pending_approval_bids
    from app.infra.database.models import WorkerBid

    bids = (
        get_pending_approval_bids(
            state_column=state_column, offset=page_callback_data.page
        )
        or []
    )
    if state_column == WorkerBid.accounting_service_state:
        for bid in bids:
            match bid.view_state:
                case ViewStatus.viewed:
                    symbol = "👁"
                case ViewStatus.pending:
                    symbol = "⏰"
                case ViewStatus.pending_approval:
                    symbol = "✉️"
                case _:
                    symbol = ""

            buttons.append(
                InlineKeyboardButton(
                    text=f"{symbol} {bid.id} {bid.l_name} {bid.f_name[0]} {bid.o_name[0]} {bid.post.name}",
                    callback_data=WorkerBidCallbackData(
                        id=bid.id,
                        mode=BidViewMode.full_with_approve,
                        endpoint_name=f"get_pending_bid_{name}",
                    ).pack(),
                )
            )
    else:
        for bid in bids:
            buttons.append(
                InlineKeyboardButton(
                    text=f"{bid.id} {bid.l_name} {bid.f_name[0]} {bid.o_name[0]} {bid.post.name}",
                    callback_data=WorkerBidCallbackData(
                        id=bid.id,
                        mode=BidViewMode.full_with_approve,
                        endpoint_name=f"get_pending_bid_{name}",
                    ).pack(),
                )
            )
    if len(bids) == 20:
        buttons.append(
            InlineKeyboardButton(
                text="Следующая страница",
                callback_data=WorkerBidPagesCallbackData(
                    page=page_callback_data.page + 1,
                    state_name=page_callback_data.state_name,
                ).pack(),
            )
        )
    if page_callback_data.page > 0:
        buttons.append(
            InlineKeyboardButton(
                text="Предыдущая страница",
                callback_data=WorkerBidPagesCallbackData(
                    page=page_callback_data.page - 1,
                    state_name=page_callback_data.state_name,
                ).pack(),
            )
        )
