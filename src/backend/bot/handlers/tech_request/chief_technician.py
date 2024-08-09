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
    get_all_waiting_technical_requests_for_repairman,
    get_deparments_for_repairman,
    update_technical_request_from_repairman,
)


router = Router(name="technical_request_chief_technician")


@router.callback_query(F.data == tech_kb.CT_button.callback_data)
async def show_tech_req_format_cb(callback: CallbackQuery):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=tech_kb.CT_rm,
    )


async def show_tech_req_format_ms(message: Message):
    await try_edit_or_answer(
        message=message,
        text=hbold(tech_kb.CT_button.text),
        reply_markup=tech_kb.CT_rm,
    )


@router.callback_query(F.data == tech_kb.CT_change_department_button.callback_data)
async def get_department(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ChiefTechnicianTechnicalRequestForm.department)
    departments = get_deparments_for_repairman(callback.message.chat.id)

    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите производство:"),
        reply_markup=kb.create_reply_keyboard(
            "⏪ Назад", *[department.name for department in departments]
        ),
    )
    await state.update_data(msg=msg)


@router.message(ChiefTechnicianTechnicalRequestForm.department)
async def set_department(message: Message, state: FSMContext):
    deparments = get_deparments_for_repairman(message.chat.id)
    if await handle_department(
        message=message,
        state=state,
        departments=deparments,
        reply_markup=tech_kb.CT_menu_markup,
    ):
        await show_tech_req_format_ms(message)


# region Chief technician own requests
@router.callback_query(
    F.data == tech_kb.CT_own_button.callback_data,
)
async def show_own_requests(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f"Производство: {department_name}"),
        reply_markup=tech_kb.CT_own_menu_markup,
    )


@router.callback_query(F.data == tech_kb.CT_own_waiting.callback_data)
async def show_own_waiting(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    requests = get_all_waiting_technical_requests_for_repairman(
        telegram_id=callback.message.chat.id, department_name=department_name
    )
    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f"Ожидающие заявки.\nПроизводство: {department_name}"),
        reply_markup=tech_kb.create_kb_with_end_point(
            end_point="chief_technician_show_form_waiting",
            menu_button=tech_kb.CT_own_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "chief_technician_show_form_waiting")
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
                    end_point="chief_technician_repair_form",
                ).pack(),
            )
        ]
    ]

    await show_form(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_or_waiting_button=tech_kb.CT_own_waiting,
    )


async def show_own_waiting_form_format_ms(message: Message, state: FSMContext):
    data = await state.get_data()
    await try_edit_or_answer(
        message=message,
        text=hbold("Выполнить заявку"),
        reply_markup=await tech_kb.CT_repair_kb(
            state=state,
            callback_data=ShowRequestCallbackData(
                request_id=data.get("request_id"),
                end_point="repairman_repair_form",
            ),
        ),
    )


@router.callback_query(ShowRequestCallbackData.filter(F.end_point == "get_CT_photo"))
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
    ShowRequestCallbackData.filter(F.end_point == "save_chief_technician_repair")
)
async def save_repair(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    data = await state.get_data()

    photo = data["photo"]
    photo_files: list[UploadFile] = []
    for doc in photo:
        photo_files.append(await download_file(doc))

    req_data = update_technical_request_from_repairman(
        photo_files=photo_files, request_id=callback_data.request_id
    )

    await notify_worker_by_telegram_id(
        id=req_data["territorial_manager_telegram_id"],
        message=text.notification_teritorial_manager
        + f"\n На производстве: {req_data["department_name"]}",
    )

    await state.clear()
    await state.set_state(Base.none)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(tech_kb.CT_button.text),
        reply_markup=tech_kb.CT_rm,
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "chief_technician_repair_form")
)
async def show_repair_form(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Выполнить заявку"),
        reply_markup=await tech_kb.CT_repair_kb(
            state=state, callback_data=callback_data
        ),
    )


@router.callback_query(F.data == tech_kb.CT_own_history.callback_data)
async def show_own_history(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    requests = get_all_history_technical_requests_for_repairman(
        telegram_id=callback.message.chat.id, department_name=department_name
    )
    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f"История заявок.\nПроизводство: {department_name}"),
        reply_markup=tech_kb.create_kb_with_end_point(
            end_point="chief_technician_show_form_history",
            menu_button=tech_kb.CT_own_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(
        F.end_point == "show_chief_technician_own_history_form"
    )
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
        history_or_waiting_button=tech_kb.CT_own_history,
    )


# endregion

# region Chief technician admin

# endregion
