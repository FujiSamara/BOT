from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
)

from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from app.adapters.bot import text, kb
from app.adapters.bot.states import (
    Base,
    TerritorialDirectorRequestForm,
)
from asyncio import sleep
from app.adapters.bot.handlers.tech_request.utils import (
    handle_department,
    show_form,
    department_names_with_count,
)
from app.adapters.bot.handlers.tech_request.schemas import ShowRequestCallbackData
from app.adapters.bot.handlers.tech_request import kb as tech_kb
from app.adapters.bot.handlers.utils import (
    try_delete_message,
    try_edit_or_answer,
)


from app.services.technical_request import (
    get_departments_names_for_territorial_director,
    get_all_pending_technical_requests_for_territorial_director,
    get_all_history_technical_requests_territorial_director,
    update_technical_request_by_territorial_director,
)

from app.infra.database.models import ApprovalStatus


router = Router(name="technical_request_territorial_director")


@router.callback_query(F.data == tech_kb.td_button.callback_data)
async def show_tech_req_menu(message: CallbackQuery | Message):
    if isinstance(message, CallbackQuery):
        message = message.message
    await try_edit_or_answer(
        message=message,
        text=hbold(tech_kb.td_button.text),
        reply_markup=tech_kb.td_change_department_menu,
    )


@router.callback_query(F.data == tech_kb.td_change_department_button.callback_data)
async def change_department(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TerritorialDirectorRequestForm.department)
    department_names = department_names_with_count(
        state=ApprovalStatus.not_relevant,
        department_names=get_departments_names_for_territorial_director(
            callback.message.chat.id
        ),
    )

    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите предприятие:"),
        reply_markup=kb.create_reply_keyboard(text.back, *department_names),
    )
    await state.update_data(msg=msg)


@router.message(TerritorialDirectorRequestForm.department)
async def set_department(message: Message, state: FSMContext):
    department_names = department_names_with_count(
        state=ApprovalStatus.not_relevant,
        department_names=get_departments_names_for_territorial_director(
            message.chat.id
        ),
    )

    if await handle_department(
        message=message,
        state=state,
        departments_names=department_names,
        reply_markup=tech_kb.td_menu_markup,
    ):
        await show_tech_req_menu(message)


@router.callback_query(F.data == tech_kb.td_menu_button.callback_data)
async def show_menu(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f"Предприятие: {department_name}"),
        reply_markup=tech_kb.td_menu_markup,
    )


@router.callback_query(F.data == tech_kb.td_history.callback_data)
async def show_history_menu(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    requests = get_all_history_technical_requests_territorial_director(
        department_name=department_name
    )

    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("История заявок"),
        reply_markup=tech_kb.create_kb_with_end_point(
            end_point="TD_TR_show_history_form",
            menu_button=tech_kb.td_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "TD_TR_show_history_form")
)
async def show_history_form(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons: list[list[InlineKeyboardButton]] = []
    await show_form(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_or_waiting_button=tech_kb.td_history,
    )


@router.callback_query(F.data == tech_kb.td_pending.callback_data)
async def show_pending_menu(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    requests = get_all_pending_technical_requests_for_territorial_director(
        department_name=department_name
    )

    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Ожидающие заявки"),
        reply_markup=tech_kb.create_kb_with_end_point(
            end_point="TD_TR_show_pending_form",
            menu_button=tech_kb.td_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "TD_TR_show_pending_form")
)
async def show_pending_form(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await state.update_data(request_id=callback_data.request_id)
    buttons = [
        [
            InlineKeyboardButton(
                text="Утвердить статус",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="TD_TR_approve_state_menu",
                ).pack(),
            )
        ],
    ]

    await show_form(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_or_waiting_button=tech_kb.td_pending,
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "TD_TR_approve_state_menu")
)
async def approve_state_menu(
    message: Message | CallbackQuery,
    state: FSMContext,
    callback_data: ShowRequestCallbackData | None = None,
):
    if isinstance(message, CallbackQuery):
        await state.update_data(id=callback_data.request_id)
        message = message
    else:
        callback_data = ShowRequestCallbackData(
            request_id=(await state.get_data()).get("id"),
            end_point="TD_TR_approve_state_menu",
        )
    await try_edit_or_answer(
        message=message,
        text=hbold("Утверждение статуса"),
        reply_markup=tech_kb.td_approval_form_kb(
            state=state, callback_data=callback_data
        ),
    )


# State
@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "TD_TR_get_correct")
)
async def get_correct_answer(
    message: Message | CallbackQuery,
    state: FSMContext,
):
    if isinstance(message, CallbackQuery):
        message = message
    await state.set_state(TerritorialDirectorRequestForm.correct)
    await try_edit_or_answer(
        message=message,
        text=hbold("Статус корректен:"),
        reply_markup=kb.create_reply_keyboard(text.back, "Да", "Нет"),
    )


@router.message(TerritorialDirectorRequestForm.correct)
async def set_correct_answer(message: Message, state: FSMContext):
    await state.set_state(Base.none)
    await try_delete_message(message=message)

    if message.text == text.back:
        await approve_state_menu(message=message, state=state)
    elif message.text in ["Да", "Нет"]:
        await state.update_data(correct=True if "Да" else False)
        await approve_state_menu(message=message, state=state)
    else:
        msg = await try_edit_or_answer(
            message=message, text=text.format_err, return_message=True
        )
        await sleep(3)
        await try_delete_message(msg)
        await get_correct_answer(message=message, state=state)


# Description
@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "TD_TR_get_description")
)
async def get_description(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TerritorialDirectorRequestForm.description)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Введите комментарий:"),
        reply_markup=kb.create_reply_keyboard(text.back),
    )


@router.message(TerritorialDirectorRequestForm.description)
async def set_description(message: Message, state: FSMContext):
    await state.set_state(Base.none)
    await try_delete_message(message=message)

    if message.text == text.back:
        await approve_state_menu(message=message, state=state)
    else:
        await state.update_data(description=message.text)
        await approve_state_menu(message=message, state=state)


# Save approval form
@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "TD_TR_save_approval_form")
)
async def save_approval_form(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    data = await state.get_data()
    if "description" not in data:
        raise ValueError("Description wasn't found in state.")
    if "correct" not in data:
        raise ValueError("Correct option wasn't found in state.")
    description: str = data.get("description")
    correct_option: bool = data.get("correct")
    await state.clear()
    await state.set_state(Base.none)
    if not (
        await update_technical_request_by_territorial_director(
            id=callback_data.request_id,
            description=description,
            correct_option=correct_option,
        )
    ):
        raise ValueError(
            f"Technical request with id: {callback_data.request_id} wasn't update from department director"
        )
    msg = await try_edit_or_answer(
        message=callback.message, text="Успешно!", return_message=True
    )
    await sleep(3)
    await try_delete_message(msg)
    await show_tech_req_menu(msg)
