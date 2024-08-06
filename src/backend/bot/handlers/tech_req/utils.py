from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from bot.handlers.tech_req.schemas import (
    ShowRequestCallbackData,
)
from db.schemas import (
    TechnicalRequestSchema,
)
from settings import get_settings


def create_keybord_with_end_point(
    requests: list[TechnicalRequestSchema],
    end_point: str,
    menu_button: InlineKeyboardButton,
) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []
    try:
        for request in requests:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=request.open_date.date().strftime(
                            get_settings().date_format
                        ),
                        callback_data=ShowRequestCallbackData(
                            request_id=request.id, end_point=end_point
                        ).pack(),
                    )
                ]
            )
    finally:
        buttons.append([menu_button])
        return InlineKeyboardMarkup(inline_keyboard=buttons)
