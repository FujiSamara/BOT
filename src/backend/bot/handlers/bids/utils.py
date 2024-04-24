
from db.models import ApprovalState
from db.schemas import BidShema
from bot.kb import payment_type_dict

def get_full_bid_info(bid: BidShema) -> str:
    stage = ""

    if bid.kru_state == ApprovalState.pending_approval:
        stage = "КРУ"
    elif bid.owner_state == ApprovalState.pending_approval:
        stage = "Собственник"
    elif bid.accountant_card_state ==  ApprovalState.pending_approval:
        stage = "Бухгалтер безнал."
    elif bid.accountant_cash_state ==  ApprovalState.pending_approval:
        stage = "Бухгалтер нал."
    elif bid.teller_card_state ==  ApprovalState.pending_approval:
        stage = "Кассир безнал."
    elif bid.teller_cash_state ==  ApprovalState.pending_approval:
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

    bid_info = f"""Сумма: {bid.amount}
Тип оплаты: {payment_type_dict[bid.payment_type]}
Предприятие: {bid.department.name}
Документ: Прикреплен к сообщению.
Цель платежа: {bid.purpose}
Наличие договора: {bid.agreement}
Заявка срочная? {bid.urgently}
Нужна платежка? {bid.need_document}
Комментарий: {bid.comment}
Текущий этап: {stage}
"""
   

    return bid_info

def get_state_bid_info(bid: BidShema) -> str:
    stage = ""
    if bid.kru_state == ApprovalState.pending_approval:
        stage = "КРУ"
    elif bid.owner_state == ApprovalState.pending_approval:
        stage = "Собственник"
    elif bid.accountant_card_state ==  ApprovalState.pending_approval:
        stage = "Бухгалтер безнал."
    elif bid.accountant_cash_state ==  ApprovalState.pending_approval:
        stage = "Бухгалтер нал."
    elif bid.teller_card_state ==  ApprovalState.pending_approval:
        stage = "Кассир безнал."
    elif bid.teller_cash_state ==  ApprovalState.pending_approval:
        stage = "Кассир нал."
    
    return f"""Заявка от {bid.create_date.date()} на сумму: {bid.amount}.
Статус: на согласовании у {stage}"""

