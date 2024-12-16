from aiogram.utils.markdown import hbold
from app.infra.database.models import ApprovalStatus, FujiScope
from app.schemas import BidSchema, WorkerBidSchema, WorkerSchema
from app.adapters.bot.kb import payment_type_dict

import app.services.bid as bid_service
import app.services.extra as extra_service


def get_full_bid_info(bid: BidSchema) -> str:
    bid_state = get_bid_state_info(bid)

    bid_info = f"""{hbold("Номер заявки")}: {bid.id}
{hbold("Создатель")}: {bid.worker.l_name} {bid.worker.f_name}
{hbold("Сумма")}: {bid.amount}
{hbold("Тип оплаты")}: {payment_type_dict[bid.payment_type]}
{hbold("Статья")}: {bid.expenditure.name}
{hbold("Предприятие заявителя")}: {bid.department.name}"""
    if bid.teller_cash_state != ApprovalStatus.skipped:
        if bid.paying_department is not None:
            bid_info += (
                f"""\n{hbold("Предприятие плательщик")}: {bid.paying_department.name}"""
            )
        else:
            bid_info += f"""\n{hbold("Предприятие плательщик")}: Определяется"""
    elif bid.paying_comment is not None:
        bid_info += f"""\n{hbold("Комментарий бухгалтера:")} {bid.paying_comment}"""
    bid_info += f"""\n{hbold("Документы")}: Прикреплены к сообщению.
{hbold("Цель платежа")}: {bid.purpose}
{hbold("Комментарий")}: {bid.comment}
{hbold("Текущий этап")}: {bid_state}
{hbold("Счет в ЭДО?")}: {"Да" if bid.need_edm else "Нет"}
{hbold("Тип деятельности")}: {bid.activity_type}
"""

    if "Отказано" in bid_state:
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


def get_bid_state_info(bid: BidSchema, separator: str = "-----") -> str:
    """Adds previous coordinators and
    current coordinators to multiline string.
    Separetes previous coordinators substring and current coordinators
    by `separator`.
    """

    coordinator_field = get_current_coordinator_field(bid)
    pending_coordintators: list[WorkerSchema] = []

    match coordinator_field:
        case "fac_state":
            pending_coordintators.append(bid.expenditure.fac)
        case "cc_state":
            pending_coordintators.append(bid.expenditure.cc)
        case "paralegal_state":
            pending_coordintators.append(bid.expenditure.paralegal)
        case "kru_state":
            krus = extra_service.get_workers_by_scope(FujiScope.bot_bid_kru)
            pending_coordintators.extend(krus)
        case "owner_state":
            owners = extra_service.get_workers_by_scope(FujiScope.bot_bid_owner)
            pending_coordintators.extend(owners)
        case "accountant_card_state":
            accountants = extra_service.get_workers_by_scope(
                FujiScope.bot_bid_accountant_card
            )
            pending_coordintators.extend(accountants)
        case "accountant_cash_state":
            accountants = extra_service.get_workers_by_scope(
                FujiScope.bot_bid_accountant_cash
            )
            pending_coordintators.extend(accountants)
        case "teller_card_state":
            tellers = extra_service.get_workers_in_department_by_scope(
                FujiScope.bot_bid_teller_card, bid.department.id
            )
            pending_coordintators.extend(tellers)
        case "teller_card_state":
            tellers = extra_service.get_tellers_cash_for_department(bid.department.id)
            pending_coordintators.extend(tellers)
        case _:
            pass

    previous_coordinators: list[WorkerSchema] = bid_service.get_bid_coordinators(bid.id)

    stage = ""
    if len(previous_coordinators) > 0:
        stage += "\n"
        stage += str.join(
            "\n",
            [
                f"{coordinator.l_name} {coordinator.f_name}"
                for coordinator in previous_coordinators
            ],
        )
    if len(pending_coordintators) > 0:
        current_stage = "\n"
        current_stage += str.join(
            "\n",
            [
                f"{coordinator.l_name} {coordinator.f_name}"
                for coordinator in pending_coordintators
            ],
        )
        separator = "\n" + separator
        stage = str.join(separator, (stage, current_stage))

    if (
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
        separator = "\n" + separator + "\n"
        stage = str.join(separator, (stage, "Отказано"))
    elif (
        bid.teller_card_state == ApprovalStatus.approved
        or bid.teller_cash_state == ApprovalStatus.approved
    ):
        separator = "\n" + separator + "\n"
        stage = str.join(separator, (stage, "Выплачено"))

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
