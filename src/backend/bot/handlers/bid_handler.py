from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

# bot imports
from bot.kb import bid_menu, create_bid_menu, main_menu, main_menu_button

from bot.text import bid_amount_err

from bot.states import BidCreating

from bot.bot import get_bot

# db imports


router = Router(name="bid")

@router.callback_query(F.data == "get_bid_menu")
async def get_menu(callback: CallbackQuery):
    await callback.message.edit_text(hbold("Добро пожаловать!"), reply_markup=bid_menu)

@router.callback_query(F.data == "create_bid")
async def get_create_menu(callback: CallbackQuery):
    await callback.message.edit_text(hbold("Настройте вашу заявку:"), reply_markup=create_bid_menu)

@router.callback_query(F.data == "get_amount_form")
async def get_amount_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidCreating.payment_amount)
    await callback.message.edit_text(hbold("Введите требуемую сумму:"), reply_markup=main_menu)

@router.message(BidCreating.payment_amount)
async def set_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.html_text)
        await state.update_data(amount=amount)
        await message.answer(hbold("Успешно!"))
        await message.answer(hbold("Настройте вашу заявку:"), reply_markup=create_bid_menu)
    except:
        await message.answer(bid_amount_err, 
                                reply_markup=main_menu)
        
