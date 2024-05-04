from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from bot.kb import create_inline_keyboard, main_menu_button
from db import service
from bot.handlers.utils import try_edit_or_answer

router = Router(name="rating")


@router.callback_query(F.data == "get_rating_menu")
async def get_rating_list(callback: CallbackQuery, state: FSMContext):
    department = service.get_worker_department_by_telegram_id(callback.message.chat.id)
    records = service.get_work_time_records_by_department(department.id)

    buttons = [
        *(
            InlineKeyboardButton(text=f"{record.day}", callback_data="kek")
            for record in records
        ),
        main_menu_button,
    ]

    keyboard = create_inline_keyboard(*buttons)

    await try_edit_or_answer(
        message=callback.message, text="Выберите смену:", reply_markup=keyboard
    )
