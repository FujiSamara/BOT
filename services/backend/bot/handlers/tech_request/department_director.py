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
    close_request,
    get_all_history_technical_requests_for_department_director,
    get_all_active_technical_requests_for_department_director,
    get_all_worker_in_group,
    get_departments_names,
    get_groups_names,
    get_technical_problem_by_name,
    get_technical_problem_names,
    update_tech_request_executor,
    update_technical_request_problem,
    get_count_req_in_departments,
)

from db.models import ApprovalStatus


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
    department_names = get_departments_names()

    count_reqs = get_count_req_in_departments(
        state=ApprovalStatus.pending_approval, tg_id=callback.message.chat.id
    )
    for key, department_name in enumerate(department_names):
        if department_name in count_reqs.keys():
            department_names[key] = f"{count_reqs[department_name]} {department_name}"
    department_names.sort()

    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите производство:"),
        reply_markup=kb.create_reply_keyboard(text.back, *department_names),
    )
    await state.update_data(msg=msg)


@router.message(DepartmentDirectorRequestForm.department)
async def set_department(message: Message, state: FSMContext):
    department_names = get_departments_names()

    count_reqs = get_count_req_in_departments(
        state=ApprovalStatus.pending_approval, tg_id=message.chat.id
    )
    for key, department_name in enumerate(department_names):
        if department_name in count_reqs.keys():
            department_names[key] = f"{count_reqs[department_name]} {department_name}"

    if await handle_department(
        message=message,
        state=state,
        departments_names=department_names,
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
    await state.update_data(request_id=callback_data.request_id)
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
        [
            InlineKeyboardButton(
                text="Закрыть заявку",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="DD_TR_close_request",
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
    ShowRequestCallbackData.filter(F.end_point == "get_DD_TR_executor_group")
)
async def get_group(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    groups_names = get_groups_names()

    await state.set_state(DepartmentDirectorRequestForm.group)
    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите отдел:"),
        reply_markup=kb.create_reply_keyboard(
            text.back,
            *groups_names,
        ),
    )
    await state.update_data(msg=msg)


@router.message(DepartmentDirectorRequestForm.group)
async def set_group(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await try_delete_message(msg)
    await try_delete_message(message)

    if message.text == text.back:
        await update_executor_format_ms(message=message, state=state)
    else:
        groups_names = get_groups_names()
        if message.text not in groups_names:
            groups_names.sort()
            msg = await message.answer(
                text=text.format_err,
                reply_markup=kb.create_reply_keyboard(
                    *[group_name for group_name in groups_names]
                ),
            )
            await state.update_data(msg=msg)

        await state.update_data(group_name=message.text)
        await get_executor(message=message, state=state)


async def get_executor(message: Message, state: FSMContext):
    await state.set_state(DepartmentDirectorRequestForm.executor)
    group_name = (await state.get_data()).get("group_name")
    workers = get_all_worker_in_group(group_name)
    await try_delete_message(message)
    msg = await message.answer(
        text=hbold(f"Выберите исполнителя в отделе '{group_name}':"),
        reply_markup=kb.create_reply_keyboard(
            text.back,
            *[
                " ".join([worker.l_name, worker.f_name, worker.o_name])
                for worker in workers
            ],
        ),
    )
    await state.update_data(msg=msg)


@router.message(DepartmentDirectorRequestForm.executor)
async def set_executor(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await try_delete_message(msg)
    await try_delete_message(message)

    if message.text == text.back:
        await update_executor_format_ms(message=message, state=state)
    else:
        LFO_workers = [
            " ".join([worker.l_name, worker.f_name, worker.o_name])
            for worker in get_all_worker_in_group(data.get("group_name"))
        ]
        if message.text not in LFO_workers:
            LFO_workers.sort()
            msg = await message.answer(
                text=text.format_err,
                reply_markup=kb.create_reply_keyboard(
                    *[LFO_worker for LFO_worker in LFO_workers]
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
    if repairman_TG_id:
        await notify_worker_by_telegram_id(
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


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "DD_TR_close_request")
)
async def close_request_change(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    yes_button = InlineKeyboardButton(
        text="Да",
        callback_data=ShowRequestCallbackData(
            request_id=callback_data.request_id,
            end_point="DD_TR_close_request_yes",
        ).pack(),
    )
    no_button = InlineKeyboardButton(
        text="Нет",
        callback_data=ShowRequestCallbackData(
            request_id=callback_data.request_id,
            end_point="DD_TR_show_form_active",
        ).pack(),
    )

    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Вы уверены, что хотите закрыть заявку?"),
        reply_markup=kb.create_inline_keyboard(yes_button, no_button),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "DD_TR_close_request_yes")
)
async def close_request_form_format_cb(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Закрыть заявку"),
        reply_markup=await tech_kb.dd_close_request_kb(
            state=state,
            callback_data=callback_data,
        ),
    )


async def close_request_form_format_ms(message: Message, state: FSMContext):
    data = await state.get_data()
    await try_edit_or_answer(
        message=message,
        text=hbold("Закрыть заявку"),
        reply_markup=await tech_kb.dd_close_request_kb(
            state=state,
            callback_data=ShowRequestCallbackData(
                request_id=data.get("request_id"),
                end_point="DD_TR_close_request_yes",
            ),
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "DD_TR_close_request_description")
)
async def get_description(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    await state.set_state(DepartmentDirectorRequestForm.description)
    await try_delete_message(callback.message)
    msg = await callback.message.answer(text=hbold("Укажите причину закрытия заявки:"))
    await state.update_data(msg=msg)


@router.message(DepartmentDirectorRequestForm.description)
async def set_description(message: Message, state: FSMContext):
    await state.set_state(Base.none)
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await try_delete_message(msg)
    await state.update_data(description=message.text)
    await try_delete_message(message)
    await close_request_form_format_ms(message, state)


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "DD_TR_save_close_request")
)
async def save_close_request(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    data = await state.get_data()
    creator_tg_id = close_request(
        request_id=data.get("request_id"),
        description=data.get("description"),
        telegram_id=callback.message.chat.id,
    )
    if creator_tg_id:
        await notify_worker_by_telegram_id(
            id=creator_tg_id,
            message=text.notification_worker,
        )
    await show_active_menu(
        callback=callback,
        state=state,
    )
