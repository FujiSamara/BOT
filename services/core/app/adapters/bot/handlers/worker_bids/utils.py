from app.schemas import WorkerBidSchema
from app.infra.database.models import ApprovalStatus
from app.infra.config import settings
from aiogram.utils.markdown import hbold
from app.services import get_worker_by_id
from app.infra.database.models import FujiScope
from app.adapters.bot.handlers.utils import notify_workers_by_scope


def get_full_worker_bid_info(bid: WorkerBidSchema) -> str:
    stage = ""

    if bid.state == ApprovalStatus.pending_approval:
        stage = "Ожидает согласования"
    elif bid.state == ApprovalStatus.approved:
        stage = "Согласована"
    else:
        stage = "Отказано"

    bid_info = f"""{hbold("Номер заявки")}: {bid.id}
{hbold("Имя")}: {bid.f_name}
{hbold("Фамилия")}: {bid.l_name}
{hbold("Отчество")}: {bid.o_name}
{hbold("Дата рождения")}: {bid.birth_date.strftime(settings.date_format) if bid.birth_date is not None else "Отсутствует"}
{hbold("Номер телефона")}: {bid.phone_number if bid.phone_number is not None else "Отсутствует"}
{hbold("Предприятие")}: {bid.department.name}
{hbold("Документы")}: Прикреплены к сообщению.
{hbold("Должность")}: {bid.post.name}
{hbold("Статус")}: {stage}

{hbold('Данные заявителя')}
{hbold("Имя")}: {bid.sender.f_name}
{hbold("Фамилия")}: {bid.sender.l_name}
{hbold("Отчество")}: {bid.sender.o_name}
{hbold("Номер телефона")}: {bid.sender.phone_number if bid.sender.phone_number is not None else "Отсутствует"}
"""

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
