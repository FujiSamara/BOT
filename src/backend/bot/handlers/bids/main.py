from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

# bot imports
from bot.kb import (
    bid_menu
)


from bot.states import Base


router = Router(name="bid_main")


### Main section
@router.callback_query(F.data == "get_bid_menu")
async def get_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Base.none)
    await callback.message.edit_text(hbold("Добро пожаловать!"), reply_markup=bid_menu)

### Create section
from bot.handlers.bids import create_bid

router.include_routers(
    create_bid.router
)