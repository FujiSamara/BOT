from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
)

from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from bot import text, kb
from bot.states import (
    Base,
    TerritorialManagerRequestForm,
)

from bot.handlers.tech_request.utils import show_form
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
    get_deparments_for_territorial_manager,
    update_technical_request_from_territorial_manager,
)

router = Router(name="technical_request_territorial_manager")


@router.callback_query(F.data == tech_kb.TM_button.callback_data)
async def show_tech_req_menu_cb(callback: CallbackQuery):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=tech_kb.TM_change_deparment_menu,
    )


async def show_tech_req_menu_ms(message: Message):
    await try_edit_or_answer(
        message=message,
        text=hbold("Тех. заявки"),
        reply_markup=tech_kb.TM_change_deparment_menu,
    )


@router.callback_query(F.data == tech_kb.TM_change_department_button.callback_data)
async def change_department(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TerritorialManagerRequestForm.department)
    departments = get_deparments_for_territorial_manager(callback.message.chat.id)

    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите производство:"),
        reply_markup=kb.create_reply_keyboard(
            "⏪ Назад", *[department.name for department in departments]
        ),
    )
    await state.update_data(msg=msg)


@router.message(TerritorialManagerRequestForm.department)
async def set_department(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await try_delete_message(msg)
    await try_delete_message(message)

    if message.text == "⏪ Назад":
        await show_tech_req_menu_ms(message)
    else:
        deparment_names = [
            department.name
            for department in get_deparments_for_territorial_manager(message.chat.id)
        ]
        if message.text not in deparment_names:
            deparment_names.sort()
            msg = await message.answer(
                text=text.format_err,
                reply_markup=kb.create_reply_keyboard(
                    *[department for department in deparment_names]
                ),
            )
            await state.update_data(msg=msg)
            return
        await state.update_data(department_name=message.text)
        await message.answer(
            text=hbold(f"Производство: {message.text}"),
            reply_markup=tech_kb.TM_menu_markup,
        )


@router.callback_query(F.data == tech_kb.TM_menu_button.callback_data)
async def show_menu(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f"Производство: {department_name}"),
        reply_markup=tech_kb.TM_menu_markup,
    )


@router.callback_query(F.data == tech_kb.TM_history.callback_data)
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
            end_point="territorial_manager_show_form_history",
            menu_button=tech_kb.TM_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(
        F.end_point == "territorial_manager_show_form_history"
    )
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
        history_or_waiting_button=tech_kb.TM_history,
    )


@router.callback_query(F.data == tech_kb.TM_waiting.callback_data)
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
            end_point="territorial_manager_show_form_waiting",
            menu_button=tech_kb.TM_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(
        F.end_point == "territorial_manager_show_form_waiting"
    )
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
                    end_point="tech_req_territorial_manager_rate_form",
                ).pack(),
            )
        ]
    ]
    await show_form(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_or_waiting_button=tech_kb.TM_waiting,
    )


@router.callback_query(
    ShowRequestCallbackData.filter(
        F.end_point == "tech_req_territorial_manager_rate_form"
    )
)
async def show_rate_form_cb(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Оценить заявку"),
        reply_markup=await tech_kb.TM_rate_kb(state=state, callback_data=callback_data),
    )


async def show_rate_form_ms(message: Message, state: FSMContext):
    data = await state.get_data()
    await try_edit_or_answer(
        message=message,
        text=hbold("Оценить заявку"),
        reply_markup=await tech_kb.TM_rate_kb(
            state=state,
            callback_data=ShowRequestCallbackData(
                request_id=data.get("request_id"),
                end_point="tech_req_territorial_manager_rate_form",
            ),
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(
        F.end_point == "territorial_manager_rate_tech_request"
    )
)
async def show_rate_tech_request(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await state.set_state(TerritorialManagerRequestForm.mark)
    await state.update_data(request_id=callback_data.request_id)
    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Оценка:"),
        reply_markup=kb.create_reply_keyboard(
            "⏪ Назад", *[str(mark) for mark in range(1, 6)]
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

    if message.text == "⏪ Назад":
        await show_tech_req_menu_ms(message)
    else:
        if int(message.text) not in range(1, 6):
            msg = await message.answer(
                text=text.format_err,
                reply_markup=kb.create_reply_keyboard(*[mark for mark in range(1, 6)]),
            )
            await state.update_data(msg=msg)
            return
        await state.update_data(mark=int(message.text))
        await show_rate_form_ms(message=message, state=state)


@router.callback_query(
    ShowRequestCallbackData.filter(
        F.end_point == "save_tech_req_territorial_manager_rate"
    )
)
async def save_rate(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    mark = (await state.get_data()).get("mark")
    request_id = callback_data.request_id
    ret_data = update_technical_request_from_territorial_manager(
        mark=mark, request_id=request_id
    )

    if ret_data:
        await notify_worker_by_telegram_id(
            id=ret_data["repairman_telegram_id"],
            message=text.notification_repairman_reopen
            + f"\nНа производстве: {ret_data["department_name"]}",
        )

    await state.clear()
    await state.set_state(Base.none)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=tech_kb.TM_button,  # ?
    )
