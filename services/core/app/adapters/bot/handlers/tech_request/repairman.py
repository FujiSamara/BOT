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
from app.adapters.bot.states import (
    Base,
    RepairmanTechnicalRequestForm,
)

from app.adapters.bot.handlers.tech_request.schemas import ShowRequestCallbackData
from app.adapters.bot.handlers.tech_request import kb as tech_kb
from app.adapters.bot.handlers.utils import (
    notify_worker_by_telegram_id,
    try_edit_or_answer,
    try_delete_message,
    download_file,
    handle_documents_form,
    handle_documents,
)
from app.adapters.bot.handlers.tech_request.utils import (
    handle_department,
    show_form,
    department_names_with_count,
)


from app.services import (
    get_all_history_technical_requests_for_repairman,
    get_all_rework_technical_requests_for_repairman,
    get_all_waiting_technical_requests_for_repairman,
    get_departments_names_for_repairman,
    update_technical_request_from_repairman,
)
from app.database.models import ApprovalStatus

router = Router(name="technical_request_repairman")


@router.callback_query(F.data == tech_kb.rm_button.callback_data)
async def show_tech_req_format_cb(callback: CallbackQuery):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=tech_kb.rm_change_department_menu,
    )


async def show_tech_rec_format_ms(message: Message):
    await message.answer(
        text=hbold("Тех. заявки"),
        reply_markup=tech_kb.rm_change_department_menu,
    )


@router.callback_query(F.data == tech_kb.rm_change_department_button.callback_data)
async def change_department(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RepairmanTechnicalRequestForm.department)
    department_names = department_names_with_count(
        state=ApprovalStatus.pending,
        tg_id=callback.message.chat.id,
        department_names=get_departments_names_for_repairman(callback.message.chat.id),
    )

    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        text=hbold("Выберите производство:"),
        reply_markup=kb.create_reply_keyboard(text.back, *department_names),
    )
    await state.update_data(msg=msg)


@router.message(RepairmanTechnicalRequestForm.department)
async def set_department(message: Message, state: FSMContext):
    if await handle_department(
        message=message,
        state=state,
        departments_names=department_names_with_count(
            state=ApprovalStatus.pending,
            tg_id=message.chat.id,
            department_names=get_departments_names_for_repairman(message.chat.id),
        ),
        reply_markup=tech_kb.rm_menu_markup,
    ):
        await show_tech_rec_format_ms(message)


@router.callback_query(F.data == tech_kb.rm_menu_button.callback_data)
async def show_menu(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f"Производство: {department_name}"),
        reply_markup=tech_kb.rm_menu_markup,
    )


@router.callback_query(F.data == tech_kb.rm_history.callback_data)
async def show_history_menu(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    requests = get_all_history_technical_requests_for_repairman(
        telegram_id=callback.message.chat.id, department_name=department_name
    )

    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f"История заявок.\nПроизводство: {department_name}"),
        reply_markup=tech_kb.create_kb_with_end_point(
            end_point="RM_TR_show_form_history",
            menu_button=tech_kb.rm_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "RM_TR_show_form_history")
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
        history_or_waiting_button=tech_kb.rm_history,
    )


@router.callback_query(F.data == tech_kb.rm_waiting.callback_data)
async def show_waiting_menu(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    requests = get_all_waiting_technical_requests_for_repairman(
        telegram_id=callback.message.chat.id, department_name=department_name
    )
    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f"Ожидающие заявки\nПроизводство: {department_name}"),
        reply_markup=tech_kb.create_kb_with_end_point(
            end_point="RM_TR_show_form_waiting",
            menu_button=tech_kb.rm_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "RM_TR_show_form_waiting")
)
async def show_waiting_form(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="Выполнить заявку",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="RM_TR_repair_waiting_form",
                ).pack(),
            )
        ]
    ]
    await show_form(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_or_waiting_button=tech_kb.rm_waiting,
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "RM_TR_repair_waiting_form")
)
async def show_repair_waiting_form_cb(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Выполнить заявку"),
        reply_markup=await tech_kb.rm_repair_waiting_kb(
            state=state, callback_data=callback_data
        ),
    )


async def show_repair_waiting_form_ms(message: Message, state: FSMContext):
    data = await state.get_data()
    await try_edit_or_answer(
        message=message,
        text=hbold("Выполнить заявку"),
        reply_markup=await tech_kb.rm_repair_waiting_kb(
            state=state,
            callback_data=ShowRequestCallbackData(
                request_id=data.get("request_id"),
                end_point="RM_TR_repair_waiting_form",
            ),
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "get_RM_TR_waiting_photo")
)
async def get_waiting_photo(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await state.update_data(request_id=callback_data.request_id)
    await handle_documents_form(
        callback.message, state, RepairmanTechnicalRequestForm.photo_waiting
    )


@router.message(RepairmanTechnicalRequestForm.photo_waiting)
async def set_waiting_photo(message: Message, state: FSMContext):
    await handle_documents(message, state, "photo", show_repair_waiting_form_ms)


@router.callback_query(F.data == tech_kb.rm_rework.callback_data)
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
            end_point="RM_TR_show_form_rework",
            menu_button=tech_kb.rm_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "RM_TR_show_form_rework")
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
                    end_point="RM_TR_repair_rework_form",
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
    ShowRequestCallbackData.filter(F.end_point == "RM_TR_repair_rework_form")
)
async def show_repair_rework_form_cb(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Выполнить заявку"),
        reply_markup=await tech_kb.rm_repair_rework_kb(
            state=state, callback_data=callback_data
        ),
    )


async def show_repair_rework_form_ms(message: Message, state: FSMContext):
    data = await state.get_data()
    await try_edit_or_answer(
        message=message,
        text=hbold("Выполнить заявку"),
        reply_markup=await tech_kb.rm_repair_rework_kb(
            state=state,
            callback_data=ShowRequestCallbackData(
                request_id=data.get("request_id"),
                end_point="RM_TR_repair_rework_form",
            ),
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "get_RM_TR_rework_photo")
)
async def get_rework_photo(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await state.update_data(request_id=callback_data.request_id)
    await handle_documents_form(
        callback.message, state, RepairmanTechnicalRequestForm.photo_rework
    )


@router.message(RepairmanTechnicalRequestForm.photo_rework)
async def set_rework_photo(message: Message, state: FSMContext):
    await handle_documents(message, state, "photo", show_repair_rework_form_ms)


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "save_RM_TR_repair")
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

    await state.clear()
    await state.set_state(Base.none)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=tech_kb.rm_change_department_menu,
    )
