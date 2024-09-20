from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
import kb
from utils import try_edit_or_answer
from db.service import get_worker_by_telegram_id

router = Router(name="personal_account")


@router.callback_query(F.data == kb.open_personal_account.callback_data)
async def get_personal_data(callback: CallbackQuery):
    worker = get_worker_by_telegram_id(callback.message.chat.id)
    text = f"{worker.l_name, worker.f_name, worker.o_name}"
    
    await try_edit_or_answer(
        text=text,
        reply_markup=(InlineKeyboardMarkup(inline_keyboard=[[kb.main_menu_button]])),
    )
