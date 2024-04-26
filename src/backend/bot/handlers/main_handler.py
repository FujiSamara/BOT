from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    ErrorEvent,
    ReplyKeyboardRemove
)
from aiogram.fsm.context import FSMContext
from bot.text import first_run_text
from bot.states import Auth
from db.service import (
    get_user_level_by_telegram_id
)
from bot.states import Base
import logging
from bot.text import err
import asyncio
from bot.handlers.utils import send_menu_by_level


router = Router(name="main")


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    level = get_user_level_by_telegram_id(message.from_user.id)
    if level == -1:
        await state.set_state(Auth.authing)
        await message.answer(first_run_text(message.from_user.full_name))
        return
    await state.set_state(Base.none)
    await send_menu_by_level(message)


@router.message(Base.none)
async def delete_extra(message: Message):
    await message.delete()


@router.callback_query(F.data == "get_menu")
async def get_menu_by_level(callback: CallbackQuery):
    '''Sends specific menu for user by his role.
    '''
    await send_menu_by_level(callback.message, edit=True)


@router.error()
async def error_handler(event: ErrorEvent):
    logging.getLogger("uvicorn.error").error(
        f"Error occurred:{event.exception}")
    message = event.update.callback_query.message
    try:
        await message.edit_text(err, reply_markup=ReplyKeyboardRemove())
        msg = message
    except Exception:
        msg = await message.answer(err, reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(3)
    await send_menu_by_level(msg, edit=True)
