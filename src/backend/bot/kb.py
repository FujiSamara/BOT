from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)

exit_bid_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🚪 Главное меню", callback_data="get_bid_menu")]
])

bid_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📝 Создать заявку", callback_data="create_bid")],
    [InlineKeyboardButton(text="🧭 Ожидающие заявки", callback_data="get_pending_bid")],
    [InlineKeyboardButton(text="🕰 История заявок", callback_data="get_history_bid")],
    [InlineKeyboardButton(text="🚪 Главное меню", callback_data="get_bid_menu")],
])

create_bid_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💰 Сумма", callback_data="get_amount_form"),
    InlineKeyboardButton(text="💵 Тип оплаты", callback_data="set_paymant_type")],
    # TODO: Sets remaining payment button
    #[InlineKeyboardButton(text="🕰 История заявок", callback_data="get_history_bid")],

    [InlineKeyboardButton(text="🚪 Главное меню", callback_data="get_bid_menu")],
])
