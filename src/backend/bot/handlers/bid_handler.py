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
from db.service import get_departments_names, create_bid

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
    await state.set_state(Base.none)
    await callback.message.edit_text(hbold("Добро пожаловать!"), reply_markup=bid_menu)

## Create bid section
@router.callback_query(F.data == "get_bid_create_menu")
async def get_create_menu(callback: CallbackQuery, state: FSMContext):
    await clear_state_with_success(callback.message, state, sleep_time=0, edit=True)

@router.callback_query(F.data == "send_bid")
async def send_bid(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.set_state(Base.none)
    amount = data.get("amount")
    payment_type = data.get("type")
    department = data.get("department")
    purpose = data.get("purpose")
    agreement = data.get("agreement")
    urgently = data.get("urgently")
    need_document = data.get("need_document")
    comment = data.get("comment")

    create_bid(
        amount=amount,
        payment_type=payment_type,
        department=department,
        purpose=purpose,
        agreement=agreement,
        urgently=urgently,
        need_document=need_document,
        comment=comment,
        telegram_id=callback.message.chat.id
    )

    await callback.message.edit_text("Успешно!")
    await asyncio.sleep(1)
    await callback.message.edit_text(hbold("Добро пожаловать!"), reply_markup=bid_menu)


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
    await state.set_state(BidCreating.agreement_existence)
    await callback.message.delete()
    await callback.message.answer(hbold("У вас есть договор?"),
                                     reply_markup=create_reply_keyboard("Да", "Нет"))

@router.message(BidCreating.agreement_existence)
async def set_agreement(message: Message, state: FSMContext):
    if message.text == "⏪ Назад":
        await clear_state_with_success(message, state, sleep_time=0)
    elif message.text in ["Да", "Нет"]:
        await state.update_data(agreement=message.text)
        await clear_state_with_success(message, state)
    else:
        await message.answer(bid_err)

# Comment
@router.callback_query(F.data == "get_comment_form")
async def get_comment_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidCreating.comment)
    await callback.message.edit_text(hbold("Введите комментарий:"))

@router.message(BidCreating.comment)
async def set_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.html_text)
    await clear_state_with_success(message, state)

# Urgently
@router.callback_query(F.data == "get_urgently_form")
async def get_urgently_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidCreating.urgently)
    await callback.message.delete()
    await callback.message.answer(hbold("Заявка срочная?"),
                                     reply_markup=create_reply_keyboard("Да", "Нет"))

@router.message(BidCreating.urgently)
async def set_agreement(message: Message, state: FSMContext):
    if message.text == "⏪ Назад":
        await clear_state_with_success(message, state, sleep_time=0)
    elif message.text in ["Да", "Нет"]:
        await state.update_data(urgently=message.text)
        await clear_state_with_success(message, state)
    else:
        await message.answer(bid_err)

# Need for a payment system
@router.callback_query(F.data == "get_need_document_form")
async def get_need_document_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidCreating.need_document)
    await callback.message.delete()
    await callback.message.answer(hbold("Нужна платежка?"),
                                     reply_markup=create_reply_keyboard("Да", "Нет"))

@router.message(BidCreating.need_document)
async def set_need_document(message: Message, state: FSMContext):
    if message.text == "⏪ Назад":
        await clear_state_with_success(message, state, sleep_time=0)
    elif message.text in ["Да", "Нет"]:
        await state.update_data(need_document=message.text)
        await clear_state_with_success(message, state)
    else:
        await message.answer(bid_err)