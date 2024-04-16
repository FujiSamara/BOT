from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
from bot.text import first_run_text
from bot.states import Auth
from db.service import get_user_level_by_telegram_id
from bot.kb import create_bid_menu_button
from bot.states import Base


router = Router(name="main")

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    level = get_user_level_by_telegram_id(message.from_user.id)
    if level == -1:
        await state.set_state(Auth.authing)
        await message.answer(first_run_text(message.from_user.full_name))
        return
    await send_menu_by_level(message)

@router.message(Base.none)
async def start(message: Message):
    await message.delete()

@router.callback_query(F.data == "get_menu")
async def get_menu_by_level(callback: CallbackQuery):
    '''Sends specific menu for user by his role.
    '''
    await send_menu_by_level(callback.message, edit=True)

async def send_menu_by_level(message: Message, edit=None):
    '''
    Sends specific menu for user by his role.

    If `edit = True` - calling `Message.edit_text` instead `Message.answer`
    '''
    level = get_user_level_by_telegram_id(message.chat.id)
    menus = []
    if level > 3:
        menus.append([create_bid_menu_button])

    # TODO: finish remaining menus.
    
    menu = InlineKeyboardMarkup(inline_keyboard=menus)
    if edit:
        await message.edit_text(hbold("Выберите дальнейшее действие:"), reply_markup=menu)
    else:
        await message.answer(hbold("Выберите дальнейшее действие:"), reply_markup=menu)