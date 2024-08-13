from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
from fastapi import UploadFile

from bot import text, kb
from bot.states import Base, ChiefTechnicianTechnicalRequestForm

from bot.handlers.tech_request.schemas import ShowRequestCallbackData
from bot.handlers.tech_request import kb as tech_kb
from bot.handlers.utils import (
    download_file,
    handle_documents,
    handle_documents_form,
    notify_worker_by_telegram_id,
    try_delete_message,
    try_edit_or_answer,
)
from bot.handlers.tech_request.utils import (
    handle_department,
    show_form,
)

from db.service import (
    get_all_history_technical_requests_for_repairman,
    get_all_repairmans_in_department,
    get_all_rework_technical_requests_for_repairman,
    get_all_waiting_technical_requests_for_repairman,
    get_all_active_requests_in_department,
    get_departments_for_repairman,
    get_technical_request_by_id,
    update_tech_request_executor,
    update_technical_request_from_repairman,
)


router = Router(name="technical_request_chief_technician")


@router.callback_query(F.data == tech_kb.ct_button.callback_data)
async def show_tech_req_format_cb(callback: CallbackQuery):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(tech_kb.ct_button.text),
        reply_markup=tech_kb.ct_rm,
    )


async def show_tech_req_format_ms(message: Message):
    await try_edit_or_answer(
        message=message,
        text=hbold(tech_kb.ct_button.text),
        reply_markup=tech_kb.ct_rm,
    )


@router.callback_query(F.data == tech_kb.ct_change_department_button.callback_data)
async def get_department(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ChiefTechnicianTechnicalRequestForm.department)
    departments = get_departments_for_repairman(callback.message.chat.id)
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


@router.message(ChiefTechnicianTechnicalRequestForm.department)
async def set_department(message: Message, state: FSMContext):
    departments = get_departments_for_repairman(message.chat.id)
    if await handle_department(
        message=message,
        state=state,
        departments=departments,
        reply_markup=tech_kb.ct_menu_markup,
    ):
        await show_tech_req_format_ms(message)


# region Own requests
@router.callback_query(
    F.data == tech_kb.ct_own_button.callback_data,
)
async def show_own_requests(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f"Производство: {department_name}"),
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
        text=hbold(tech_kb.ct_own_waiting.text + f"\nПроизводство: {department_name}"),
        reply_markup=tech_kb.create_kb_with_end_point(
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
                    end_point="CT_TR_repair_form",
                ).pack(),
            )
        ]
    ]

    await show_form(
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
        reply_markup=await tech_kb.ct_repair_kb(
            state=state,
            callback_data=ShowRequestCallbackData(
                request_id=data.get("request_id"),
                end_point="CT_TR_repair_form",
            ),
        ),
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
        text=hbold(f"Заявки на доработку\nПроизводство: {department_name}"),
        reply_markup=tech_kb.create_kb_with_end_point(
            end_point="CT_TR_show_form_rework",
            menu_button=tech_kb.rm_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "CT_TR_show_form_rework")
)
async def show_rework_form(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="Выполнить заявку",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="CT_TR_repair_form",
                ).pack(),
            )
        ]
    ]
    await show_form(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_or_waiting_button=tech_kb.rm_rework,
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "CT_TR_repair_form")
)
async def show_repair_form_cb(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Выполнить заявку"),
        reply_markup=await tech_kb.rm_repair_rework_kb(
            state=state, callback_data=callback_data
        ),
    )


@router.callback_query(ShowRequestCallbackData.filter(F.end_point == "get_CT_TR_photo"))
async def get_repairman_photo(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await state.update_data(request_id=callback_data.request_id)
    await handle_documents_form(
        callback.message, state, ChiefTechnicianTechnicalRequestForm.photo
    )


@router.message(ChiefTechnicianTechnicalRequestForm.photo)
async def set_repairman_photo(message: Message, state: FSMContext):
    await handle_documents(
        message,
        state,
        "photo",
        show_own_waiting_form_format_ms,
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

    request_data = update_technical_request_from_repairman(
        photo_files=photo_files, request_id=callback_data.request_id
    )

    await notify_worker_by_telegram_id(
        id=request_data["territorial_manager_telegram_id"],
        message=text.notification_territorial_manager
        + f"\n На производстве: {request_data['department_name']}",
    )

    await notify_worker_by_telegram_id(
        id=request_data["worker_telegram_id"], message=text.notification_worker
    )

    await state.set_state(Base.none)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(tech_kb.ct_button.text),
        reply_markup=tech_kb.ct_rm,
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "CT_TR_repair_form")
)
async def show_repair_form(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Выполнить заявку"),
        reply_markup=await tech_kb.ct_repair_kb(
            state=state, callback_data=callback_data
        ),
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
        text=hbold(tech_kb.ct_own_history.text + f"\nПроизводство: {department_name}"),
        reply_markup=tech_kb.create_kb_with_end_point(
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
    await show_form(
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
    requests = get_all_active_requests_in_department(department_name)
    await try_edit_or_answer(
        callback.message,
        text=hbold(tech_kb.ct_admin_button.text + f"\nПредприятие: {department_name}"),
        reply_markup=tech_kb.create_kb_with_end_point(
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
    repairman = get_technical_request_by_id(callback_data.request_id).repairman
    repairman_full_name_old = " ".join(
        [repairman.l_name, repairman.f_name, repairman.o_name]
    )
    await state.update_data(repairman_full_name_old=repairman_full_name_old)
    buttons: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="Сменить исполнителя",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="show_CT_TR_change_executor",
                ).pack(),
            )
        ]
    ]

    await show_form(
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
    ShowRequestCallbackData.filter(F.end_point == "get_CT_TR_executor")
)
async def get_executor(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    await state.set_state(ChiefTechnicianTechnicalRequestForm.executor)
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


@router.message(ChiefTechnicianTechnicalRequestForm.executor)
async def set_executor(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    if msg:
        await try_delete_message(msg)
    await try_delete_message(message)

    if message.text == text.back:
        await show_tech_req_format_ms(message)
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

        await state.update_data(repairman_full_name_new=message.text)
        await show_change_executor_format_ms(message=message, state=state)


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "save_CT_TR_admin_form")
)
async def save_CT_TR_admin_form(
    callback: CallbackQuery, callback_data: ShowRequestCallbackData, state: FSMContext
):
    request_id = callback_data.request_id
    repairman_full_name = (
        (await state.get_data()).get("repairman_full_name_new").split(" ")
    )
    repairman_TG_id = update_tech_request_executor(
        request_id=request_id, repairman_full_name=repairman_full_name
    )
    data = await state.get_data()
    await notify_worker_by_telegram_id(
        id=repairman_TG_id,
        message="Вас назначили на заявку"
        + f"\n На производстве: {data.get('department_name')}",
    )
    await state.clear()
    await state.set_state(Base.none)
    await show_tech_req_format_cb(callback=callback)


# endregion
