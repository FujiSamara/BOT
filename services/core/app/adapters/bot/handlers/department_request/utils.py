from typing import Optional
from app.adapters.bot.states import Base
from app.infra.config import settings

from aiogram.types import (
    CallbackQuery,
    InputMediaDocument,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from app.adapters.bot import text

from app.infra.database.models import ApprovalStatus
from app.services import (
    get_technical_request_by_id,
    get_cleaning_request_by_id,
    get_request_count_in_departments_by_tg_id,
    get_request_count_in_departments,
)

from app.adapters.bot.handlers.utils import (
    try_delete_message,
    try_edit_or_answer,
)
from app.adapters.bot.kb import (
    create_inline_keyboard,
    create_reply_keyboard,
    main_menu_button,
)
from app.adapters.bot.handlers.department_request.schemas import (
    ShowRequestCallbackData,
    RequestType,
)

from app.schemas import DepartmentSchema


def get_departments_names_executor(
    tg_id: int, type: RequestType
) -> list[DepartmentSchema]:
    import app.services as s

    match type.name:
        case RequestType.TR.name:
            return s.get_departments_names_for_repairman(tg_id)
        case RequestType.CR.name:
            return s.get_departments_names_for_cleaner(tg_id)
    return []


async def show_form_technician(
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
        + request.open_date.date().strftime(settings.date_format)
        + f"\nОписание:\n{request.description}\n\
Адрес: {request.department.address}\n\
ФИО сотрудника: {request.worker.l_name} {request.worker.f_name} {request.worker.o_name}\n\
Номер телефона: {request.worker.phone_number}\n\
Должность: {request.worker.post.name}\n\
ФИО исполнителя: {request.repairman.l_name} {request.repairman.f_name} {request.repairman.o_name}\n\
Номер телефона: {request.repairman.phone_number}\n\
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
        case ApprovalStatus.not_relevant:
            text_form += "Не актуально"

    text_form += "\n \n"

    if request.repair_date:
        text_form += (
            "Дата ремонта: "
            + request.repair_date.date().strftime(settings.date_format)
            + "\n"
        )
    if request.confirmation_date:
        text_form += (
            "Дата утверждения проделанной работы: "
            + request.confirmation_date.date().strftime(settings.date_format)
            + "\n"
        )
        if request.confirmation_description:
            text_form += "Комментарий ТУ: " + request.confirmation_description + "\n \n"

        if request.reopen_date:
            text_form += (
                "Дата переоткрытия заявки: "
                + request.reopen_date.date().strftime(settings.date_format)
                + "\n"
            )
        if request.reopen_repair_date:
            text_form += (
                "Повторная дата ремонта: "
                + request.reopen_repair_date.date().strftime(settings.date_format)
                + "\n"
            )
        if request.reopen_confirmation_date:
            text_form += (
                "Повторная дата утверждения: "
                + request.reopen_confirmation_date.date().strftime(settings.date_format)
                + "\n"
            )
        if request.score:
            text_form += f"\nОценка проделанной работы: {request.score}\n"

    if request.close_description:
        text_form += (
            "Комментарий при закрытие заявки: " + request.close_description + "\n \n"
        )

    if request.close_date:
        text_form += (
            "Дата закрытия заявки: "
            + request.close_date.date().strftime(settings.date_format)
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
    if "department_name" in data or "WR" in callback_data.end_point:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=text.back,
                    callback_data=history_or_waiting_button.callback_data,
                )
            ]
        )
    else:
        buttons.append([main_menu_button])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    if callback:
        await try_edit_or_answer(
            message=callback.message, text=text_form, reply_markup=keyboard
        )
    else:
        await try_edit_or_answer(message=message, text=text_form, reply_markup=keyboard)


async def show_form_cleaning(
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

    request = get_cleaning_request_by_id(callback_data.request_id)
    text_form = (
        f"{hbold(request.problem.problem_name)} от "
        + request.open_date.date().strftime(settings.date_format)
        + f"\nОписание:\n{request.description}\n\
Адрес: {request.worker.department.address}\n\
ФИО сотрудника: {request.worker.l_name} {request.worker.f_name} {request.worker.o_name}\n\
Номер телефона: {request.worker.phone_number}\n\
Должность: {request.worker.post.name}\n\
ФИО исполнителя: {request.cleaner.l_name} {request.cleaner.f_name} {request.cleaner.o_name}\n\
Номер телефона: {request.cleaner.phone_number}\n\
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
        case ApprovalStatus.not_relevant:
            text_form += "Не актуально"

    text_form += "\n \n"

    if request.cleaning_date:
        text_form += (
            "Дата клининга: "
            + request.cleaning_date.date().strftime(settings.date_format)
            + "\n"
        )
    if request.confirmation_date:
        text_form += (
            "Дата утверждения проделанной работы: "
            + request.confirmation_date.date().strftime(settings.date_format)
            + "\n"
        )
        if request.confirmation_description:
            text_form += "Комментарий ТУ: " + request.confirmation_description + "\n \n"

        if request.reopen_date:
            text_form += (
                "Дата переоткрытия заявки: "
                + request.reopen_date.date().strftime(settings.date_format)
                + "\n"
            )
        if request.reopen_cleaning_date:
            text_form += (
                "Повторная дата клининга: "
                + request.reopen_cleaning_date.date().strftime(settings.date_format)
                + "\n"
            )
        if request.reopen_confirmation_date:
            text_form += (
                "Повторная дата утверждения: "
                + request.reopen_confirmation_date.date().strftime(settings.date_format)
                + "\n"
            )
            if request.close_description:
                text_form += "Комментарий ТУ: " + request.close_description + "\n \n"

        if request.close_date:
            text_form += (
                "Дата закрытия заявки: "
                + request.close_date.date().strftime(settings.date_format)
                + "\n"
            )

        if request.score:
            text_form += f"\nОценка проделанной работы: {request.score}\n"

    buttons.append(
        [
            InlineKeyboardButton(
                text="Фотографии проблемы",
                callback_data=ShowRequestCallbackData(
                    request_id=request.id,
                    end_point=f"{RequestType.CR.name}_problem_docs",
                    last_end_point=callback_data.end_point,
                ).pack(),
            )
        ]
    )

    if request.cleaning_date:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Фотографии клининга",
                    callback_data=ShowRequestCallbackData(
                        request_id=request.id,
                        end_point=f"{RequestType.CR.name}_repair_docs",
                        last_end_point=callback_data.end_point,
                    ).pack(),
                )
            ]
        )

    if request.reopen_cleaning_date:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Фотографии повторного клининга",
                    callback_data=ShowRequestCallbackData(
                        request_id=request.id,
                        end_point=f"{RequestType.CR.name}_reopen_docs",
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
            msg = await message.answer(
                text=text.format_err,
                reply_markup=create_reply_keyboard(text.back, *departments_names),
            )
            await state.update_data(msg=msg)
            return
        department_name = " ".join(message.text.split(" ")[1:])
        await state.update_data(department_name=department_name)
        await message.answer(
            text=hbold(f"Предприятие: {department_name}"),
            reply_markup=reply_markup,
        )
        await state.set_state(Base.none)


def department_names_with_count(
    state: ApprovalStatus,
    department_names: list[str],
    tg_id: int | None = None,
    type: RequestType = RequestType.TR,
) -> list[str]:
    from app.infra.database.models import TechnicalRequest, CleaningRequest

    model = TechnicalRequest if type == RequestType.TR else CleaningRequest
    if department_names == []:
        return []
    if tg_id is not None:
        request_count = get_request_count_in_departments_by_tg_id(
            state=state, tg_id=tg_id, model=model
        )
    else:
        request_count = get_request_count_in_departments(state=state, model=model)
    out_department_names = []
    if len(department_names) > 0:
        for department_name, count in request_count:
            out_department_names.append(f"{count} {department_name}")
            if department_name in department_names:
                department_names.remove(department_name)
        for department_name in department_names:
            out_department_names.append(f"0 {department_name}")

        out_department_names.sort(reverse=True)
    return out_department_names
