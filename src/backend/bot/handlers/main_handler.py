from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
from bot.text import first_run_text
from bot.states import Auth
from db.service import get_user_level_by_telegram_id


router = Router(name="main")

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    level = get_user_level_by_telegram_id(message.from_user.id)
    if level == -1:
        await state.set_state(Auth.authing)
        await message.answer(first_run_text(message.from_user.full_name))
        return
    await send_menu_by_level(message)

from bot.kb import bid_menu

async def send_menu_by_level(message: Message):
    '''Sends specific menu for user by his role.
    '''
    if True: # bid menu
        await message.answer(hbold("Добро пожаловать!"), reply_markup=bid_menu)
    else:
        pass
    # TODO: Make menu switching