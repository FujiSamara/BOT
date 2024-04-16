from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
import asyncio

# bot imports
from bot.kb import (
    bid_menu,
    create_bid_menu,
    payment_type_menu,
    create_bid_menu_button,
    create_inline_keyboard,
    create_reply_keyboard,
    ReplyKeyboardRemove
)

from bot.text import bid_err, payment_types

from bot.states import BidCreating, Base

# db imports
from db.service import get_departments_names

router = Router(name="bid")

### Main section
async def clear_state_with_success(message: Message, state: FSMContext, sleep_time=1):
    ans = await message.answer(hbold("Успешно!"), reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(sleep_time)
    await ans.delete()
    await state.set_state(Base.none)

@router.callback_query(F.data == "get_bid_menu")
async def get_menu(callback: CallbackQuery):
    await callback.message.edit_text(hbold("Добро пожаловать!"), reply_markup=bid_menu)

## Create bid section
@router.callback_query(F.data == "create_bid")
async def get_create_menu(callback: CallbackQuery, state: FSMContext):
    await clear_state_with_success(callback.message, state, sleep_time=0)
    await callback.message.edit_text(hbold("Настройте вашу заявку:"), reply_markup=create_bid_menu)



# Amount section
@router.callback_query(F.data == "get_amount_form")
async def get_amount_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidCreating.payment_amount)
    await callback.message.edit_text(hbold("Введите требуемую сумму:"),
                                     reply_markup=create_inline_keyboard(create_bid_menu_button))

@router.message(BidCreating.payment_amount)
async def set_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.html_text)
        await state.update_data(amount=amount)
        await clear_state_with_success(message, state)
        await message.answer(hbold("Настройте вашу заявку:"), reply_markup=create_bid_menu)
    except:
        await message.answer(bid_err, 
                                reply_markup=create_inline_keyboard(create_bid_menu_button))
        
# Payment type section
@router.callback_query(F.data == "get_paymant_from")
async def get_amount_type_form(callback: CallbackQuery):
    await callback.message.edit_text(hbold("Выберите тип оплаты:"), reply_markup=payment_type_menu)

@router.callback_query(F.data.in_(payment_types))
async def set_amount_type(callback: CallbackQuery, state: FSMContext):
    if callback.data in payment_types:
        await state.update_data(type=callback.data)
        await clear_state_with_success(callback.message, state)
        await callback.message.edit_text(hbold("Настройте вашу заявку:"), reply_markup=create_bid_menu)
    
# Department section
@router.callback_query(F.data == "get_department_from")
async def get_create_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidCreating.department)
    dep = get_departments_names()
    await callback.message.delete()
    await callback.message.answer(hbold("Выберите предприятие:"),
                                     reply_markup=create_reply_keyboard("⏪ Назад", *dep))

@router.message(BidCreating.department)
async def set_department_type(message: Message, state: FSMContext):
    dep = get_departments_names()
    if message.text == "⏪ Назад":
        await clear_state_with_success(message, state, sleep_time=0)
        await message.answer(hbold("Настройте вашу заявку:"), reply_markup=create_bid_menu)
    elif message.text in dep:
        await state.update_data(type=message.text)
        await clear_state_with_success(message, state)
        await message.answer(hbold("Настройте вашу заявку:"), reply_markup=create_bid_menu)
    else:
        await message.answer(bid_err)

# Purpose section
@router.callback_query(F.data == "get_purpose_form")
async def get_purpose_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidCreating.payment_purpose)
    await callback.message.edit_text(hbold("Введите цель платежа:"))

@router.message(BidCreating.payment_purpose)
async def set_purpose(message: Message, state: FSMContext):
    await state.update_data(purpose=message.html_text)
    await clear_state_with_success(message, state)
    await message.answer(hbold("Настройте вашу заявку:"), reply_markup=create_bid_menu)

# Comment
@router.callback_query(F.data == "get_comment_form")
async def get_comment_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidCreating.comment)
    await callback.message.edit_text(hbold("Введите комментарий:"))

@router.message(BidCreating.comment)
async def set_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.html_text)
    await clear_state_with_success(message, state)
    await message.answer(hbold("Настройте вашу заявку:"), reply_markup=create_bid_menu)     
