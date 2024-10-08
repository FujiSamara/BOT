from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
)

from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from db.models import ApprovalStatus
from bot import text, kb
from bot.states import (
    Base,
    TerritorialManagerRequestForm,
)

from bot.handlers.tech_request.utils import handle_department, show_form
from bot.handlers.tech_request.schemas import ShowRequestCallbackData
from bot.handlers.tech_request import kb as tech_kb
from bot.handlers.utils import (
    notify_worker_by_telegram_id,
    try_delete_message,
    try_edit_or_answer,
)


from db.service import (
    get_all_history_technical_requests_for_territorial_manager,
    get_all_waiting_technical_requests_for_territorial_manager,
    get_departments_names_for_territorial_manager,
    update_technical_request_from_territorial_manager,
)

router = Router(name="technical_request_territorial_manager")


@router.callback_query(F.data == tech_kb.tm_button.callback_data)
async def show_tech_req_menu_cb(callback: CallbackQuery):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=tech_kb.tm_change_department_menu,
    )


async def show_tech_req_menu_ms(message: Message):
    await try_edit_or_answer(
        message=message,
        text=hbold("Тех. заявки"),
        reply_markup=tech_kb.tm_change_department_menu,
    )


@router.callback_query(F.data == tech_kb.tm_change_department_button.callback_data)
async def change_department(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TerritorialManagerRequestForm.department)
    department_names = get_departments_names_for_territorial_manager(
        callback.message.chat.id
    )
    department_names.sort()

    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите производство:"),
        reply_markup=kb.create_reply_keyboard(text.back, *department_names),
    )
    await state.update_data(msg=msg)


@router.message(TerritorialManagerRequestForm.department)
async def set_department(message: Message, state: FSMContext):
    if await handle_department(
        message=message,
        state=state,
        departments_names=get_departments_names_for_territorial_manager(
            message.chat.id
        ),
        reply_markup=tech_kb.tm_menu_markup,
    ):
        await show_tech_req_menu_ms(message)


@router.callback_query(F.data == tech_kb.tm_menu_button.callback_data)
async def show_menu(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f"Производство: {department_name}"),
        reply_markup=tech_kb.tm_menu_markup,
    )


@router.callback_query(F.data == tech_kb.tm_history.callback_data)
async def show_history_menu(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    requests = get_all_history_technical_requests_for_territorial_manager(
        telegram_id=callback.message.chat.id, department_name=department_name
    )

    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("История заявок"),
        reply_markup=tech_kb.create_kb_with_end_point(
            end_point="TM_TR_show_form_history",
            menu_button=tech_kb.tm_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "TM_TR_show_form_history")
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
        history_or_waiting_button=tech_kb.tm_history,
    )


@router.callback_query(F.data == tech_kb.tm_waiting.callback_data)
async def show_waiting_menu(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    requests = get_all_waiting_technical_requests_for_territorial_manager(
        telegram_id=callback.message.chat.id, department_name=department_name
    )
    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Ожидающие заявки"),
        reply_markup=tech_kb.create_kb_with_end_point(
            end_point="TM_TR_show_form_waiting",
            menu_button=tech_kb.tm_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "TM_TR_show_form_waiting")
)
async def show_waiting_form(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="Оценить заявку",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="TM_TR_rate_form",
                ).pack(),
            )
        ]
    ]
    await show_form(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_or_waiting_button=tech_kb.tm_waiting,
    )


@router.callback_query(ShowRequestCallbackData.filter(F.end_point == "TM_TR_rate_form"))
async def show_rate_form_cb(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Оценить заявку"),
        reply_markup=await tech_kb.tm_rate_kb(state=state, callback_data=callback_data),
    )


async def show_rate_form_ms(message: Message, state: FSMContext):
    data = await state.get_data()
    await try_edit_or_answer(
        message=message,
        text=hbold("Оценить заявку"),
        reply_markup=await tech_kb.tm_rate_kb(
            state=state,
            callback_data=ShowRequestCallbackData(
                request_id=data.get("request_id"),
                end_point="TM_TR_rate_form",
            ),
        ),
    )


@router.callback_query(ShowRequestCallbackData.filter(F.end_point == "TM_TR_rate"))
async def show_rate_tech_request(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await state.set_state(TerritorialManagerRequestForm.mark)
    await state.update_data(request_id=callback_data.request_id)
    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Оценка:"),
        reply_markup=kb.create_reply_keyboard(
            text.back, *[str(mark) for mark in range(1, 6)]
        ),
    )
    await state.update_data(msg=msg)


@router.message(TerritorialManagerRequestForm.mark)
async def set_mark(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await try_delete_message(msg)
    await try_delete_message(message)

    if message.text == text.back:
        await state.set_state(Base.none)
        await show_rate_form_ms(message=message, state=state)
    else:
        if int(message.text) not in range(1, 6):
            msg = await message.answer(
                text=text.format_err,
                reply_markup=kb.create_reply_keyboard(
                    *[str(mark) for mark in range(1, 6)]
                ),
            )
            await state.update_data(msg=msg)
            return
        await state.update_data(mark=int(message.text))
        await show_rate_form_ms(message=message, state=state)
        await state.set_state(Base.none)


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "description_TM_TR")
)
async def get_description(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await state.set_state(TerritorialManagerRequestForm.description)
    await try_delete_message(callback.message)
    msg = await callback.message.answer(text=hbold("Введите комментарий:"))
    await state.update_data(msg=msg)


@router.message(TerritorialManagerRequestForm.description)
async def set_description(message: Message, state: FSMContext):
    await state.set_state(Base.none)
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await try_delete_message(msg)
    await state.update_data(description=message.text)
    await try_delete_message(message)
    await show_rate_form_ms(message, state)


@router.callback_query(ShowRequestCallbackData.filter(F.end_point == "save_TM_TR_rate"))
async def save_rate(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    data = await state.get_data()
    mark = data.get("mark")
    description = data.get("description")
    request_id = callback_data.request_id

    request_data = update_technical_request_from_territorial_manager(
        mark=mark, request_id=request_id, description=description
    )

    if mark == 1 and request_data["state"] not in [
        ApprovalStatus.approved,
        ApprovalStatus.skipped,
    ]:
        await notify_worker_by_telegram_id(
            id=request_data["repairman_telegram_id"],
            message=text.notification_repairman_reopen
            + f"\nНа производстве: {request_data['department_name']}",
        )

    await notify_worker_by_telegram_id(
        id=request_data["worker_telegram_id"], message=text.notification_worker
    )

    await state.clear()
    await state.set_state(Base.none)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=tech_kb.tm_change_department_menu,
    )
