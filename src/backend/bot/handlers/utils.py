from typing import Any
from aiogram.types import Message, InlineKeyboardMarkup
from aiogram.utils.markdown import hbold
from db.models import Access
from db.schemas import WorkerSchema
from db.service import get_workers_by_level, get_user_level_by_telegram_id
from bot.bot import get_bot
from bot.kb import (
    create_bid_menu_button,
    teller_card_menu_button,
    teller_cash_menu_button,
    accountant_card_menu_button,
    accountant_cash_menu_button,
    owner_menu_button,
    kru_menu_button,
    rating_menu_button,
)


async def send_menu_by_level(message: Message, edit=None):
    """
    Sends specific menu for user by his role.

    If `edit = True` - calling `Message.edit_text` instead `Message.answer`
    """
    level = get_user_level_by_telegram_id(message.chat.id)
    menus = []

    match get_access_by_level(level):
        case Access.worker:
            menus.append([create_bid_menu_button])
        case Access.teller_cash:
            menus.append([teller_cash_menu_button])
        case Access.teller_card:
            menus.append([teller_card_menu_button])
        case Access.kru:
            menus.append([kru_menu_button])
            menus.append([rating_menu_button])
        case Access.accountant_cash:
            menus.append([accountant_cash_menu_button])
        case Access.accountant_card:
            menus.append([accountant_card_menu_button])
        case Access.owner:
            menus.append([owner_menu_button])

    menu = InlineKeyboardMarkup(inline_keyboard=menus)

    if edit:
        await try_edit_or_answer(
            message=message,
            text=hbold("Выберите дальнейшее действие:"),
            reply_markup=menu,
        )
    else:
        await message.answer(hbold("Выберите дальнейшее действие:"), reply_markup=menu)


def get_access_by_level(level: int) -> Access:
    """
    Returns relevant worker post by `level`.
    """
    if level >= 2 and level <= 3:
        return Access.worker

    if level == 4:
        return Access.teller_cash

    if level == 5:
        return Access.teller_card

    if level == 6:
        return Access.kru

    if level == 7:
        return Access.accountant_cash

    if level == 8:
        return Access.accountant_card

    if level == 10:
        return Access.owner


async def try_delete_message(message: Message) -> bool:
    """
    Tries to delete message, return `True`
    if the `message` successfully deleted, `False` otherwise.
    """
    try:
        await message.delete()
        return True
    except Exception:
        return False


async def try_edit_message(
    message: Message, text: str, reply_markup: Any = None
) -> bool:
    """
    Tries to edit message. Return `True`
    if the `message` successfully edited, `False` otherwise.
    """
    try:
        await message.edit_text(text=text, reply_markup=reply_markup)
        return True
    except Exception:
        return False


async def try_edit_or_answer(message: Message, text: str, reply_markup: Any = None):
    """
    Tries to edit message.
    if the `message` unsuccessfully edited
    then answers message by `Message.answer_text`.

    Returns: `True` if message edited, `False` otherwise.
    """
    if not await try_edit_message(
        message=message, text=text, reply_markup=reply_markup
    ):
        await message.answer(text=text, reply_markup=reply_markup)
        return False

    return True


async def notify_workers_by_level(level: int, message: str) -> None:
    """
    Sends notify `message` to workers by their `level`.
    """
    workers: list[WorkerSchema] = get_workers_by_level(level)

    for worker in workers:
        if not worker.telegram_id:
            continue
        msg = await get_bot().send_message(chat_id=worker.telegram_id, text=message)
        await send_menu_by_level(message=msg)
