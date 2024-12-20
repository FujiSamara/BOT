from app.schemas import WorkerBidSchema
from app.infra.database.models import ApprovalStatus
from app.infra.config import settings
from aiogram.utils.markdown import hbold


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
"""

    return bid_info


def get_worker_bid_list_info(bid: WorkerBidSchema) -> str:
    return (
        f"{bid.id}: {bid.l_name} " + f"{bid.create_date.strftime(settings.date_format)}"
    )
