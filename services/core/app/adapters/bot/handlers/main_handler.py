from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, ErrorEvent, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

import asyncio

from app.infra.logging import logger
import app.db.service as service

from app.adapters.bot.handlers.utils import send_menu_by_scopes, try_delete_message
from app.adapters.bot.text import err
from app.adapters.bot.states import Base
from app.adapters.bot.states import Auth
from app.adapters.bot.text import first_run_text


router = Router(name="main")


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    worker = service.get_worker_by_telegram_id(message.from_user.id)
    if not worker:
        await state.set_state(Auth.authing)
        await message.answer(first_run_text(message.from_user.full_name))
        return
    await state.clear()
    await state.set_state(Base.none)
    await send_menu_by_scopes(message)


@router.message(Base.none)
async def delete_extra(message: Message):
    await message.delete()


@router.callback_query(F.data == "get_menu")
async def get_menu_by_scope(callback: CallbackQuery, state: FSMContext):
    """Sends specific menu for user by his role."""
    await state.clear()
    await state.set_state(Base.none)
    await send_menu_by_scopes(callback.message, edit=True)


@router.error()
async def error_handler(event: ErrorEvent):
    logger.error(f"Error occurred: {event.exception}")
    message = event.update.callback_query.message
    await try_delete_message(message)
    msg = await message.answer(err, reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(3)
    await msg.delete()
    await send_menu_by_scopes(msg)
