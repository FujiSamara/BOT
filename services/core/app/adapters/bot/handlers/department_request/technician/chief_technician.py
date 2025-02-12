from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
from fastapi import UploadFile

from app.adapters.bot import text, kb
from app.adapters.bot.states import Base, ChiefTechnicianTechnicalRequestForm

from app.adapters.bot.handlers.department_request.schemas import ShowRequestCallbackData
from app.adapters.bot.handlers.department_request import kb as tech_kb
from app.adapters.bot.handlers.utils import (
    download_file,
    handle_documents,
    handle_documents_form,
    try_delete_message,
    try_edit_or_answer,
)
from app.adapters.bot.handlers.department_request.utils import (
    handle_department,
    show_form_technician,
    department_names_with_count,
)

from app.services import (
    set_not_relevant_state,
    get_all_history_technical_requests_for_repairman,
    get_all_worker_in_group,
    get_all_rework_technical_requests_for_repairman,
    get_all_waiting_technical_requests_for_repairman,
    get_all_active_requests_in_department_for_chief_technician,
    get_departments_names_for_chief_technician,
    get_groups_names,
    get_technical_request_by_id,
    update_tech_request_executor,
    update_technical_request_from_repairman,
)
from app.infra.database.models import ApprovalStatus

router = Router(name="technical_request_chief_technician")


@router.callback_query(F.data == tech_kb.ct_button.callback_data)
async def show_tech_req_format(message: Message | CallbackQuery):
    if isinstance(message, CallbackQuery):
        message = message.message

    await try_edit_or_answer(
        message=message,
        text=hbold(tech_kb.ct_button.text),
        reply_markup=tech_kb.ct_rm,
    )


@router.callback_query(F.data == tech_kb.ct_change_department_button.callback_data)
async def get_department(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ChiefTechnicianTechnicalRequestForm.department)
    department_names = department_names_with_count(
        state=ApprovalStatus.pending,
        department_names=get_departments_names_for_chief_technician(
            callback.message.chat.id
        ),
    )
    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите предприятие:"),
        reply_markup=kb.create_reply_keyboard(text.back, *department_names),
    )
    await state.update_data(msg=msg)


@router.message(ChiefTechnicianTechnicalRequestForm.department)
async def set_department(message: Message, state: FSMContext):
    if await handle_department(
        message=message,
        state=state,
        departments_names=department_names_with_count(
            state=ApprovalStatus.pending,
            department_names=get_departments_names_for_chief_technician(
                message.chat.id
            ),
        ),
        reply_markup=tech_kb.ct_menu_markup,
    ):
        await show_tech_req_format(message)


# region Own requests
@router.callback_query(
    F.data == tech_kb.ct_own_button.callback_data,
)
async def show_own_requests(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f"Предприятие: {department_name}"),
        reply_markup=tech_kb.ct_own_menu_markup,
    )


@router.callback_query(F.data == tech_kb.ct_own_waiting.callback_data)
async def show_own_waiting(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    requests = get_all_waiting_technical_requests_for_repairman(
        telegram_id=callback.message.chat.id, department_name=department_name
    )
    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(tech_kb.ct_own_waiting.text + f"\nПредприятие: {department_name}"),
        reply_markup=tech_kb.create_kb_with_end_point_TR(
            end_point="CT_TR_show_form_waiting",
            menu_button=tech_kb.ct_own_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "CT_TR_show_form_waiting")
)
async def show_own_waiting_form_format_cb(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="Выполнить заявку",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="CT_TR_repair_waiting_form",
                ).pack(),
            )
        ]
    ]

    await show_form_technician(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_or_waiting_button=tech_kb.ct_own_waiting,
    )


async def show_own_waiting_form_format_ms(message: Message, state: FSMContext):
    data = await state.get_data()
    await try_edit_or_answer(
        message=message,
        text=hbold("Выполнить заявку"),
        reply_markup=await tech_kb.ct_repair_waiting_kb(
            state=state,
            callback_data=ShowRequestCallbackData(
                request_id=data.get("request_id"),
                end_point="CT_TR_repair_waiting_form",
            ),
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "CT_TR_repair_waiting_form")
)
async def show_waiting_repair_form_cb(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Выполнить заявку"),
        reply_markup=await tech_kb.ct_repair_waiting_kb(
            state=state, callback_data=callback_data
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "get_CT_TR_photo_waiting")
)
async def get_waiting_repairman_photo(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await state.update_data(request_id=callback_data.request_id)
    await handle_documents_form(
        callback.message, state, ChiefTechnicianTechnicalRequestForm.photo_waiting
    )


@router.message(ChiefTechnicianTechnicalRequestForm.photo_waiting)
async def set_waiting_repairman_photo(message: Message, state: FSMContext):
    await handle_documents(
        message,
        state,
        "photo",
        show_own_waiting_form_format_ms,
    )


@router.callback_query(F.data == tech_kb.ct_rework.callback_data)
async def show_rework_menu(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    requests = get_all_rework_technical_requests_for_repairman(
        telegram_id=callback.message.chat.id, department_name=department_name
    )
    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f"Заявки на доработку\nПредприятие: {department_name}"),
        reply_markup=tech_kb.create_kb_with_end_point(
            end_point="CT_TR_show_form_rework",
            menu_button=tech_kb.ct_own_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "CT_TR_show_form_rework")
)
async def show_rework_form_format_cb(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="Выполнить заявку",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="CT_TR_repair_rework_form",
                ).pack(),
            )
        ]
    ]
    await show_form_technician(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_or_waiting_button=tech_kb.ct_rework,
    )


async def show_rework_form_format_ms(message: Message, state: FSMContext):
    data = await state.get_data()
    await try_edit_or_answer(
        message=message,
        text=hbold("Выполнить заявку"),
        reply_markup=await tech_kb.ct_repair_rework_kb(
            state=state,
            callback_data=ShowRequestCallbackData(
                request_id=data.get("request_id"),
                end_point="CT_TR_repair_rework_form",
            ),
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "CT_TR_repair_rework_form")
)
async def show_rework_repair_form_cb(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Выполнить заявку"),
        reply_markup=await tech_kb.ct_repair_rework_kb(
            state=state, callback_data=callback_data
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "get_CT_TR_photo_rework")
)
async def get_rework_repairman_photo(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await state.update_data(request_id=callback_data.request_id)
    await handle_documents_form(
        callback.message, state, ChiefTechnicianTechnicalRequestForm.photo_rework
    )


@router.message(ChiefTechnicianTechnicalRequestForm.photo_rework)
async def set_rework_repairman_photo(message: Message, state: FSMContext):
    await handle_documents(
        message,
        state,
        "photo",
        show_rework_form_format_ms,
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "save_CT_TR_repair")
)
async def save_repair(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    data = await state.get_data()

    photo = data["photo"]
    photo_files: list[UploadFile] = []
    for doc in photo:
        photo_files.append(await download_file(doc))

    if not (
        await update_technical_request_from_repairman(
            photo_files=photo_files, request_id=callback_data.request_id
        )
    ):
        raise ValueError(
            f"Technical request with id: {callback_data.request_id} wasn't update by executor"
        )
    await state.set_state(Base.none)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(tech_kb.ct_button.text),
        reply_markup=tech_kb.ct_rm,
    )


@router.callback_query(F.data == tech_kb.ct_own_history.callback_data)
async def show_own_history(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    requests = get_all_history_technical_requests_for_repairman(
        telegram_id=callback.message.chat.id, department_name=department_name
    )
    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(tech_kb.ct_own_history.text + f"\nПредприятие: {department_name}"),
        reply_markup=tech_kb.create_kb_with_end_point_TR(
            end_point="show_CT_TR_own_history_form",
            menu_button=tech_kb.ct_own_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "show_CT_TR_own_history_form")
)
async def show_own_history_form(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons: list[list[InlineKeyboardButton]] = []
    await show_form_technician(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_or_waiting_button=tech_kb.ct_own_history,
    )


# endregion

# region Admin requests


@router.callback_query(F.data == tech_kb.ct_admin_button.callback_data)
async def show_admin_menu(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    requests = get_all_active_requests_in_department_for_chief_technician(
        department_name
    )
    await try_edit_or_answer(
        callback.message,
        text=hbold(tech_kb.ct_admin_button.text + f"\nПредприятие: {department_name}"),
        reply_markup=tech_kb.create_kb_with_end_point_and_symbols(
            end_point="show_CT_TR_admin_form",
            menu_button=tech_kb.ct_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "show_CT_TR_admin_form")
)
async def show_admin_form(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    await state.update_data(request_id=callback_data.request_id)
    repairman = get_technical_request_by_id(callback_data.request_id).repairman
    repairman_full_name_old = " ".join(
        [repairman.l_name, repairman.f_name, repairman.o_name]
    )
    await state.update_data(repairman_full_name=repairman_full_name_old)
    buttons: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="Сменить исполнителя",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="show_CT_TR_change_executor",
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="Закрыть заявку",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="CT_TR_close_request",
                ).pack(),
            )
        ],
    ]

    await show_form_technician(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_or_waiting_button=tech_kb.ct_admin_button,
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "show_CT_TR_change_executor")
)
async def show_change_executor_format_cb(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    await state.update_data(request_id=callback_data.request_id)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Сменить исполнителя"),
        reply_markup=await tech_kb.ct_admin_kb(
            state=state, callback_data=callback_data
        ),
    )


async def show_change_executor_format_ms(message: Message, state: FSMContext):
    data = await state.get_data()
    await try_edit_or_answer(
        message=message,
        text=hbold("Сменить исполнителя"),
        reply_markup=await tech_kb.ct_admin_kb(
            state=state,
            callback_data=ShowRequestCallbackData(
                request_id=data.get("request_id"),
                end_point="show_CT_TR_change_executor",
            ),
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "get_CT_TR_executor_group")
)
async def get_group(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    groups_names = get_groups_names()

    await state.set_state(ChiefTechnicianTechnicalRequestForm.group)
    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите отдел:"),
        reply_markup=kb.create_reply_keyboard(
            text.back,
            *groups_names,
        ),
    )
    await state.update_data(msg=msg)


@router.message(ChiefTechnicianTechnicalRequestForm.group)
async def set_group(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await try_delete_message(msg)
    await try_delete_message(message)

    if message.text == text.back:
        await show_change_executor_format_ms(message=message, state=state)
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
    await state.set_state(ChiefTechnicianTechnicalRequestForm.executor)
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


@router.message(ChiefTechnicianTechnicalRequestForm.executor)
async def set_executor(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await try_delete_message(msg)
    await try_delete_message(message)

    if message.text == text.back:
        await show_tech_req_format(message)
    else:
        LFO_workers = [
            " ".join([repairman.l_name, repairman.f_name, repairman.o_name])
            for repairman in get_all_worker_in_group(data.get("group_name"))
        ]
        if message.text not in LFO_workers:
            LFO_workers.sort()
            msg = await message.answer(
                text=text.format_err,
                reply_markup=kb.create_reply_keyboard(
                    *[LFO_repairman for LFO_repairman in LFO_workers]
                ),
            )
            await state.update_data(msg=msg)

        await state.update_data(repairman_full_name=message.text)
        await show_change_executor_format_ms(message=message, state=state)


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "save_CT_TR_admin_form")
)
async def save_CT_TR_admin_form(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    request_id = callback_data.request_id
    repairman_full_name = (await state.get_data()).get("repairman_full_name").split(" ")
    data = await state.get_data()
    await state.clear()
    if not (
        await update_tech_request_executor(
            request_id=request_id,
            repairman_full_name=repairman_full_name,
            department_name=data.get("department_name"),
        )
    ):
        raise ValueError(f"Executor of technical request {request_id} wasn't update")

    await state.set_state(Base.none)
    await show_tech_req_format(callback=callback)


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "CT_TR_close_request")
)
async def close_request_change(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    yes_button = InlineKeyboardButton(
        text="Да",
        callback_data=ShowRequestCallbackData(
            request_id=callback_data.request_id,
            end_point="CT_TR_close_request_yes",
        ).pack(),
    )
    no_button = InlineKeyboardButton(
        text="Нет",
        callback_data=ShowRequestCallbackData(
            request_id=callback_data.request_id,
            end_point="show_CT_TR_admin_form",
        ).pack(),
    )

    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Вы уверены, что хотите закрыть заявку?"),
        reply_markup=kb.create_inline_keyboard(yes_button, no_button),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "CT_TR_close_request_yes")
)
async def close_request_form_format_cb(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Закрыть заявку"),
        reply_markup=await tech_kb.ct_close_request_kb(
            state=state,
            callback_data=callback_data,
        ),
    )


async def close_request_form_format_ms(message: Message, state: FSMContext):
    data = await state.get_data()
    await try_edit_or_answer(
        message=message,
        text=hbold("Закрыть заявку"),
        reply_markup=await tech_kb.ct_close_request_kb(
            state=state,
            callback_data=ShowRequestCallbackData(
                request_id=data.get("request_id"),
                end_point="CT_TR_close_request_yes",
            ),
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "CT_TR_close_request_description")
)
async def get_description(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    await state.set_state(ChiefTechnicianTechnicalRequestForm.description)
    await try_delete_message(callback.message)
    msg = await callback.message.answer(text=hbold("Укажите причину закрытия заявки:"))
    await state.update_data(msg=msg)


@router.message(ChiefTechnicianTechnicalRequestForm.description)
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
    ShowRequestCallbackData.filter(F.end_point == "CT_TR_save_close_request")
)
async def save_close_request(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    data = await state.get_data()
    if "request_id" not in data:
        raise ValueError("Technical request id wasn't found")
    if "description" not in data:
        raise ValueError("Technical request description wasn't found")

    if not await set_not_relevant_state(
        request_id=data.get("request_id"),
        description=data.get("description"),
        telegram_id=callback.message.chat.id,
    ):
        raise ValueError(
            f"Technical request with id: {data.get('request_id')} wasn't update"
        )

    await state.clear()
    await state.set_state(Base.none)

    await show_tech_req_format(
        message=callback.message,
    )


# endregion
