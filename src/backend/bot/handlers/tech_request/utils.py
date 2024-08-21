import logging
from typing import Optional
from bot.states import Base
from settings import get_settings

from aiogram.types import (
    CallbackQuery,
    InputMediaDocument,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from bot import text

from db.models import ApprovalStatus
from db.service import get_technical_request_by_id
from db.schemas import DepartmentSchema

from bot.handlers.utils import (
    try_delete_message,
    try_edit_or_answer,
)
from bot.kb import create_inline_keyboard, create_reply_keyboard
from bot.handlers.tech_request.schemas import (
    ShowRequestCallbackData,
)


async def show_form(
    state: FSMContext,
    callback_data: ShowRequestCallbackData,
    history_or_waiting_button: InlineKeyboardButton,
    buttons: list[list[InlineKeyboardButton]],
    callback: Optional[CallbackQuery] = None,
    message: Optional[Message] = None,
):
    data = await state.get_data()
    if "msgs" in data:
        for msg in data["msgs"]:
            await try_delete_message(msg)
        await state.update_data(msgs=[])

    request = get_technical_request_by_id(callback_data.request_id)
    text_form = (
        f"{hbold(request.problem.problem_name)} от "
        + request.open_date.date().strftime(get_settings().date_format)
        + f"\nОписание:\n{request.description}\n\
Адрес: {request.worker.department.address}\n\
ФИО сотрудника: {request.worker.l_name} {request.worker.f_name} {request.worker.o_name}\n\
Номер телефона: {request.worker.phone_number}\n\
Должность: {request.worker.post.name}\n\
ФИО исполнителя: {request.repairman.l_name} {request.repairman.f_name} {request.repairman.o_name}\n\
Статус: "
    )

    match request.state:
        case ApprovalStatus.approved:
            text_form += "Выполнено"
        case ApprovalStatus.pending:
            text_form += "В процессе выполнения"
        case ApprovalStatus.pending_approval:
            text_form += "Ожидание оценки от ТУ"
        case ApprovalStatus.denied:
            text_form += "Отправлено на доработку"
        case ApprovalStatus.skipped:
            text_form += "Не выполнено"
    text_form += "\n \n"

    if request.repair_date:
        text_form += (
            "Дата ремонта "
            + request.repair_date.date().strftime(get_settings().date_format)
            + "\n"
        )
    if request.confirmation_date:
        text_form += (
            "Дата утверждения проделанной работы "
            + request.confirmation_date.date().strftime(get_settings().date_format)
            + "\n"
        )
        if request.reopen_date:
            text_form += (
                "Дата переоткрытия заявки "
                + request.reopen_date.date().strftime(get_settings().date_format)
                + "\n"
            )
            if request.confirmation_description:
                text_form += (
                    "Комментарий ТУ: " + request.confirmation_description + "\n"
                )
        if request.reopen_repair_date:
            text_form += (
                "Повторная дата ремонта "
                + request.reopen_repair_date.date().strftime(get_settings().date_format)
                + "\n"
            )
        if request.reopen_confirmation_date:
            text_form += (
                "Повторная дата утверждения "
                + request.reopen_confirmation_date.date().strftime(
                    get_settings().date_format
                )
                + "\n"
            )
            if request.close_description:
                text_form += "Комментарий ТУ: " + request.close_description + "\n"

        if request.close_date:
            text_form += (
                "Дата закрытия заявки "
                + request.close_date.date().strftime(get_settings().date_format)
                + "\n"
            )

    buttons.append(
        [
            InlineKeyboardButton(
                text="Фотографии поломки",
                callback_data=ShowRequestCallbackData(
                    request_id=request.id,
                    end_point="TR_problem_docs",
                    last_end_point=callback_data.end_point,
                ).pack(),
            )
        ]
    )

    if request.repair_date:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Фотографии ремонта",
                    callback_data=ShowRequestCallbackData(
                        request_id=request.id,
                        end_point="TR_repair_docs",
                        last_end_point=callback_data.end_point,
                    ).pack(),
                )
            ]
        )

    if request.reopen_repair_date:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Фотографии повторного ремонта",
                    callback_data=ShowRequestCallbackData(
                        request_id=request.id,
                        end_point="TR_reopen_repair_docs",
                        last_end_point=callback_data.end_point,
                    ).pack(),
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=text.back, callback_data=history_or_waiting_button.callback_data
            )
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    if callback:
        await try_edit_or_answer(
            message=callback.message, text=text_form, reply_markup=keyboard
        )
    else:
        await try_edit_or_answer(message=message, text=text_form, reply_markup=keyboard)


async def send_photos(
    callback: CallbackQuery,
    state: FSMContext,
    callback_data: ShowRequestCallbackData,
    media: list[InputMediaDocument],
    request_id: int,
):
    await try_delete_message(callback.message)
    msgs = await callback.message.answer_media_group(media=media)
    await state.update_data(msgs=msgs)
    await msgs[0].reply(
        text=hbold("Выберите действие:"),
        reply_markup=create_inline_keyboard(
            InlineKeyboardButton(
                text=text.back,
                callback_data=ShowRequestCallbackData(
                    request_id=request_id,
                    end_point=callback_data.last_end_point,
                ).pack(),
            )
        ),
    )


async def handle_department(
    message: Message,
    state: FSMContext,
    departments_names: list[str],
    reply_markup: InlineKeyboardMarkup,
) -> bool | None:
    """
    Return True if message == '⏪ Назад' else answer on message
    """
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await try_delete_message(msg)
    await try_delete_message(message)

    if message.text == text.back:
        await state.set_state(Base.none)
        return True
    else:
        if message.text not in departments_names:
            departments_names.sort()
            msg = await message.answer(
                text=text.format_err,
                reply_markup=create_reply_keyboard(text.back, *departments_names),
            )
            await state.update_data(msg=msg)
            return

        await state.update_data(department_name=message.text)
        await message.answer(
            text=hbold(f"Производство: {message.text}"),
            reply_markup=reply_markup,
        )
        await state.set_state(Base.none)
