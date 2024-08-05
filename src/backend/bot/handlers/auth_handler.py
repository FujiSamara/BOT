from aiogram import Router, flags
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

# bot imports
from bot.text import user_not_exist_text

from bot.states import Auth, Base

from bot.handlers.main_handler import send_menu_by_scopes

# db imports
from db.service import update_worker_tg_id_by_number


router = Router(name="auth")


@router.message(Auth.authing)
@flags.chat_action("typing")
async def auth(message: Message, state: FSMContext):
    if update_worker_tg_id_by_number(message.html_text, message.from_user.id):
        await state.set_state(Base.none)
        await send_menu_by_scopes(message)
    else:
        await message.answer(user_not_exist_text)
