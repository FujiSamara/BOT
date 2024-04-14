from aiogram import Router, flags
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

# bot imports
from bot.text import user_not_exist_text

from bot.states import Auth

from bot.handlers.main_handler import send_menu_by_role

# db imports
from db.service import set_user_tg_id_by_number



router = Router(name="auth")

@router.message(Auth.authing)
@flags.chat_action("typing")
async def auth(message: Message, state: FSMContext):
    if set_user_tg_id_by_number(message.html_text):
        await state.clear()
        await message.answer(hbold("Пожалуйста подождите..."))
        await send_menu_by_role()
    else:
        await message.answer(user_not_exist_text)
        