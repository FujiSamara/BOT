from typing import Awaitable, Callable, Optional, Any
import asyncio
from aiogram.types import (
    ReplyKeyboardRemove,
    Message,
    ContentType,
    InputMediaDocument,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
from db.schemas import (
    ProblemITSchema,
    BidITSchema,
)
from bot.states import Base
from bot.text import bid_create_greet
from bot.handlers.utils import (
    try_edit_message,
    try_delete_message,
)
from db.service import get_bid_it_by_id
from db.models import ApprovalStatus
from bot.kb import (
    get_create_tm_bid_it_menu,
    get_create_repairman_it_menu,
)


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
        f"{hbold(bid.problem.problem)} от "
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
                text_form += "Комментарий ТУ: " + bid.confirmation_description + "\n"
        # if bid.reopen_repair_date:
        #     text_form += (
        #         "Повторная дата ремонта "
        #         + bid.reopening_repair_date.strftime('%d.%m.%Y')
        #         + "\n"
        #     )
        # if bid.reopen_approve_date:
        #     text_form += (
        #         "Повторная дата утверждения "
        #         + bid.reopen_approve_date.strftime('%d.%m.%Y')
        #         + "\n"
        #     )
        # if bid.reopen_work_comment:
        #     text_form += "Комментарий ТУ: " + bid.reopen_work_comment + "\n"

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
    bid = get_bid_it_by_id((await state.get_data()).get("bid_id"))
    problem_text = get_bid_it_info(bid)
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


async def handle_documents(
    message: Message,
    state: FSMContext,
    document_name: str,
    on_complete: Callable[[Any, Any], Awaitable[Any]],
):
    if message.content_type == ContentType.TEXT:
        if message.text == "Готово":
            data = await state.get_data()
            msgs = data.get("msgs")
            documents = data.get("documents")
            if msgs:
                for msg in msgs:
                    await try_delete_message(msg)
                await state.update_data(msgs=[])
            if documents:
                specified_documents = data.get(document_name)
                if not specified_documents:
                    specified_documents = []
                specified_documents.extend(documents)
                await state.update_data(documents=[])
                await state.update_data({document_name: specified_documents})
            msg = data.get("msg")
            if msg:
                await try_delete_message(msg)
            await try_delete_message(message)
            await on_complete(message, state)
        elif message.text == "Сбросить":
            data = await state.get_data()
            msgs = data.get("msgs")
            documents = data.get("documents")
            if msgs:
                for msg in msgs:
                    await try_delete_message(msg)
                await state.update_data(msgs=[])
            await state.update_data(documents=[])
            await state.update_data({document_name: []})
            msg = data.get("msg")
            if msg:
                await try_delete_message(msg)
            await try_delete_message(message)
            await on_complete(message, state)
        else:
            await try_delete_message(message)
            msg = await message.answer("Отправьте документ или фото!")
            await asyncio.sleep(1)
            await try_delete_message(msg)
    elif (
        message.content_type == ContentType.DOCUMENT
        or message.content_type == ContentType.PHOTO
    ):
        data = await state.get_data()
        documents: list = data.get("documents")
        msgs: list = data.get("msgs")
        if not documents:
            documents = []
        if message.content_type == ContentType.PHOTO:
            documents.append(message.photo[-1])
        else:
            documents.append(message.document)
        if not msgs:
            msgs = []
        msgs.append(message)
        await state.update_data(msgs=msgs, documents=documents)
    else:
        await try_delete_message(message)
        msg = await message.answer("Отправьте документ или фото!")
        await asyncio.sleep(1)
        await try_delete_message(msg)


async def clear_state_with_success_rm(
    message: Message, state: FSMContext, sleep_time=1, edit=False
):
    ans = await message.answer(hbold("Успешно!"), reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(sleep_time)
    await ans.delete()
    await state.set_state(Base.none)
    bid_id = (await state.get_data()).get("bid_id")
    bid = get_bid_it_by_id(bid_id)
    text = get_bid_it_info(bid)

    if edit:
        await try_edit_message(
            message=message,
            text=hbold(bid_create_greet) + "\n" + text,
            reply_markup=await get_create_repairman_it_menu(state),
        )
    else:
        await message.answer(
            text=hbold(bid_create_greet) + "\n" + text,
            reply_markup=await get_create_repairman_it_menu(state),
        )


def filter_media_by_reopen(media: list[InputMediaDocument]) -> None:
    rm = [doc for doc in media if doc.media.filename.find("reopen") == -1]
    if len(rm) == len(media):
        return
    for doc in rm:
        media.remove(doc)
