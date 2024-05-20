from aiogram.utils.markdown import hbold
from db.models import ApprovalStatus
from db.schemas import BidSchema
from bot.kb import payment_type_dict


def get_full_bid_info(bid: BidSchema) -> str:
    stage = ""

    if bid.kru_state == ApprovalStatus.pending_approval:
        stage = "КРУ"
    elif bid.owner_state == ApprovalStatus.pending_approval:
        stage = "Собственник"
    elif bid.accountant_card_state == ApprovalStatus.pending_approval:
        stage = "Бухгалтер безнал."
    elif bid.accountant_cash_state == ApprovalStatus.pending_approval:
        stage = "Бухгалтер нал."
    elif bid.teller_card_state == ApprovalStatus.pending_approval:
        stage = "Кассир безнал."
    elif bid.teller_cash_state == ApprovalStatus.pending_approval:
        stage = "Кассир нал."
    elif (
        bid.kru_state == ApprovalStatus.denied
        or bid.owner_state == ApprovalStatus.denied
        or bid.accountant_card_state == ApprovalStatus.denied
        or bid.accountant_cash_state == ApprovalStatus.denied
        or bid.teller_card_state == ApprovalStatus.denied
        or bid.teller_cash_state == ApprovalStatus.denied
    ):
        stage = "Отказано"
    else:
        stage = "Выплачено"

    bid_info = f"""{hbold("Сумма")}: {bid.amount}
{hbold("Тип оплаты")}: {payment_type_dict[bid.payment_type]}
{hbold("Предприятие")}: {bid.department.name}
{hbold("Документы")}: Прикреплены к сообщению.
{hbold("Цель платежа")}: {bid.purpose}
{hbold("Наличие договора")}: {bid.agreement}
{hbold("Заявка срочная?")} {bid.urgently}
{hbold("Нужна платежка?")} {bid.need_document}
{hbold("Комментарий")}: {bid.comment}
{hbold("Текущий этап")}: {stage}
"""

    return bid_info


def get_state_bid_info(bid: BidSchema) -> str:
    stage = ""
    if bid.kru_state == ApprovalStatus.pending_approval:
        stage = "КРУ"
    elif bid.owner_state == ApprovalStatus.pending_approval:
        stage = "Собственника"
    elif bid.accountant_card_state == ApprovalStatus.pending_approval:
        stage = "Бухгалтера безнал."
    elif bid.accountant_cash_state == ApprovalStatus.pending_approval:
        stage = "Бухгалтера нал."
    elif bid.teller_card_state == ApprovalStatus.pending_approval:
        stage = "Кассира безнал."
    elif bid.teller_cash_state == ApprovalStatus.pending_approval:
        stage = "Кассира нал."

    return f"""Заявка от {bid.create_date.date()} на сумму: {bid.amount}.
Статус: на согласовании у {stage}"""


def get_bid_list_info(bid: BidSchema) -> str:
    return (
        f"{bid.worker.l_name} " + f"{bid.create_date.strftime('%d.%m.%Y')} {bid.amount}"
    )
