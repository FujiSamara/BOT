from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

# bot imports
from bot.kb import (
    bid_menu,
    create_bid_menu,
    payment_type_menu,
    bid_menu_button,
    create_inline_keyboard
)

from bot.text import bid_err, payment_types

from bot.states import BidCreating

# db imports


router = Router(name="bid")

@router.callback_query(F.data == "get_bid_menu")
async def get_menu(callback: CallbackQuery):
    await callback.message.edit_text(hbold("Добро пожаловать!"), reply_markup=bid_menu)

# Create bid section
@router.callback_query(F.data == "create_bid")
async def get_create_menu(callback: CallbackQuery):
    await callback.message.edit_text(hbold("Настройте вашу заявку:"), reply_markup=create_bid_menu)

# Amount section
@router.callback_query(F.data == "get_amount_form")
async def get_amount_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidCreating.payment_amount)
    await callback.message.edit_text(hbold("Введите требуемую сумму:"),
                                     reply_markup=create_inline_keyboard(bid_menu_button))

@router.message(BidCreating.payment_amount)
async def set_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.html_text)
        await state.update_data(amount=amount)
        await message.answer(hbold("Успешно! Настройте вашу заявку:"), reply_markup=create_bid_menu)
    except:
        await message.answer(bid_err, 
                                reply_markup=create_inline_keyboard(bid_menu_button))
        
# Payment type section
@router.callback_query(F.data == "set_paymant_type")
async def get_amoun_form(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(hbold("Выберите тип оплаты:"), reply_markup=payment_type_menu)

@router.callback_query(F.data.in_(payment_types))
async def set_type(callback: CallbackQuery, state: FSMContext):
    if callback.data in payment_types:
        await state.update_data(type=callback.data)
        await callback.message.edit_text(hbold("Успешно! Настройте вашу заявку:"), reply_markup=create_bid_menu)
