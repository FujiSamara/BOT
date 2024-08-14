# Department.territorial_manager_id

# import asyncio
# from io import BytesIO
# from typing import Optional
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    # InlineKeyboardButton,
    # InlineKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

# from fastapi import UploadFile

from bot.text import format_err

from bot.kb import (
    tm_department_menu,
    create_reply_keyboard,
    tm_bids_it_menu,
#     repairman_department_menu,
#     create_inline_keyboard,
#     get_create_repairman_it_menu,
#     bids_pending_for_repairman,
)
from bot.states import TMForm

# from bot.text import bid_create_greet
from bot.handlers.utils import (
    try_edit_or_answer,
    try_delete_message,
    try_edit_message,
    # download_file,
    #     handle_documents_form,
    #     handle_documents,
)
# from bot.handlers.bids_it.utils import (
#     get_bid_it_list_info,
#     get_short_bid_it_info,
# )
# from bot.handlers.bids_it.schemas import (
#     BidITViewMode,
#     BidITViewType,
#     BidITCallbackData,
#     RepairmanBidITCallbackData,
# )


from db.service import (
#     update_bid_it_rm,
    get_departments_names_by_tm_telegram_id,
#     get_pending_bids_it_by_worker_telegram_id,
#     get_bid_it_by_id,
)

router = Router(name="bid_it_territorial_manager")

@router.callback_query(F.data == "get_it_tm_menu")
async def get_tm_it_menu(callback: CallbackQuery):
    await try_edit_message(
        message=callback.message,
        text="IT заявки ТУ",
        reply_markup=tm_department_menu,
    )

@router.callback_query(F.data == "get_department_it_tm")
async def get_tm_department_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TMForm.department)
    dep = get_departments_names_by_tm_telegram_id(callback.message.chat.id)
    await try_delete_message(callback.message)
    await callback.message.answer(
        hbold("Выберите производство:"),
        reply_markup=create_reply_keyboard("⏪ Назад", *dep),
    )

@router.message(TMForm.department)
async def set_department_type(message: Message, state: FSMContext):
    dep = get_departments_names_by_tm_telegram_id(message.from_user.id)
    if message.text == "⏪ Назад":
        await state.clear()
        await try_edit_message(
            message=message,
            text="IT заявки ТУ",
            reply_markup=tm_department_menu,
        )
    elif message.text in dep:
        await state.update_data(department=message.text)
        await try_edit_or_answer(
            message=message,
            text=hbold(f'Заявки на производстве "{message.text}"'),
            reply_markup=tm_bids_it_menu,
        )
    else:
        await message.answer(format_err)