import logging
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
)

from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from bot import text
from bot.states import (
    Base,
    TerritorialManagerRequestForm,
)
from bot.kb import (
    create_reply_keyboard,
    territorial_manager_rate_tech_req_kb,
    territorial_manager_req_change_deparment_menu,
    territorial_manager_tech_req_change_department_button,
    territorial_manager_tech_req_button,
    territorial_manager_tech_req_menu_markup,
    territorial_manager_tech_req_menu_button,
    territorial_manager_tech_req_waiting,
    territorial_manager_tech_req_history,
)
from bot.handlers.utils import (
    notify_worker_by_telegram_id,
    try_delete_message,
    try_edit_or_answer,
)
from bot.handlers.tech_req.utils import (
    create_keybord_for_requests_with_end_point,
    # send_photos,
    show_form,
)
from bot.handlers.tech_req.schemas import ShowRequestCallbackData

from db.service import (
    get_all_history_technical_requests_by_territorial_manager_TG_id_and_department_name,
    get_all_waiting_technical_requests_by_territorial_manager_TG_id_and_department_name,
    get_deparments_by_territorial_manager_telegram_id,
    update_technical_request_from_territorial_manager,
    # get_technical_problem_names,
    # get_technical_request_by_id,
    # update_technical_request_territorial_manager,
)

router = Router(name="technical_request_territorial_manager")


@router.callback_query(F.data == territorial_manager_tech_req_button.callback_data)
async def territorial_manager_menu_cb(callback: CallbackQuery):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=territorial_manager_req_change_deparment_menu,
    )


async def territorial_manager_menu_ms(message: Message):
    await try_edit_or_answer(
        message=message,
        text=hbold("Тех. заявки"),
        reply_markup=territorial_manager_req_change_deparment_menu,
    )


@router.callback_query(
    F.data == territorial_manager_tech_req_change_department_button.callback_data
)
async def department_change(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TerritorialManagerRequestForm.department)
    departments = get_deparments_by_territorial_manager_telegram_id(
        callback.message.chat.id
    )

    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите производство:"),
        reply_markup=create_reply_keyboard(
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
        await territorial_manager_menu_ms(message)
    else:
        deparment_names = [
            department.name
            for department in get_deparments_by_territorial_manager_telegram_id(
                message.chat.id
            )
        ]
        if message.text not in deparment_names:
            deparment_names.sort()
            msg = await message.answer(
                text=text.format_err,
                reply_markup=create_reply_keyboard(
                    *[department for department in deparment_names]
                ),
            )
            await state.update_data(msg=msg)
            return
        await state.update_data(department_name=message.text)
        await message.answer(
            text=hbold(f"Производство: {message.text}"),
            reply_markup=territorial_manager_tech_req_menu_markup,
        )


@router.callback_query(F.data == territorial_manager_tech_req_menu_button.callback_data)
async def territorial_manager_tech_req_menu(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f"Производство: {department_name}"),
        reply_markup=territorial_manager_tech_req_menu_markup,
    )


@router.callback_query(F.data == territorial_manager_tech_req_history.callback_data)
async def territorial_manager_history(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    requests = get_all_history_technical_requests_by_territorial_manager_TG_id_and_department_name(
        telegram_id=callback.message.chat.id, department_name=department_name
    )

    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("История заявок"),
        reply_markup=create_keybord_for_requests_with_end_point(
            end_point="territorial_manager_show_form_history",
            menu_button=territorial_manager_tech_req_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(
        F.end_point == "territorial_manager_show_form_history"
    )
)
async def territorial_manager_show_form_history(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons: list[list[InlineKeyboardButton]] = []
    await show_form(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_button=territorial_manager_tech_req_history,
    )


@router.callback_query(F.data == territorial_manager_tech_req_waiting.callback_data)
async def territorial_manager_waiting(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    requests = get_all_waiting_technical_requests_by_territorial_manager_TG_id_and_department_name(
        telegram_id=callback.message.chat.id, department_name=department_name
    )
    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Ожидающие заявки"),
        reply_markup=create_keybord_for_requests_with_end_point(
            end_point="territorial_manager_show_form_waiting",
            menu_button=territorial_manager_tech_req_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(
        F.end_point == "territorial_manager_show_form_waiting"
    )
)
async def territorial_manager_show_form_waiting(
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
        history_button=territorial_manager_tech_req_waiting,
    )


@router.callback_query(
    ShowRequestCallbackData.filter(
        F.end_point == "tech_req_territorial_manager_rate_form"
    )
)
async def tech_req_territorial_manager_rate_form_cb(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Оценить заявку"),
        reply_markup=await territorial_manager_rate_tech_req_kb(
            state=state, callback_data=callback_data
        ),
    )


async def tech_req_territorial_manager_rate_form_ms(
    message: Message, state: FSMContext
):
    data = await state.get_data()
    await try_edit_or_answer(
        message=message,
        text=hbold("Оценить заявку"),
        reply_markup=await territorial_manager_rate_tech_req_kb(
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
async def territorial_manager_rate_tech_request(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await state.set_state(TerritorialManagerRequestForm.mark)
    await state.update_data(request_id=callback_data.request_id)
    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Оценка:"),
        reply_markup=create_reply_keyboard(
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
        await territorial_manager_menu_ms(message)
    else:
        if int(message.text) not in range(1, 6):
            msg = await message.answer(
                text=text.format_err,
                reply_markup=create_reply_keyboard(*[mark for mark in range(1, 6)]),
            )
            await state.update_data(msg=msg)
            return
        await state.update_data(mark=int(message.text))
        await tech_req_territorial_manager_rate_form_ms(message=message, state=state)


@router.callback_query(
    ShowRequestCallbackData.filter(
        F.end_point == "save_tech_req_territorial_manager_rate"
    )
)
async def save_tech_req_territorial_manager_rate(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    mark = (await state.get_data()).get("mark")
    request_id = callback_data.request_id
    repairman_TG_id = update_technical_request_from_territorial_manager(
        mark=mark, request_id=request_id
    )

    if repairman_TG_id:
        await notify_worker_by_telegram_id(
            id=repairman_TG_id, message=text.notifay_repairman_reopen
        )

    await state.clear()
    await state.set_state(Base.none)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=territorial_manager_req_change_deparment_menu,
    )
