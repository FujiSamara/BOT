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
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [main_menu_button]
])

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

    [main_menu_button],
])
