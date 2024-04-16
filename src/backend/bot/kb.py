from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)

# Buttons
bid_menu_button = InlineKeyboardButton(text="📝 Меню создания заявки", callback_data="get_bid_menu")

main_menu_button = InlineKeyboardButton(text="🚪 Главное меню", callback_data="get_menu")

# Keyboards
bid_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📝 Создать заявку", callback_data="create_bid")],
    [InlineKeyboardButton(text="🧭 Ожидающие заявки", callback_data="get_pending_bid")],
    [InlineKeyboardButton(text="🕰 История заявок", callback_data="get_history_bid")],
    [main_menu_button],
])

create_bid_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💰 Сумма", callback_data="get_amount_form"),
    InlineKeyboardButton(text="💵 Тип оплаты", callback_data="set_paymant_type")],
    # TODO: Sets remaining payment button
    #[InlineKeyboardButton(text="🕰 История заявок", callback_data="get_history_bid")],

    [bid_menu_button],
])

payment_type_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💵 Наличная", callback_data="cash"),
    InlineKeyboardButton(text="💳 Безналичная", callback_data="card")],
    [InlineKeyboardButton(text="🚕 Требуется такси", callback_data="taxi")],
    [bid_menu_button]
])

def create_inline_keyboard(*buttons):
    return InlineKeyboardMarkup(inline_keyboard=[
        [button for button in buttons]
    ])
