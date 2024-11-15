from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
from bot.handlers.bids import create_bid
from bot.handlers.bids import coordinate_bid
from bot.handlers.bids import worker_bid

# bot imports
from bot.kb import bid_menu


from bot.states import Base


router = Router(name="bid_main")


# Main section


# Create menu
@router.callback_query(F.data == "get_create_bid_menu")
async def get_menu(message: CallbackQuery | Message, state: FSMContext):
    if isinstance(message, CallbackQuery):
        message = message.message
    await state.set_state(Base.none)
    await message.edit_text(hbold("Заявки на оплату платежей"), reply_markup=bid_menu)


# Create section
coordinate_bid.build_coordinations()

router.include_routers(create_bid.router, coordinate_bid.router, worker_bid.router)
