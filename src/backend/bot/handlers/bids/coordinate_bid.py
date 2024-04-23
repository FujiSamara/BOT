from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from typing import Any

from bot.kb import (
    main_menu_button,
    create_inline_keyboard,
    InlineKeyboardButton,
    kru_menu_button
)

from db.models import Bid

router = Router(name="bid_coordination")

class CoordinationFactory():

    def __init__(
            self,
            router: Router,
            coordinator_menu_button: InlineKeyboardButton,
            state_column: Any
        ):
        router.callback_query.register(self.get_menu, F.data == coordinator_menu_button.callback_data)


    async def get_menu(self, callback: CallbackQuery, state: FSMContext):
        keyboard = create_inline_keyboard(
            main_menu_button
        )

        await callback.message.edit_text(text="Добро пожаловать!", reply_markup=keyboard)

    async def get_history(self, callback: CallbackQuery):
        pass




def build_coordinations():
    kru_factory = CoordinationFactory(
        router=router,
        coordinator_menu_button=kru_menu_button,
        state_column=Bid.kru_state
    )