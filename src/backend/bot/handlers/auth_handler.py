from aiogram import Router, flags
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

# bot imports
from bot.text import user_not_exist_text

from bot.states import Auth

from bot.handlers.main_handler import send_menu_by_access

# db imports
from db.service import update_user_tg_id_by_number



router = Router(name="auth")

@router.message(Auth.authing)
@flags.chat_action("typing")
async def auth(message: Message, state: FSMContext):
    if update_user_tg_id_by_number(message.html_text, message.from_user.id):
        await state.clear()
        await send_menu_by_access(message)
    else:
        await message.answer(user_not_exist_text)
        