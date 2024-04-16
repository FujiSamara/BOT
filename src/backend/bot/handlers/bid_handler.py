from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
import asyncio

# bot imports
from bot.kb import (
    bid_menu,
    get_create_bid_menu,
    payment_type_menu,
    create_bid_menu_button,
    create_inline_keyboard,
    create_reply_keyboard,
    ReplyKeyboardRemove
)

from bot.text import bid_err, payment_types, bid_create_greet

from bot.states import BidCreating, Base

# db imports
from db.service import get_departments_names

router = Router(name="bid")

### Main section
async def clear_state_with_success(message: Message, state: FSMContext, sleep_time=1, edit=False):
    ans = await message.answer(hbold("Успешно!"), reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(sleep_time)
    await ans.delete()
    await state.set_state(Base.none)
    if edit:
        await message.edit_text(hbold(bid_create_greet),
                                reply_markup=await get_create_bid_menu(state))
    else:
        await message.answer(hbold(bid_create_greet),
                             reply_markup=await get_create_bid_menu(state))

@router.callback_query(F.data == "get_bid_menu")
async def get_menu(callback: CallbackQuery, state: FSMContext):
    await state.update_data(
        amount=None, 
        type=None,
        department=None,
        agreement=None
    )
    await callback.message.edit_text(hbold("Добро пожаловать!"), reply_markup=bid_menu)

## Create bid section
@router.callback_query(F.data == "get_bid_create_menu")
async def get_create_menu(callback: CallbackQuery, state: FSMContext):
    await clear_state_with_success(callback.message, state, sleep_time=0, edit=True)



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
        await state.update_data(amount=str(amount))
        await clear_state_with_success(message, state)
    except:
        await message.answer(bid_err, 
                                reply_markup=create_inline_keyboard(create_bid_menu_button))
        
# Payment type section
@router.callback_query(F.data == "get_paymant_form")
async def get_amount_type_form(callback: CallbackQuery):
    await callback.message.edit_text(hbold("Выберите тип оплаты:"), reply_markup=payment_type_menu)

@router.callback_query(F.data.in_(payment_types))
async def set_amount_type(callback: CallbackQuery, state: FSMContext):
    if callback.data in payment_types:
        await state.update_data(type=callback.data)
        await clear_state_with_success(callback.message, state, edit=True)
    
# Department section
@router.callback_query(F.data == "get_department_form")
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
    elif message.text in dep:
        await state.update_data(department=message.text)
        await clear_state_with_success(message, state)
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

# Agreement existence 
@router.callback_query(F.data == "get_agreement_form")
async def get_agreement_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidCreating.comment)
    await callback.message.edit_text(hbold("У вас есть договор?"),
                                     reply_markup=create_reply_keyboard("Да", "Нет"))

@router.callback_query(F.data.in_(payment_types))
async def set_agreement(callback: CallbackQuery, state: FSMContext):
    if callback.data in payment_types:
        await state.update_data(agreement=callback.data)
        await clear_state_with_success(callback.message, state, edit=True)

# Comment
@router.callback_query(F.data == "get_comment_form")
async def get_comment_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidCreating.comment)
    await callback.message.edit_text(hbold("Введите комментарий:"))

@router.message(BidCreating.comment)
async def set_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.html_text)
    await clear_state_with_success(message, state)
