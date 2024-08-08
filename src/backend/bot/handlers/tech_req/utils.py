from settings import get_settings

from aiogram.types import (
    CallbackQuery,
    InputMediaDocument,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from db.models import ApprovalStatus
from db.service import get_technical_request_by_id
from db.schemas import TechnicalRequestSchema

from bot.handlers.utils import (
    try_delete_message,
    try_edit_or_answer,
)
from bot.kb import create_inline_keyboard
from bot.handlers.tech_req.schemas import (
    ShowRequestCallbackData,
)


def create_keybord_for_requests_with_end_point(
    requests: list[TechnicalRequestSchema],
    end_point: str,
    menu_button: InlineKeyboardButton,
) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []
    try:
        for request in requests:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=request.open_date.date().strftime(
                            get_settings().date_format
                        ),
                        callback_data=ShowRequestCallbackData(
                            request_id=request.id, end_point=end_point
                        ).pack(),
                    )
                ]
            )
    finally:
        buttons.append([menu_button])
        return InlineKeyboardMarkup(inline_keyboard=buttons)


async def show_form(
    callback: CallbackQuery,
    state: FSMContext,
    callback_data: ShowRequestCallbackData,
    history_button: InlineKeyboardButton,
    buttons: list[list[InlineKeyboardButton]],
):
    data = await state.get_data()
    if "msgs" in data:
        for msg in data["msgs"]:
            await try_delete_message(msg)
        await state.update_data(msgs=[])

    request = get_technical_request_by_id(callback_data.request_id)
    text = (
        f"{hbold(request.problem.problem_name)} от "
        + request.open_date.date().strftime(get_settings().date_format)
        + f"\nОписание:\n{request.description}\n\
Адресс: {request.worker.department.address}\n\
ФИО сотрудника: {request.worker.l_name} {request.worker.f_name} {request.worker.o_name}\n\
ФИО исполнителя: {request.repairman.l_name} {request.repairman.f_name} {request.repairman.o_name}\n\
Статус: "
    )

    match request.state:
        case ApprovalStatus.approved:
            text += "Выполенно"
        case ApprovalStatus.pending:
            text += "В процессе выполнения"
        case ApprovalStatus.pending_approval:
            text += "Ожидание оценки от ТУ"
        case ApprovalStatus.denied:
            text += "Отправленно на доработку"
        case ApprovalStatus.skipped:
            text += "Не выполненно"
    text += "\n \n"

    if request.confirmation_date:
        text += (
            "Дата утверждения проделанной работы "
            + request.confirmation_date.date().strftime(get_settings().date_format)
            + "\n"
        )
        if request.close_date:
            text += (
                "Дата закрытия заявки "
                + request.close_date.date().strftime(get_settings().date_format)
                + "\n"
            )
        if request.reopen_date:
            text += (
                "Дата переоткрытия заявки "
                + request.reopen_date.date().strftime(get_settings().date_format)
                + "\n"
            )
        if request.reopen_repair_date:
            text += (
                "Повторная дата ремонта "
                + request.reopen_repair_date.date().strftime(get_settings().date_format)
                + "\n"
            )
        if request.reopen_confirmation_date:
            text += (
                "Повторная дата утверждения "
                + request.reopen_confirmation_date.date().strftime(
                    get_settings().date_format
                )
                + "\n"
            )

    buttons.append(
        [
            InlineKeyboardButton(
                text="Фотографии поломки",
                callback_data=ShowRequestCallbackData(
                    request_id=request.id,
                    end_point="problem_docs",
                    last_end_point=callback_data.end_point,
                ).pack(),
            )
        ]
    )

    if request.repair_date:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Фотогарфии ремонта",
                    callback_data=ShowRequestCallbackData(
                        request_id=request.id,
                        end_point="repair_docs",
                        last_end_point=callback_data.end_point,
                    ).pack(),
                )
            ]
        )

    buttons.append(
        [InlineKeyboardButton(text="Назад", callback_data=history_button.callback_data)]
    )

    keybord = InlineKeyboardMarkup(inline_keyboard=buttons)
    await try_edit_or_answer(message=callback.message, text=text, reply_markup=keybord)


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
                text="Назад",
                callback_data=ShowRequestCallbackData(
                    request_id=request_id,
                    end_point=callback_data.last_end_point,
                ).pack(),
            )
        ),
    )
