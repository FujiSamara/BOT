from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.handlers.bids_it import (
    create_bid_it,
    repairman,
    territorial_manager,
)
from aiogram.utils.markdown import hbold

# bot imports
from bot.kb import bid_it_menu


from bot.states import Base


router = Router(name="bid_it_main")

# Main section


# Create menu
@router.callback_query(F.data == "get_create_bid_it_menu")
async def get_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Base.none)
    await callback.message.edit_text(
        hbold("Заявка в IT отдел"), reply_markup=bid_it_menu
    )


# Create section
# coordinate_bid.build_coordinations() # хз что это

router.include_routers(create_bid_it.router, repairman.router, territorial_manager.router)
