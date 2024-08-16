from typing import Optional
import asyncio
from aiogram.types import (
    ReplyKeyboardRemove,
    Message,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
from db.schemas import (
    ProblemITSchema,
    BidITSchema,
)
from bot.states import Base
from bot.handlers.utils import (
    try_edit_message,
)
from db.service import get_bid_it_by_id
from db.models import ApprovalStatus
from bot.kb import get_create_tm_bid_it_menu

def get_id_by_problem_type(
    problem_type: str, problems: list[ProblemITSchema]
) -> Optional[int]:
    for problem in problems:
        if problem_type == problem.problem:
            return problem.id
    return None


def get_bid_it_list_info(bid: BidITSchema) -> str:
    return (
        f"{bid.id}: {bid.worker.l_name} "
        + f"{bid.opening_date.strftime('%d.%m.%Y')} {bid.problem.problem}"
    )


def get_full_bid_it_info(bid: BidITSchema) -> str:
    stage = ""

    if bid.status == ApprovalStatus.pending:
        stage = "В ожидании у ответственного специалиста"
    elif bid.status == ApprovalStatus.approved:
        stage = "Выполнена"
    elif bid.status == ApprovalStatus.pending_approval:
        stage = "В ожидании оценки ТУ"
    elif bid.status == ApprovalStatus.denied:
        stage = "Работа специалиста не прошла проверку ТУ. В ожидании у ответственного специалиста"

    bid_info = f"""{hbold("Номер заявки")}: {bid.id}
{hbold("Проблема")}: {bid.problem.problem}
{hbold("Описание проблемы")}: {bid.problem_comment}
{hbold("Фото")}: Прикреплено к сообщению.
{hbold("Дата создания")}: {bid.opening_date.strftime('%d.%m.%Y')}
{hbold("Текущий этап")}: {stage}
"""

    return bid_info


def get_bid_it_state_info(bid: BidITSchema) -> str:
    stage = "На согласовании у "

    if bid.status == ApprovalStatus.pending_approval:
        stage += "ТУ"
    elif bid.status == ApprovalStatus.pending:
        stage += "ответственного специалиста"
    # elif (
    #     bid.kru_state == ApprovalStatus.denied
    # ):
    #     stage = "Отказано"
    else:
        stage = "Выполнено"

    return stage


def get_full_bid_it_info_tm(bid: BidITSchema) -> str:
    stage = ""

    if bid.status == ApprovalStatus.pending:
        stage = "В ожидании у ответственного специалиста"
    elif bid.status == ApprovalStatus.approved:
        stage = "Выполнена"
    elif bid.status == ApprovalStatus.pending_approval:
        stage = "В ожидании оценки ТУ"
    elif bid.status == ApprovalStatus.denied:
        stage = "Работа специалиста не прошла проверку ТУ. В ожидании у ответственного специалиста"

    bid_info = f"""{hbold("Номер заявки")}: {bid.id}
{hbold("Проблема")}: {bid.problem.problem}
{hbold("Описание проблемы")}: {bid.problem_comment}
{hbold("Фото проблемы")}: Прикреплено к сообщению.
{hbold("Фото выполненной работы")}: Прикреплено к сообщению.
{hbold("Дата создания")}: {bid.opening_date.strftime('%d.%m.%Y')}
{hbold("Текущий этап")}: {stage}
"""

    return bid_info


def get_short_bid_it_info(bid: BidITSchema) -> str:
    return f"""Заявка {bid.id} от {bid.opening_date.date()}: {bid.problem.problem}.
Статус: {get_bid_it_state_info(bid)}"""


async def clear_state_with_success_it_tm(
    message: Message, state: FSMContext, sleep_time=1, edit=False
):
    ans = await message.answer(hbold("Успешно!"), reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(sleep_time)
    await ans.delete()
    await state.set_state(Base.none)
    bid = get_bid_it_by_id((await state.get_data()).get("bid_id"))
    problem_text = get_full_bid_it_info_tm(bid)
    if edit:
        await try_edit_message(
            message=message,
            text=f"Выполненная заявка:\n{problem_text}",
            reply_markup=await get_create_tm_bid_it_menu(state),
        )
    else:
        await message.answer(
            text=f"Выполненная заявка:\n{problem_text}",
            reply_markup=await get_create_tm_bid_it_menu(state),
        )
