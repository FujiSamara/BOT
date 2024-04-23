from io import BytesIO
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, Document, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
import asyncio

# bot imports
from bot.bot import get_bot
from bot.kb import (
    bid_menu,
    get_create_bid_menu,
    payment_type_menu,
    settings_bid_menu_button,
    create_bid_menu_button,
    create_inline_keyboard,
    create_reply_keyboard,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    payment_type_dict,
    bid_create_history_button,
    bid_create_pending_button
)

from bot.text import bid_err, payment_types, bid_create_greet

from bot.states import BidCreating, Base
from bot.handlers.bids.model import BidCallbackData, BidViewMode, BidViewType

# db imports
from db.service import (
    get_departments_names,
    create_bid,
    get_bids_by_worker_telegram_id,
    get_bid_by_id,
    get_pending_bids_by_worker_telegram_id
)
from db.models import ApprovalState
from db.schemas import BidShema


router = Router(name="bid_creating")



async def clear_state_with_success(
        message: Message,
        state: FSMContext,
        sleep_time=1,
        edit=False
    ):
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


## Create section
@router.callback_query(F.data == "get_bid_settings_menu")
async def get_settings_form(callback: CallbackQuery, state: FSMContext):
    await clear_state_with_success(
        callback.message,
        state,
        sleep_time=0,
        edit=True
    )

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
    document: Document = data.get("document")
    file = await get_bot().get_file(document.file_id)
    file: BytesIO = await get_bot().download_file(file.file_path)

    kru_state = ApprovalState.pending_approval
    owner_state = ApprovalState.pending
    if int(amount) < 10000:
        owner_state = ApprovalState.skipped
    accountant_card_state = ApprovalState.pending
    accountant_cash_state = ApprovalState.pending
    teller_card_state = ApprovalState.pending
    teller_cash_state = ApprovalState.pending

    if payment_type == "card":
        accountant_cash_state = ApprovalState.skipped
        teller_cash_state = ApprovalState.skipped
    else:
        accountant_card_state = ApprovalState.skipped
        teller_card_state = ApprovalState.skipped

    create_bid(
        amount=amount,
        payment_type=payment_type,
        department=department,
        file=file,
        filename=document.file_name,
        purpose=purpose,
        agreement=agreement,
        urgently=urgently,
        need_document=need_document,
        comment=comment,
        telegram_id=callback.message.chat.id,
        kru_state=kru_state,
        owner_state=owner_state,
        accountant_card_state=accountant_card_state,
        accountant_cash_state=accountant_cash_state,
        teller_card_state=teller_card_state,
        teller_cash_state=teller_cash_state
    )

    await callback.message.edit_text("Успешно!")
    await asyncio.sleep(1)
    await callback.message.edit_text(hbold("Добро пожаловать!"), reply_markup=bid_menu)
    await state.clear()


# Amount section
@router.callback_query(F.data == "get_amount_form")
async def get_amount_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidCreating.payment_amount)
    await callback.message.edit_text(hbold("Введите требуемую сумму:"),
                                     reply_markup=create_inline_keyboard(settings_bid_menu_button))

@router.message(BidCreating.payment_amount)
async def set_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.html_text)
        await state.update_data(amount=str(amount))
        await clear_state_with_success(message, state)
    except:
        await message.answer(bid_err, 
                                reply_markup=create_inline_keyboard(settings_bid_menu_button))
        
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
async def get_department_form(callback: CallbackQuery, state: FSMContext):
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

# Document
@router.callback_query(F.data == "get_document_form")
async def get_bids_pending(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidCreating.document)
    await callback.message.delete()
    await callback.message.answer(hbold("Прикрепите документ:"),
                                     reply_markup=create_inline_keyboard(settings_bid_menu_button))
    
@router.message(BidCreating.document)
async def set_need_document(message: Message, state: FSMContext):
    if message.document:
        await state.update_data(document=message.document)
        await clear_state_with_success(message, state)
    else:
        await message.answer(bid_err,
                                     reply_markup=create_inline_keyboard(settings_bid_menu_button))

## History section


def get_full_bid_info(bid: BidShema) -> str:
    stage = ""

    if bid.kru_state == ApprovalState.pending_approval:
        stage = "КРУ"
    elif bid.owner_state == ApprovalState.pending_approval:
        stage = "Собственник"
    elif bid.accountant_card_state ==  ApprovalState.pending_approval:
        stage = "Бухгалтер безнал."
    elif bid.accountant_cash_state ==  ApprovalState.pending_approval:
        stage = "Бухгалтер нал."
    elif bid.teller_card_state ==  ApprovalState.pending_approval:
        stage = "Кассир безнал."
    elif bid.teller_cash_state ==  ApprovalState.pending_approval:
        stage = "Кассир нал."
    elif (
        bid.kru_state == ApprovalState.denied or
        bid.owner_state == ApprovalState.denied or
        bid.accountant_card_state == ApprovalState.denied or
        bid.accountant_cash_state == ApprovalState.denied or
        bid.teller_card_state == ApprovalState.denied or
        bid.teller_cash_state == ApprovalState.denied
    ):
        stage = "Отказано"
    else:
        stage = "Выплачено"

    bid_info = f"""Сумма: {bid.amount}
Тип оплаты: {payment_type_dict[bid.payment_type]}
Предприятие: {bid.department.name}
Документ: Прикреплен к сообщению.
Цель платежа: {bid.purpose}
Наличие договора: {bid.agreement}
Заявка срочная? {bid.urgently}
Нужна платежка? {bid.need_document}
Комментарий: {bid.comment}
Текущий этап: {stage}
"""
   

    return bid_info

def get_state_bid_info(bid: BidShema) -> str:
    stage = ""
    if bid.kru_state == ApprovalState.pending_approval:
        stage = "КРУ"
    elif bid.owner_state == ApprovalState.pending_approval:
        stage = "Собственник"
    elif bid.accountant_card_state ==  ApprovalState.pending_approval:
        stage = "Бухгалтер безнал."
    elif bid.accountant_cash_state ==  ApprovalState.pending_approval:
        stage = "Бухгалтер нал."
    elif bid.teller_card_state ==  ApprovalState.pending_approval:
        stage = "Кассир безнал."
    elif bid.teller_cash_state ==  ApprovalState.pending_approval:
        stage = "Кассир нал."
    
    return f"""Заявка от {bid.create_date.date()} на сумму: {bid.amount}.
Статус: на согласовании у {stage}"""


# Full info
@router.callback_query(
    BidCallbackData.filter(F.type == BidViewType.creation),
    BidCallbackData.filter(F.mode == BidViewMode.full)
)
async def get_bid(callback: CallbackQuery, callback_data: BidCallbackData):
    bid_id = callback_data.id
    bid = get_bid_by_id(bid_id)
    await callback.message.delete()
    document = BufferedInputFile(file=bid.document.file.read(), filename=bid.document.filename)

    caption = get_full_bid_info(bid)

    await callback.message.answer_document(
        document=document,
        caption=caption,
        reply_markup=create_inline_keyboard(bid_create_history_button)
    )

@router.callback_query(F.data == "get_create_history_bid")
async def get_bids_history(callback: CallbackQuery):
    bids = get_bids_by_worker_telegram_id(callback.message.chat.id)
    bids = sorted(bids, key=lambda bid: bid.create_date, reverse=True)[:10]
    keyboard = create_inline_keyboard(
        *(InlineKeyboardButton(
            text=f"Заявка от {bid.create_date.date()} на cумму {bid.amount}",
            callback_data=BidCallbackData(
                id=bid.id,
                mode=BidViewMode.full,
                type=BidViewType.creation
            ).pack()
        ) for bid in bids),
        create_bid_menu_button
    )
    await callback.message.delete()
    await callback.message.answer("История заявок:", reply_markup=keyboard)

# Base info with state
@router.callback_query(
    BidCallbackData.filter(F.type == BidViewType.creation),
    BidCallbackData.filter(F.mode == BidViewMode.state_only)
)
async def get_bid_state(callback: CallbackQuery, callback_data: BidCallbackData):
    bid_id = callback_data.id
    bid = get_bid_by_id(bid_id)
    await callback.message.delete()

    text = get_state_bid_info(bid)

    await callback.message.answer(
        text=text,
        reply_markup=create_inline_keyboard(bid_create_pending_button)
    )

@router.callback_query(F.data == "get_create_pending_bid")
async def get_bids_pending(callback: CallbackQuery):
    bids = get_pending_bids_by_worker_telegram_id(callback.message.chat.id)
    bids = sorted(bids, key=lambda bid: bid.create_date, reverse=True)[:10]
    keyboard = create_inline_keyboard(
        *(InlineKeyboardButton(
            text=f"Заявка от {bid.create_date.date()} на cумму {bid.amount}",
            callback_data=BidCallbackData(
                id=bid.id,
                mode=BidViewMode.state_only,
                type=BidViewType.creation
            ).pack()
        ) for bid in bids),
        create_bid_menu_button
    )
    await callback.message.delete()
    await callback.message.answer("Ожидающие заявки:", reply_markup=keyboard)