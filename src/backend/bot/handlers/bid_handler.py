from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

# bot imports
from bot.kb import bid_menu

# db imports


router = Router(name="bid")

@router.callback_query(F.data == "get_menu")
async def get_menu(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(hbold("Добро пожаловать!"), reply_markup=bid_menu)
