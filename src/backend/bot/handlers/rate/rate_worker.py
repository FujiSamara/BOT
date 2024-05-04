from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.kb import create_inline_keyboard
from db import service

router = Router(name="rating")


@router.callback_query(F.data == "get_rating_menu")
async def get_rating_list(callback: CallbackQuery, state: FSMContext):
    records = service.get_work_time_records_by_department()
