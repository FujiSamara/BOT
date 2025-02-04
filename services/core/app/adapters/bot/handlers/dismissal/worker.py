from fastapi import UploadFile
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    Message,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
import asyncio

# bot imports
from app.adapters.bot.kb import dismissal_menu
from app.adapters.bot.states import (
    Base,
    DismissalRequest,
)

from app.adapters.bot.handlers.utils import (
    send_menu_by_scopes,
    try_delete_message,
    try_edit_message,
    download_file,
    handle_documents,
    handle_documents_form,
)
from app.adapters.bot.handlers.dismissal.utils import (
    clear_state_with_success_employee,
    with_next_line,
)

# db imports
from app.services import (
    create_dismissal_blank,
    get_worker_info_by_telegram_id,
)

router = Router(name="employee")


@router.callback_query(F.data == "get_create_dismissal_menu")
async def get_create_dismissal_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(Base.none)
    worker_info_list = get_worker_info_by_telegram_id(callback.message.chat.id)
    worker_info = with_next_line(worker_info_list)
    await callback.message.edit_text(hbold(worker_info), reply_markup=dismissal_menu)


@router.callback_query(F.data == "create_dismissal_request")
async def create_dismissal_request(callback: CallbackQuery, state: FSMContext):
    await clear_state_with_success_employee(callback.message, state, edit=True)


@router.callback_query(F.data == "upload_dismissal_blank")
async def upload_dismissal_blank(callback: CallbackQuery, state: FSMContext):
    await handle_documents_form(callback.message, state, DismissalRequest.blank)


@router.message(DismissalRequest.blank)
async def handle_dismissal_blank(message: Message, state: FSMContext):
    await handle_documents(
        message,
        state,
        "blank",
        clear_state_with_success_employee,
    )


@router.callback_query(F.data == "get_dismissal_reason")
async def get_dismissal_reason(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DismissalRequest.dismissal_reason)
    await try_delete_message(callback.message)
    msg = await callback.message.answer(hbold("Введите причину увольнения:"))
    await state.update_data(msg=msg)


@router.message(DismissalRequest.dismissal_reason)
async def handle_dismissal_reason(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    await state.update_data(dismissal_reason=message.text)
    await try_delete_message(message)
    await try_delete_message(msg)
    await clear_state_with_success_employee(message, state)


@router.callback_query(F.data == "send_dismissal_blank")
async def send_dismissal_blank(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    blank = data.get("blank")
    dismissal_reason = data.get("dismissal_reason")
    document_files: list[UploadFile] = []

    for doc in blank:
        document_files.append(await download_file(doc))

    ans = await create_dismissal_blank(
        files=document_files,
        dismissal_reason=dismissal_reason,
        telegram_id=callback.message.chat.id,
    )
    if not ans:
        await try_edit_message(message=callback.message, text="У вас нет руководителя")
    else:
        await try_edit_message(message=callback.message, text="Успешно!")
    await asyncio.sleep(1)
    await state.clear()
    await state.set_state(Base.none)
    await send_menu_by_scopes(callback.message, edit=True)
