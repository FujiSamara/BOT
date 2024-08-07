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


def create_keybord_with_end_point(
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
    text = f"{hbold(request.problem.problem_name)} от {request.open_date.date()}. \n\
Описание:\n{request.description} \n\
Адресс: {request.worker.department.address}\n\
ФИО сотрудника: {request.worker.l_name} {request.worker.f_name} {request.worker.o_name}.\n\
ФИО исполнителя: {request.repairman.l_name} {request.repairman.f_name} {request.repairman.o_name}.\n\
Статус: "

    match request.state:
        case ApprovalStatus.approved:
            text += "Выполенно."
        case ApprovalStatus.pending:
            text += "В процессе выполнения."
        case ApprovalStatus.pending_approval:
            text += "Ожидание оценки от ТУ."
        case ApprovalStatus.denied:
            text += "Отправленно на доработку."
    text += "\n"

    if request.confirmation_date:
        text += f"Дата утверждения проделанной работы {request.confirmation_date.strftype("%d.%m.%Y")}.\n"
        if request.close_date:
            text += f"Дата закрытия заявки {request.close_date.strftype("%d.%m.%Y")}.\n"
        if request.reopen_date:
            text += (
                f"Дата переоткрытия заявки {request.reopen_date.strftype("%d.%m.%Y")}."
            )

    buttons.append(
        [InlineKeyboardButton(text="Назад", callback_data=history_button.callback_data)]
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

    if request.state == ApprovalStatus.pending_approval:
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
