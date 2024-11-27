from typing import Optional
import asyncio
from aiogram.types import (
    ReplyKeyboardRemove,
    Message,
    InputMediaDocument,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
from app.bot.handlers.bids_it.schemas import (
    BidITCallbackData,
    BidITViewMode,
)
from app.db.schemas import (
    ProblemITSchema,
    BidITSchema,
)
from app.bot.states import Base
from app.bot.handlers.utils import (
    try_edit_message,
)
from app.db.service import get_bid_it_by_id
from app.db.models import ApprovalStatus
from app.bot.handlers.bids_it.kb import (
    get_create_tm_bid_it_menu,
    get_create_repairman_it_menu,
)


def get_id_by_problem_type(
    problem_type: str, problems: list[ProblemITSchema]
) -> Optional[int]:
    for problem in problems:
        if problem_type == problem.name:
            return problem.id
    return None


def get_bid_it_list_info(bid: BidITSchema) -> str:
    return (
        f"{bid.id}: {bid.worker.l_name} "
        + f"{bid.opening_date.strftime('%d.%m.%Y')} {bid.problem.name}"
    )


def get_bid_it_state_info(bid: BidITSchema) -> str:
    stage = ""

    match bid.status:
        case ApprovalStatus.pending:
            stage = "В ожидании у IT специалиста"
        case ApprovalStatus.approved:
            stage = "Выполнено"
        case ApprovalStatus.pending_approval:
            stage = "В ожидании оценки ТУ"
        case ApprovalStatus.denied:
            stage = "Отправлено на доработку"
        case ApprovalStatus.skipped:
            stage = "Не выполнено"
    return stage


def get_bid_it_info(bid: BidITSchema) -> str:
    text_form = (
        f"{hbold(bid.problem.name)} от "
        + bid.opening_date.strftime("%d.%m.%Y")
        + f"\nОписание:\n{bid.problem_comment}\n\
Адрес: {bid.worker.department.address}\n\
ФИО сотрудника: {bid.worker.l_name} {bid.worker.f_name} {bid.worker.o_name}\n\
Номер телефона: {bid.worker.phone_number}\n\
Должность: {bid.worker.post.name}\n\
ФИО исполнителя: {bid.repairman.l_name} {bid.repairman.f_name} {bid.repairman.o_name}\n\
Статус: "
    )

    text_form += get_bid_it_state_info(bid)
    text_form += "\n \n"

    if bid.done_date:
        text_form += "Дата ремонта " + bid.done_date.strftime("%d.%m.%Y") + "\n"
    if bid.approve_date:
        text_form += (
            "Дата утверждения проделанной работы "
            + bid.approve_date.strftime("%d.%m.%Y")
            + "\n"
        )
        if bid.reopening_date:
            text_form += (
                "Дата переоткрытия заявки "
                + bid.reopening_date.strftime("%d.%m.%Y")
                + "\n"
            )
            if bid.work_comment:
                text_form += "Комментарий ТУ: " + bid.work_comment + "\n"
        if bid.reopen_done_date:
            text_form += (
                "Повторная дата ремонта "
                + bid.reopen_done_date.strftime("%d.%m.%Y")
                + "\n"
            )
        if bid.reopen_approve_date:
            text_form += (
                "Повторная дата утверждения "
                + bid.reopen_approve_date.strftime("%d.%m.%Y")
                + "\n"
            )
        if bid.reopen_work_comment:
            text_form += "Комментарий ТУ: " + bid.reopen_work_comment + "\n"

        if bid.close_date:
            text_form += (
                "Дата закрытия заявки " + bid.close_date.strftime("%d.%m.%Y") + "\n"
            )

    return text_form


async def clear_state_with_success_it_tm(
    message: Message, state: FSMContext, sleep_time=1, edit=False
):
    ans = await message.answer(hbold("Успешно!"), reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(sleep_time)
    await ans.delete()
    await state.set_state(Base.none)
    data = await state.get_data()
    bid = get_bid_it_by_id(data.get("bid_id"))
    problem_text = get_bid_it_info(bid)
    callback_data = BidITCallbackData(
        id=data.get("bid_id"),
        mode=BidITViewMode.pending,
        endpoint_name="create_bid_it_info_tm",
    )
    if edit:
        await try_edit_message(
            message=message,
            text=problem_text,
            reply_markup=await get_create_tm_bid_it_menu(callback_data, state),
        )
    else:
        await message.answer(
            text=problem_text,
            reply_markup=await get_create_tm_bid_it_menu(callback_data, state),
        )


async def clear_state_with_success_rm_work(
    message: Message, state: FSMContext, sleep_time=1, edit=False
):
    ans = await message.answer(hbold("Успешно!"), reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(sleep_time)
    await ans.delete()
    await state.set_state(Base.none)
    data = await state.get_data()
    bid_id = data.get("bid_id")
    bid = get_bid_it_by_id(bid_id)
    text = get_bid_it_info(bid)

    callback_data = BidITCallbackData(
        id=data.get("bid_id"),
        mode=BidITViewMode.pending,
        endpoint_name="create_bid_it_info_rm",
    )

    if edit:
        await try_edit_message(
            message=message,
            text=text,
            reply_markup=await get_create_repairman_it_menu(callback_data, state),
        )
    else:
        await message.answer(
            text=text,
            reply_markup=await get_create_repairman_it_menu(callback_data, state),
        )


async def clear_state_with_success_rm_rework(
    message: Message, state: FSMContext, sleep_time=1, edit=False
):
    ans = await message.answer(hbold("Успешно!"), reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(sleep_time)
    await ans.delete()
    await state.set_state(Base.none)
    data = await state.get_data()
    bid_id = data.get("bid_id")
    bid = get_bid_it_by_id(bid_id)
    text = get_bid_it_info(bid)

    callback_data = BidITCallbackData(
        id=data.get("bid_id"),
        mode=BidITViewMode.deny,
        endpoint_name="create_bid_it_info_rm",
    )

    if edit:
        await try_edit_message(
            message=message,
            text=text,
            reply_markup=await get_create_repairman_it_menu(callback_data, state),
        )
    else:
        await message.answer(
            text=text,
            reply_markup=await get_create_repairman_it_menu(callback_data, state),
        )


def filter_media_by_reopen(media: list[InputMediaDocument]) -> None:
    rm = [doc for doc in media if doc.media.filename.find("reopen") == -1]
    if len(rm) == len(media):
        return
    for doc in rm:
        media.remove(doc)


def filter_media_by_done(media: list[InputMediaDocument]) -> None:
    rm = [doc for doc in media if doc.media.filename.find("reopen") != -1]
    if len(rm) == len(media):
        return
    for doc in rm:
        media.remove(doc)


def create_buttons_for_repairman(
    buttons, bid_it: BidITSchema, callback_data: BidITCallbackData
):
    buttons.append(
        [
            InlineKeyboardButton(
                text="Показать фото проблемы",
                callback_data=BidITCallbackData(
                    id=bid_it.id,
                    mode=callback_data.mode,
                    endpoint_name="create_documents_problem_rm",
                ).pack(),
            )
        ]
    )
    if bid_it.done_date:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Показать фото выполненной работы",
                    callback_data=BidITCallbackData(
                        id=bid_it.id,
                        mode=callback_data.mode,
                        endpoint_name="create_documents_done_rm",
                    ).pack(),
                )
            ]
        )
    if bid_it.reopen_done_date:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Показать фото переделанной работы",
                    callback_data=BidITCallbackData(
                        id=bid_it.id,
                        mode=callback_data.mode,
                        endpoint_name="create_documents_done_reopen_rm",
                    ).pack(),
                )
            ]
        )


def create_buttons_for_worker(
    buttons, bid_it: BidITSchema, callback_data: BidITCallbackData
):
    buttons.append(
        [
            InlineKeyboardButton(
                text="Показать фото проблемы",
                callback_data=BidITCallbackData(
                    id=bid_it.id,
                    mode=callback_data.mode,
                    endpoint_name="create_documents_problem",
                ).pack(),
            )
        ]
    )
    if bid_it.done_date:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Показать фото выполненной работы",
                    callback_data=BidITCallbackData(
                        id=bid_it.id,
                        mode=callback_data.mode,
                        endpoint_name="create_documents_done",
                    ).pack(),
                )
            ]
        )
    if bid_it.reopen_done_date:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Показать фото переделанной работы",
                    callback_data=BidITCallbackData(
                        id=bid_it.id,
                        mode=callback_data.mode,
                        endpoint_name="create_documents_done_reopen",
                    ).pack(),
                )
            ]
        )


def create_buttons_for_territorial_manager(
    buttons, bid_it: BidITSchema, callback_data: BidITCallbackData
):
    buttons.append(
        [
            InlineKeyboardButton(
                text="Показать фото проблемы",
                callback_data=BidITCallbackData(
                    id=bid_it.id,
                    mode=callback_data.mode,
                    endpoint_name="create_documents_problem_tm",
                ).pack(),
            )
        ]
    )
    if bid_it.done_date:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Показать фото выполненной работы",
                    callback_data=BidITCallbackData(
                        id=bid_it.id,
                        mode=callback_data.mode,
                        endpoint_name="create_documents_done_tm",
                    ).pack(),
                )
            ]
        )
    if bid_it.reopen_done_date:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Показать фото переделанной работы",
                    callback_data=BidITCallbackData(
                        id=bid_it.id,
                        mode=callback_data.mode,
                        endpoint_name="create_documents_done_reopen_tm",
                    ).pack(),
                )
            ]
        )
