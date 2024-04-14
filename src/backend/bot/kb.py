from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)


bid_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📝 Создать заявку", callback_data="create_bid"),
    InlineKeyboardButton(text="🧭 Ожидающие заявки", callback_data="get_pending_bid")],
    [InlineKeyboardButton(text="🕰 История заявок", callback_data="get_history_bid")],
    [InlineKeyboardButton(text="🚪 Главное меню", callback_data="get_bid_menu")],
])
