from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from aiogram.fsm.context import FSMContext

# Buttons
create_bid_menu_button = InlineKeyboardButton(text="Меню настройки заявки", callback_data="get_bid_create_menu")

bid_menu_button = InlineKeyboardButton(text="Меню создания заявок", callback_data="get_bid_menu")

main_menu_button = InlineKeyboardButton(text="Главное меню", callback_data="get_menu")

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
    [InlineKeyboardButton(text="Создать заявку", callback_data="get_bid_create_menu")],
    [InlineKeyboardButton(text="Ожидающие заявки", callback_data="get_pending_bid")],
    [InlineKeyboardButton(text="История заявок", callback_data="get_history_bid")],
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

    if not amount:
        amount = "0"
    else:
        amount += " ✅"
    if not payment_type:
        payment_type = "Не указано"
    else:
        payment_type = payment_type_dict[payment_type] + " ✅"
    if not department:
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
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сумма", callback_data="get_amount_form"),
         InlineKeyboardButton(text=amount, callback_data="dummy")],

        [InlineKeyboardButton(text="Тип оплаты", callback_data="get_paymant_form"),
         InlineKeyboardButton(text=payment_type, callback_data="dummy")],

        [InlineKeyboardButton(text="Предприятие", callback_data="get_department_form"),
         InlineKeyboardButton(text=department, callback_data="dummy")],

        [InlineKeyboardButton(text="Наличие договора", callback_data="get_agreement_form"),
         InlineKeyboardButton(text=agreement, callback_data="dummy")],

        [InlineKeyboardButton(text="Заявка срочная?", callback_data="get_urgently_form"),
         InlineKeyboardButton(text=urgently, callback_data="dummy")],

        [InlineKeyboardButton(text="Нужна платежка?", callback_data="get_need_document_form"),
         InlineKeyboardButton(text=need_document, callback_data="dummy")],

        [InlineKeyboardButton(text="Цель платежа" + purpose_postfix, callback_data="get_purpose_form")],
        # TODO: Sets remaining payment button
        #[InlineKeyboardButton(text="История заявок", callback_data="get_history_bid")],
        [InlineKeyboardButton(text="Комментарий", callback_data="get_comment_form")],
        [bid_menu_button],
    ])

payment_type_dict = {
    "cash": "Наличная",
    "card": "Безналичная",
    "taxi": "Требуется такси"
}

payment_type_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=payment_type_dict["cash"], callback_data="cash"),
    InlineKeyboardButton(text=payment_type_dict["card"], callback_data="card")],
    [InlineKeyboardButton(text=payment_type_dict["taxi"], callback_data="taxi")],
    [create_bid_menu_button]
])




