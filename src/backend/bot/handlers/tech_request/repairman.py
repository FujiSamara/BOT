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
from bot.states import (
    Base,
    RepairmanTechnicalRequestForm,
)

from bot.handlers.tech_request.schemas import ShowRequestCallbackData
from bot.handlers.tech_request import kb as tech_kb
from bot.handlers.utils import (
    notify_worker_by_telegram_id,
    try_edit_or_answer,
    try_delete_message,
    download_file,
    handle_documents_form,
    handle_documents,
)
from bot.handlers.tech_request.utils import (
    handle_department,
    show_form,
)


from db.service import (
    get_all_history_technical_requests_for_repairman,
    get_all_rework_technical_requests_for_repairman,
    get_all_waiting_technical_requests_for_repairman,
    get_deparments_for_repairman,
    update_technical_request_from_repairman,
)


router = Router(name="technical_request_repairman")


@router.callback_query(F.data == tech_kb.rm_button.callback_data)
async def show_tech_req_format_cb(callback: CallbackQuery):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=tech_kb.rm_change_deparment_menu,
    )


async def show_tech_rec_format_ms(message: Message):
    await message.answer(
        text=hbold("Тех. заявки"),
        reply_markup=tech_kb.rm_change_deparment_menu,
    )


@router.callback_query(F.data == tech_kb.rm_change_department_button.callback_data)
async def change_department(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RepairmanTechnicalRequestForm.department)
    departments = get_deparments_for_repairman(callback.message.chat.id)
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


@router.message(RepairmanTechnicalRequestForm.department)
async def set_department(message: Message, state: FSMContext):
    departments = get_deparments_for_repairman(message.chat.id)
    if await handle_department(
        message=message,
        state=state,
        departments=departments,
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
                    end_point="RM_TR_repair_form",
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


@router.callback_query(F.data == tech_kb.rm_rework.callback_data)
async def show_rework_menu(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department_name")
    requests = get_all_rework_technical_requests_for_repairman(
        telegram_id=callback.message.chat.id, department_name=department_name
    )
    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f"Заявки на дорабоку\nПроизводство: {department_name}"),
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
                    end_point="RM_TR_repair_form",
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
    ShowRequestCallbackData.filter(F.end_point == "RM_TR_repair_form")
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


async def show_repair_form_ms(message: Message, state: FSMContext):
    data = await state.get_data()
    await try_edit_or_answer(
        message=message,
        text=hbold("Выполнить заявку"),
        reply_markup=await tech_kb.rm_repair_waiting_kb(
            state=state,
            callback_data=ShowRequestCallbackData(
                request_id=data.get("request_id"),
                end_point="RM_TR_repair_form",
            ),
        ),
    )


@router.callback_query(ShowRequestCallbackData.filter(F.end_point == "get_RM_TR_photo"))
async def get_photo(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await state.update_data(request_id=callback_data.request_id)
    await handle_documents_form(
        callback.message, state, RepairmanTechnicalRequestForm.photo
    )


@router.message(RepairmanTechnicalRequestForm.photo)
async def set_photo(message: Message, state: FSMContext):
    await handle_documents(message, state, "photo", show_repair_form_ms)


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
        text=hbold("Тех. заявки"),
        reply_markup=tech_kb.rm_change_deparment_menu,
    )
