from typing import Any
from aiogram.types import Message


async def try_delete_message(message: Message) -> bool:
    '''
    Tries to delete message, return `True`
    if the `message` successfully deleted, `False` otherwise.
    '''
    try:
        await message.delete()
        return True
    except Exception:
        return False


async def try_edit_message(
        message: Message,
        text: str,
        reply_markup: Any = None
) -> None:
    '''
    Tries to edit message.
    if the `message` unsuccessfully edited
    then answers message.
    '''
    try:
        await message.edit_text(text=text, reply_markup=reply_markup)
    except Exception:
        return
