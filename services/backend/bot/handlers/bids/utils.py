from aiogram.utils.markdown import hbold
from db.models import ApprovalStatus
from db.schemas import BidSchema, WorkerBidSchema
from bot.kb import payment_type_dict


def get_full_bid_info(bid: BidSchema) -> str:
    bid_state = get_bid_state_info(bid)

    bid_info = f"""{hbold("Номер заявки")}: {bid.id}
{hbold("Создатель")}: {bid.worker.l_name} {bid.worker.f_name}
{hbold("Сумма")}: {bid.amount}
{hbold("Тип оплаты")}: {payment_type_dict[bid.payment_type]}
{hbold("Предприятие заявителя")}: {bid.department.name}"""
    if bid.teller_cash_state != ApprovalStatus.skipped:
        if bid.paying_department is not None:
            bid_info += f"""\n{hbold("Предприятие плательщик")}: {bid.paying_department.name}\n"""
        else:
            bid_info += f"""\n{hbold("Предприятие плательщик")}: Определяется\n"""
    bid_info += f"""{hbold("Документы")}: Прикреплены к сообщению.
{hbold("Цель платежа")}: {bid.purpose}
{hbold("Комментарий")}: {bid.comment}
{hbold("Текущий этап")}: {bid_state}
{hbold("Счет в ЭДО?")}: {"Да" if bid.need_edm else "Нет"}
{hbold("Тип деятельности")}: {bid.activity_type}
"""

    if bid_state == "Отказано":
        bid_info += f"\n{hbold('Причина отказа')}: {bid.denying_reason}"

    return bid_info


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
{hbold("Предприятие")}: {bid.department.name}
{hbold("Документы")}: Прикреплены к сообщению.
{hbold("Должность")}: {bid.post.name}
{hbold("Статус")}: {stage}
"""

    return bid_info


def get_bid_state_info(bid: BidSchema) -> str:
    stage = "На согласовании у "

    if bid.fac_state == ApprovalStatus.pending_approval:
        stage += "ЦФО"
    elif bid.cc_state == ApprovalStatus.pending_approval:
        stage += "ЦЗ"
    elif bid.paralegal_state == ApprovalStatus.pending_approval:
        stage += "Юрисконсульт"
    elif bid.kru_state == ApprovalStatus.pending_approval:
        stage += "КРУ"
    elif bid.owner_state == ApprovalStatus.pending_approval:
        stage += "Собственник"
    elif bid.accountant_card_state == ApprovalStatus.pending_approval:
        stage += "Бухгалтер безнал."
    elif bid.accountant_cash_state == ApprovalStatus.pending_approval:
        stage += "Бухгалтер нал."
    elif bid.teller_card_state == ApprovalStatus.pending_approval:
        stage += "Кассир безнал."
    elif bid.teller_cash_state == ApprovalStatus.pending_approval:
        stage += "Кассир нал."
    elif (
        bid.fac_state == ApprovalStatus.denied
        or bid.cc_state == ApprovalStatus.denied
        or bid.paralegal_state == ApprovalStatus.denied
        or bid.kru_state == ApprovalStatus.denied
        or bid.owner_state == ApprovalStatus.denied
        or bid.accountant_card_state == ApprovalStatus.denied
        or bid.accountant_cash_state == ApprovalStatus.denied
        or bid.teller_card_state == ApprovalStatus.denied
        or bid.teller_cash_state == ApprovalStatus.denied
    ):
        stage = "Отказано"
    else:
        stage = "Выплачено"

    return stage


def get_short_bid_info(bid: BidSchema) -> str:
    return f"""Заявка {bid.id} от {bid.create_date.date()} на сумму: {bid.amount}.
Статус: {get_bid_state_info(bid)}"""


def get_bid_list_info(bid: BidSchema) -> str:
    return (
        f"{bid.id}: {bid.worker.l_name} "
        + f"{bid.create_date.strftime('%d.%m.%Y')} {bid.amount}"
    )


def get_worker_bid_list_info(bid: WorkerBidSchema) -> str:
    return f"{bid.id}: {bid.l_name} " + f"{bid.create_date.strftime('%d.%m.%Y')}"


def get_current_coordinator_field(bid: BidSchema) -> str:
    if bid.fac_state == ApprovalStatus.pending_approval:
        return "fac_state"
    elif bid.cc_state == ApprovalStatus.pending_approval:
        return "cc_state"
    elif bid.paralegal_state == ApprovalStatus.pending_approval:
        return "paralegal_state"

    elif bid.kru_state == ApprovalStatus.pending_approval:
        return "kru_state"
    elif bid.owner_state == ApprovalStatus.pending_approval:
        return "owner_state"
    elif bid.accountant_card_state == ApprovalStatus.pending_approval:
        return "accountant_card_state"
    elif bid.accountant_cash_state == ApprovalStatus.pending_approval:
        return "accountant_cash_state"
    elif bid.teller_card_state == ApprovalStatus.pending_approval:
        return "teller_card_state"
    elif bid.teller_cash_state == ApprovalStatus.pending_approval:
        return "teller_cash_state"
