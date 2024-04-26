from typing import Any
from aiogram.utils.markdown import hbold
from db.models import ApprovalState
from db.schemas import BidShema
from bot.kb import payment_type_dict
from aiogram.types import Message


def get_full_bid_info(bid: BidShema) -> str:
    stage = ""

    if bid.kru_state == ApprovalState.pending_approval:
        stage = "КРУ"
    elif bid.owner_state == ApprovalState.pending_approval:
        stage = "Собственник"
    elif bid.accountant_card_state == ApprovalState.pending_approval:
        stage = "Бухгалтер безнал."
    elif bid.accountant_cash_state == ApprovalState.pending_approval:
        stage = "Бухгалтер нал."
    elif bid.teller_card_state == ApprovalState.pending_approval:
        stage = "Кассир безнал."
    elif bid.teller_cash_state == ApprovalState.pending_approval:
        stage = "Кассир нал."
    elif (
        bid.kru_state == ApprovalState.denied or
        bid.owner_state == ApprovalState.denied or
        bid.accountant_card_state == ApprovalState.denied or
        bid.accountant_cash_state == ApprovalState.denied or
        bid.teller_card_state == ApprovalState.denied or
        bid.teller_cash_state == ApprovalState.denied
    ):
        stage = "Отказано"
    else:
        stage = "Выплачено"

    bid_info = f"""{hbold("Сумма")}: {bid.amount}
{hbold("Тип оплаты")}: {payment_type_dict[bid.payment_type]}
{hbold("Предприятие")}: {bid.department.name}
{hbold("Документ")}: Прикреплен к сообщению.
{hbold("Цель платежа")}: {bid.purpose}
{hbold("Наличие договора")}: {bid.agreement}
{hbold("Заявка срочная?")} {bid.urgently}
{hbold("Нужна платежка?")} {bid.need_document}
{hbold("Комментарий")}: {bid.comment}
{hbold("Текущий этап")}: {stage}
"""

    return bid_info


def get_state_bid_info(bid: BidShema) -> str:
    stage = ""
    if bid.kru_state == ApprovalState.pending_approval:
        stage = "КРУ"
    elif bid.owner_state == ApprovalState.pending_approval:
        stage = "Собственника"
    elif bid.accountant_card_state == ApprovalState.pending_approval:
        stage = "Бухгалтера безнал."
    elif bid.accountant_cash_state == ApprovalState.pending_approval:
        stage = "Бухгалтера нал."
    elif bid.teller_card_state == ApprovalState.pending_approval:
        stage = "Кассира безнал."
    elif bid.teller_cash_state == ApprovalState.pending_approval:
        stage = "Кассира нал."

    return f"""Заявка от {bid.create_date.date()} на сумму: {bid.amount}.
Статус: на согласовании у {stage}"""


def get_bid_list_info(bid: BidShema) -> str:
    return (f"{bid.worker.l_name} " +
            f"{bid.create_date.strftime('%d.%m.%Y')} {bid.amount}")


async def try_delete_message(message: Message) -> bool:
    '''
    Tries to delete message, return `True`
    if the `message` successfully deleted, `False` otherwise.
    '''
    try:
        await message.delete()
        return True
    except Exception:
        return False


async def try_edit_message(
        message: Message,
        text: str,
        reply_markup: Any = None
) -> None:
    '''
    Tries to edit message.
    if the `message` unsuccessfully edited
    then answers message.
    '''
    try:
        await message.edit_text(text=text, reply_markup=reply_markup)
    except Exception:
        return
        # await message.answer(text=text, reply_markup=reply_markup)
