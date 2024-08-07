from aiogram import Router, F

from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from fastapi import UploadFile

from bot import text
from bot.states import (
    Base,
    RepairmanTechnicalRequestForm,
)
from bot.kb import (
    repairman_tech_req_menu_button,
    repairman_tech_req_menu,
    repairman_tech_req_waiting,
    repairman_repair_tech_req_kb,
    repairman_tech_req_history,
)
from bot.handlers.utils import (
    notify_worker_by_telegram_id,
    try_edit_or_answer,
    try_delete_message,
    download_file,
    handle_documents_form,
    handle_documents,
)
from bot.handlers.tech_req.utils import (
    create_keybord_with_end_point,
    show_form,
)
from bot.handlers.tech_req.schemas import ShowRequestCallbackData

from db.service import (
    get_all_history_technical_requests_by_repairman_TG_and_department_id,
    get_all_waiting_technical_requests_by_repairman_TG_id_and_department_id,
    update_technical_request_repairman,
)

router = Router(name="technical_request_repairman")


@router.callback_query(F.data == repairman_tech_req_menu_button.callback_data)
async def repairman_menu(callback: CallbackQuery):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=repairman_tech_req_menu,
    )


@router.callback_query(F.data == repairman_tech_req_history.callback_data)
async def repairman_history(callback: CallbackQuery, state):
    requests = get_all_history_technical_requests_by_repairman_TG_and_department_id(
        telegram_id=callback.message.chat.id
    )

    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("История заявок"),
        reply_markup=create_keybord_with_end_point(
            end_point="repairman_show_form_history",
            menu_button=repairman_tech_req_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "repairman_show_form_history")
)
async def repairman_show_form_history(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons: list[list[InlineKeyboardButton]] = []
    await show_form(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_button=repairman_tech_req_history,
    )


@router.callback_query(F.data == repairman_tech_req_waiting.callback_data)
async def repairman_waiting(callback: CallbackQuery):
    requests = get_all_waiting_technical_requests_by_repairman_TG_id_and_department_id(
        telegram_id=callback.message.chat.id
    )
    await try_delete_message(callback.message)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Ожидающие заявки"),
        reply_markup=create_keybord_with_end_point(
            end_point="repairman_show_form_waiting",
            menu_button=repairman_tech_req_menu_button,
            requests=requests,
        ),
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "repairman_show_form_waiting")
)
async def repairman_show_form_waiting(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    buttons: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="Выполнить заявку",
                callback_data=ShowRequestCallbackData(
                    request_id=callback_data.request_id,
                    end_point="repairman_repair_form",
                ).pack(),
            )
        ]
    ]
    await show_form(
        callback=callback,
        callback_data=callback_data,
        state=state,
        buttons=buttons,
        history_button=repairman_tech_req_waiting,
    )


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "repairman_repair_form")
)
async def repairman_repair_form_cb(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Выполнить заявку"),
        reply_markup=await repairman_repair_tech_req_kb(
            state=state, callback_data=callback_data
        ),
    )


async def repairman_repair_form_ms(message: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await try_edit_or_answer(
        message=message,
        text=hbold("Выполнить заявку"),
        reply_markup=await repairman_repair_tech_req_kb(
            state=state,
            callback_data=ShowRequestCallbackData(
                request_id=data.get("request_id"),
                end_point="repairman_repair_form",
            ),
        ),
    )


@router.callback_query(ShowRequestCallbackData.filter(F.end_point == "get_photo"))
async def get_repairman_photo(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    await state.update_data(request_id=callback_data.request_id)
    await handle_documents_form(
        callback.message, state, RepairmanTechnicalRequestForm.photo
    )


@router.message(RepairmanTechnicalRequestForm.photo)
async def set_repairman_photo(message: Message, state: FSMContext):
    await handle_documents(message, state, "photo", repairman_repair_form_ms)


@router.callback_query(
    ShowRequestCallbackData.filter(F.end_point == "save_repairman_repair")
)
async def save_repairman_repair(
    callback: CallbackQuery, state: FSMContext, callback_data: ShowRequestCallbackData
):
    data = await state.get_data()

    photo = data["photo"]
    photo_files: list[UploadFile] = []
    for doc in photo:
        photo_files.append(await download_file(doc))

    teritorial_manager_id = update_technical_request_repairman(
        photo_files=photo_files, request_id=callback_data.request_id
    )

    await notify_worker_by_telegram_id(
        id=teritorial_manager_id, message=text.notifay_teritorial_manager
    )

    await state.clear()
    await state.set_state(Base.none)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold("Тех. заявки"),
        reply_markup=repairman_tech_req_menu,
    )
