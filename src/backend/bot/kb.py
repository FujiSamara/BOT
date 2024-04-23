from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from aiogram.fsm.context import FSMContext
from aiogram.types import Document

from db.models import ApprovalState

# Buttons
settings_bid_menu_button = InlineKeyboardButton(text="Меню настройки заявки", callback_data="get_bid_settings_menu")

create_bid_menu_button = InlineKeyboardButton(text="Меню создания заявок", callback_data="get_create_bid_menu")

main_menu_button = InlineKeyboardButton(text="Главное меню", callback_data="get_menu")

bid_create_history_button = InlineKeyboardButton(text="История заявок", callback_data="get_create_history_bid")
bid_create_pending_button = InlineKeyboardButton(text="Ожидающие заявки", callback_data="get_create_pending_bid")
## Keyboards
def create_inline_keyboard(*buttons: list[InlineKeyboardButton]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [button] for button in buttons
    ])

def create_reply_keyboard(*texts: list[str]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=text)] for text in texts
    ])

# Bid
bid_menu = InlineKeyboardMarkup(inline_keyboard=[
    [settings_bid_menu_button],
    [bid_create_pending_button],
    [bid_create_history_button],
    [main_menu_button],
])

async def get_create_bid_menu(state: FSMContext) -> InlineKeyboardMarkup:
    data = await state.get_data()
    amount = data.get("amount")
    payment_type = data.get("type")
    department = data.get("department")
    agreement = data.get("agreement")
    urgently = data.get("urgently")
    need_document = data.get("need_document")
    document: Document = data.get("document")
    document_text = "Отсутствует"

    all_field_exist = True

    if not amount:
        all_field_exist = False
        amount = "0"
    else:
        amount += " ✅"
    if not payment_type:
        all_field_exist = False
        payment_type = "Не указано"
    else:
        payment_type = payment_type_dict[payment_type] + " ✅"
    if not department:
        all_field_exist = False
        department = "Не указано"
    else:
        department += " ✅"
    if not agreement:
        agreement = "Нет ✅"
    else:
        agreement += " ✅"
    if not urgently:
        urgently = "Нет ✅"
    else:
        urgently += " ✅"
    if not need_document:
        need_document = "Нет ✅"
    else:
        need_document += " ✅"

    purpose_postfix = ""
    if "purpose" in data:
        purpose_postfix = " ✅"
    else:
        all_field_exist = False

    if not document:
        all_field_exist = False
    else:
        document_text = document.file_name + " ✅"

    keyboard = [
        [InlineKeyboardButton(text="Сумма", callback_data="get_amount_form"),
         InlineKeyboardButton(text=amount, callback_data="dummy")],

        [InlineKeyboardButton(text="Тип оплаты", callback_data="get_paymant_form"),
         InlineKeyboardButton(text=payment_type, callback_data="dummy")],

        [InlineKeyboardButton(text="Предприятие", callback_data="get_department_form"),
         InlineKeyboardButton(text=department, callback_data="dummy")],

        [InlineKeyboardButton(text="Документ", callback_data="get_document_form"),
         InlineKeyboardButton(text=document_text, callback_data="dummy")],

        [InlineKeyboardButton(text="Наличие договора", callback_data="get_agreement_form"),
         InlineKeyboardButton(text=agreement, callback_data="dummy")],

        [InlineKeyboardButton(text="Заявка срочная?", callback_data="get_urgently_form"),
         InlineKeyboardButton(text=urgently, callback_data="dummy")],

        [InlineKeyboardButton(text="Нужна платежка?", callback_data="get_need_document_form"),
         InlineKeyboardButton(text=need_document, callback_data="dummy")],

        [InlineKeyboardButton(text="Цель платежа" + purpose_postfix, callback_data="get_purpose_form")],
        # TODO: Sets remaining payment button
        [InlineKeyboardButton(text="Комментарий", callback_data="get_comment_form")],
        [create_bid_menu_button],
    ]
    if all_field_exist:
        keyboard.append([InlineKeyboardButton(text="Отправить заявку", 
                                          callback_data="send_bid")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

payment_type_dict = {
    "cash": "Наличная",
    "card": "Безналичная",
    "taxi": "Требуется такси"
}

approval_state_dict = {
    ApprovalState.approved: "Согласовано",
    ApprovalState.pending: "Ожидает поступления",
    ApprovalState.pending_approval: "Ожидает согласования",
    ApprovalState.denied: "Отклонено",
    ApprovalState.skipped: "Пропущено"
}

payment_type_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=payment_type_dict["cash"], callback_data="cash"),
    InlineKeyboardButton(text=payment_type_dict["card"], callback_data="card")],
    [InlineKeyboardButton(text=payment_type_dict["taxi"], callback_data="taxi")],
    [settings_bid_menu_button]
])




