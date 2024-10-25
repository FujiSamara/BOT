from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
)

from bot.kb import (
    get_per_cab_monitoring_list_btn,
    main_menu_button,
    get_monitoring_menu_btn,
)
from bot.handlers.utils import (
    try_edit_or_answer,
)
from bot.handlers.perconal_cab import utils


router = Router(name="personal_cabinet")


@router.callback_query(F.data == get_monitoring_menu_btn.callback_data)
async def get_monitoring_menu_btn(callback: CallbackQuery):
    pass


@router.callback_query(F.data == get_per_cab_monitoring_list_btn.callback_data)
async def get_monitoring_list(callback: CallbackQuery):
    await try_edit_or_answer(
        text=utils.get_monitoring_list(),
        message=callback.message,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[main_menu_button]]),
    )
