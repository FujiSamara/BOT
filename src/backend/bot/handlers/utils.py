from typing import Any, Awaitable, Callable
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    ContentType,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup
from aiogram.utils.markdown import hbold
from db.models import Access
from db.schemas import WorkerSchema
from db.service import get_workers_by_level, get_worker_level_by_telegram_id
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
    worker_bid_menu_button,
    create_reply_keyboard,
)
import asyncio


async def send_menu_by_level(message: Message, edit=None):
    """
    Sends specific menu for user by his role.

    If `edit = True` - calling `Message.edit_text` instead `Message.answer`
    """
    level = get_worker_level_by_telegram_id(message.chat.id)
    menus = []

    match get_access_by_level(level):
        case Access.worker:
            menus.append([create_bid_menu_button])
            menus.append([worker_bid_menu_button])
            if level == 6:
                menus.append([rating_menu_button])
        case Access.teller_cash:
            menus.append([teller_cash_menu_button])
        case Access.teller_card:
            menus.append([teller_card_menu_button])
        case Access.kru:
            menus.append([kru_menu_button])
        case Access.accountant_cash:
            menus.append([accountant_cash_menu_button])
        case Access.accountant_card:
            menus.append([accountant_card_menu_button])
        case Access.owner:
            menus.append([owner_menu_button])

    menu = InlineKeyboardMarkup(inline_keyboard=menus)

    msg = await message.answer("Загрузка...", reply_markup=ReplyKeyboardRemove())
    await try_delete_message(msg)

    if edit:
        await try_edit_or_answer(
            message=message,
            text=hbold("Фуджи team"),
            reply_markup=menu,
        )
    else:
        await message.answer(hbold("Фуджи team"), reply_markup=menu)


def get_access_by_level(level: int) -> Access:
    """
    Returns relevant worker post by `level`.
    """

    if level == 7:
        return Access.teller_cash

    if level == 8:
        return Access.teller_card

    if level == 16:
        return Access.kru

    if level == 17:
        return Access.accountant_cash

    if level == 18:
        return Access.accountant_card

    if level == 25:
        return Access.owner

    if level >= 5:
        return Access.worker


def get_levels_by_access(access: Access) -> list[int]:
    """Returns level by access."""
    match access:
        case Access.worker:
            return [5, 6]
        case Access.kru:
            return [16]
        case Access.teller_cash:
            return [7]
        case Access.teller_card:
            return [8]
        case Access.kru:
            return [16]
        case Access.accountant_card:
            return [18]
        case Access.accountant_cash:
            return [17]
        case Access.owner:
            return [25]
        case _:
            return []


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
        msg = await notify_worker_by_telegram_id(id=worker.telegram_id, message=message)
        await send_menu_by_level(message=msg)


async def notify_workers_by_access(access: Access, message: str) -> None:
    """
    Sends notify `message` to workers by their `access`.
    """
    for level in get_levels_by_access(access):
        await notify_workers_by_level(level, message)


async def notify_worker_by_telegram_id(id: int, message: str) -> Message:
    """
    Sends notify `message` to worker by their `id`.

    Returns sended `Message`.
    """
    return await get_bot().send_message(chat_id=id, text=message)


async def handle_documents(
    message: Message,
    state: FSMContext,
    document_name: str,
    on_complete: Callable[[Any, Any], Awaitable[Any]],
):
    if message.content_type == ContentType.TEXT:
        if message.text == "Готово":
            data = await state.get_data()
            msgs = data.get("msgs")
            documents = data.get("documents")
            if msgs:
                for msg in msgs:
                    await try_delete_message(msg)
                await state.update_data(msgs=[])
            if documents:
                specified_documents = data.get(document_name)
                if not specified_documents:
                    specified_documents = []
                specified_documents.extend(documents)
                await state.update_data(documents=[])
                await state.update_data({document_name: specified_documents})
            msg = data.get("msg")
            if msg:
                await try_delete_message(msg)
            await try_delete_message(message)
            await on_complete(message, state)
        elif message.text == "Сбросить":
            data = await state.get_data()
            msgs = data.get("msgs")
            documents = data.get("documents")
            if msgs:
                for msg in msgs:
                    await try_delete_message(msg)
                await state.update_data(msgs=[])
            await state.update_data(documents=[])
            await state.update_data({document_name: []})
            msg = data.get("msg")
            if msg:
                await try_delete_message(msg)
            await try_delete_message(message)
            await on_complete(message, state)
        else:
            await try_delete_message(message)
            msg = await message.answer("Отправьте документ или фото!")
            await asyncio.sleep(1)
            await try_delete_message(msg)
    elif (
        message.content_type == ContentType.DOCUMENT
        or message.content_type == ContentType.PHOTO
    ):
        data = await state.get_data()
        documents: list = data.get("documents")
        msgs: list = data.get("msgs")
        if not documents:
            documents = []
        if message.content_type == ContentType.PHOTO:
            documents.append(message.photo[-1])
        else:
            documents.append(message.document)
        if not msgs:
            msgs = []
        msgs.append(message)
        await state.update_data(msgs=msgs, documents=documents)
    else:
        await try_delete_message(message)
        msg = await message.answer("Отправьте документ или фото!")
        await asyncio.sleep(1)
        await try_delete_message(msg)


async def handle_documents_form(
    message: Message, state: FSMContext, document_type: StatesGroup
):
    await state.set_state(document_type)
    await try_delete_message(message)
    msg = await message.answer(
        text=hbold("Прикрепите документы:"),
        reply_markup=create_reply_keyboard("Готово", "Сбросить"),
    )
    await state.update_data(msg=msg)


async def handle_save_documents(
    message: Message, state: FSMContext, document_name: str
):
    pass
