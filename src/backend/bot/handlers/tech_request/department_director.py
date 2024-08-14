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
    DepartmentDirectorRequestForm,
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
    get_all_history_technical_requests_for_department_director,
    get_all_active_technical_requests_for_department_director,
    get_all_departments,
    get_all_repairmans_in_department,
    get_technical_problem_by_name,
    get_technical_problem_names,
    get_technical_request_by_id,
    update_tech_request_executor,
    update_technical_request_problem,
)

router = Router(name="technical_request_department_director")


@router.callback_query(F.data == tech_kb.dd_button.callback_data)
async def show_tech_req_menu_cb(callback: CallbackQuery):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=tech_kb.dd_change_department_menu,
    )


async def show_tech_req_menu_ms(message: Message):
    await try_edit_or_answer(
        message=message,
        text=hbold("Тех. заявки"),
        reply_markup=tech_kb.dd_change_department_menu,
    )


@router.callback_query(F.data == tech_kb.dd_change_department_button.callback_data)
async def change_department(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DepartmentDirectorRequestForm.department)
    departments = get_all_departments(callback.message.chat.id)
    department_names = [department.name for department in departments]
    department_names.sort()

    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите производство:"),
        reply_markup=kb.create_reply_keyboard(
            text.back, *[department_name for department_name in department_names]
        ),
    )
    await state.update_data(msg=msg)


@router.message(DepartmentDirectorRequestForm.department)
async def set_department(message: Message, state: FSMContext):
    if await handle_department(
        message=message,
        state=state,
        departments=get_all_departments(message.chat.id),
        reply_markup=tech_kb.dd_menu_markup,
    ):
        await show_tech_req_menu_ms(message)


@router.callback_query(F.data == tech_kb.dd_menu_button.callback_data)
async def show_menu(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f"Производство: {department_name}"),
        reply_markup=tech_kb.dd_menu_markup,
    )


@router.callback_query(F.data == tech_kb.dd_history.callback_data)
async def show_history_menu(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    requests = get_all_history_technical_requests_for_department_director(
        department_name=department_name
    )

    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("История заявок"),
        reply_markup=tech_kb.create_kb_with_end_point(
            end_point="DD_TR_show_form_history",
            menu_button=tech_kb.dd_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "DD_TR_show_form_history")
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
        history_or_waiting_button=tech_kb.dd_history,
    )


@router.callback_query(F.data == tech_kb.dd_active.callback_data)
async def show_active_menu(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    requests = get_all_active_technical_requests_for_department_director(
        telegram_id=callback.message.chat.id, department_name=department_name
    )

    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Активные заявки"),
        reply_markup=tech_kb.create_kb_with_end_point(
            end_point="DD_TR_show_form_active",
            menu_button=tech_kb.dd_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "DD_TR_show_form_active")
)
async def show_active_request_form(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons = [
        [
            InlineKeyboardButton(
                text="Изменить исполнителя",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="DD_TR_update_request_executor",
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="Изменить проблему",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="DD_TR_update_request_problem",
                ).pack(),
            )
        ],
    ]

    await show_form(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_or_waiting_button=tech_kb.dd_active,
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "DD_TR_update_request_executor")
)
async def update_executor_format_cb(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Изменить исполнителя"),
        reply_markup=await tech_kb.dd_update_kb_executor(
            state=state, callback_data=callback_data
        ),
    )


async def update_executor_format_ms(message: Message, state: FSMContext):
    data = await state.get_data()
    await try_edit_or_answer(
        message=message,
        text=hbold("Изменить исполнителя"),
        reply_markup=await tech_kb.dd_update_kb_executor(
            state=state,
            callback_data=ShowRequestCallbackData(
                request_id=data.get("request_id"),
                end_point="DD_TR_update_request_executor",
            ),
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "get_DD_TR_executor")
)
async def get_executor(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    await state.set_state(DepartmentDirectorRequestForm.executor)
    department_name = (await state.get_data()).get("department_name")
    repairmans = get_all_repairmans_in_department(department_name)
    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите исполнителя:"),
        reply_markup=kb.create_reply_keyboard(
            text.back,
            *[
                " ".join([repairman.l_name, repairman.f_name, repairman.o_name])
                for repairman in repairmans
            ],
        ),
    )
    await state.update_data(msg=msg)
    await state.update_data(request_id=callback_data.request_id)


@router.message(DepartmentDirectorRequestForm.executor)
async def set_executor(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await try_delete_message(msg)
    await try_delete_message(message)

    if message.text == text.back:
        await update_executor_format_ms(message)
    else:
        LFO_repairmans = [
            " ".join([repairman.l_name, repairman.f_name, repairman.o_name])
            for repairman in get_all_repairmans_in_department(
                data.get("department_name")
            )
        ]
        if message.text not in LFO_repairmans:
            LFO_repairmans.sort()
            msg = await message.answer(
                text=text.format_err,
                reply_markup=kb.create_reply_keyboard(
                    *[LFO_repairman for LFO_repairman in LFO_repairmans]
                ),
            )
            await state.update_data(msg=msg)

        await state.update_data(repairman_full_name=message.text)
        await update_executor_format_ms(message=message, state=state)


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "DD_TR_save_change_executor")
)
async def save_change_executor(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    data = await state.get_data()
    request_id = callback_data.request_id
    repairman_full_name = data.get("repairman_full_name").split(" ")
    repairman_TG_id = update_tech_request_executor(
        request_id=request_id, repairman_full_name=repairman_full_name
    )
    notify_worker_by_telegram_id(
        id=repairman_TG_id, message=text.notification_repairman
    )
    await show_active_request_form(
        callback=callback, callback_data=callback_data, state=state
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "DD_TR_update_request_problem")
)
async def update_problem_format_cb(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Изменить заявку"),
        reply_markup=await tech_kb.dd_update_problem_kb(
            state=state, callback_data=callback_data
        ),
    )


async def update_problem_format_ms(message: Message, state: FSMContext):
    data = await state.get_data()
    await try_edit_or_answer(
        message=message,
        text=hbold("Изменить заявку"),
        reply_markup=await tech_kb.dd_update_problem_kb(
            state=state,
            callback_data=ShowRequestCallbackData(
                request_id=data.get("request_id"),
                end_point="DD_TR_update_request_problem",
            ),
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "get_DD_TR_problem")
)
async def get_problem(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await state.set_state(DepartmentDirectorRequestForm.problem)
    problems = get_technical_problem_names()
    problems.sort()
    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите проблему:"),
        reply_markup=kb.create_reply_keyboard(
            text.back, *[problem for problem in problems]
        ),
    )
    await state.update_data(request_id=callback_data.request_id)
    await state.update_data(msg=msg)


@router.message(DepartmentDirectorRequestForm.problem)
async def set_problem(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await try_delete_message(msg)
    await try_delete_message(message)

    if message.text == text.back:
        await state.set_state(Base.none)
        await update_problem_format_ms(message, state)
    else:
        problems = get_technical_problem_names()
        if message.text not in problems:
            problems.sort()
            msg = await message.answer(
                text=text.format_err,
                reply_markup=kb.create_reply_keyboard(
                    *[problem for problem in problems]
                ),
            )
            await state.update_data(msg=msg)
            return

        await state.update_data(
            problem_id=get_technical_problem_by_name(message.text).id
        )
        await update_problem_format_ms(message, state)
        await state.set_state(Base.none)


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "DD_TR_save_change_problem")
)
async def save_change_problem(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    data = await state.get_data()
    request_id = callback_data.request_id
    problem_id = data.get("problem_id")
    update_technical_request_problem(request_id=request_id, problem_id=problem_id)
    await show_active_request_form(
        callback=callback, callback_data=callback_data, state=state
    )
