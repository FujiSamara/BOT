from typing import Any, Awaitable, Callable
from functools import cache
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    ContentType,
    Document,
    PhotoSize,
    File,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup
from aiogram.utils.markdown import hbold
from fastapi import UploadFile
from db.models import FujiScope
from db.schemas import WorkerSchema
import db.service as service
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
    worker_tech_req_menu_button,
    repairman_tech_req_button,
    chief_technician_tech_req_button,
    territorial_manager_tech_req_button,
)
import asyncio


@cache
def get_scope_menu_dict() -> dict[FujiScope, InlineKeyboardMarkup]:
    """Returns cached scope-menu dict"""
    return {
        FujiScope.bot_bid_kru: kru_menu_button,
        FujiScope.bot_bid_owner: owner_menu_button,
        FujiScope.bot_bid_accountant_card: accountant_card_menu_button,
        FujiScope.bot_bid_accountant_cash: accountant_cash_menu_button,
        FujiScope.bot_bid_teller_card: teller_card_menu_button,
        FujiScope.bot_bid_teller_cash: teller_cash_menu_button,
        FujiScope.bot_rate: rating_menu_button,
        FujiScope.bot_worker_bid: worker_bid_menu_button,
        FujiScope.bot_bid_create: create_bid_menu_button,
        FujiScope.bot_technical_request_worker: worker_tech_req_menu_button,
        FujiScope.bot_technical_request_repairman: repairman_tech_req_button,
        FujiScope.bot_technical_request_chief_technician: chief_technician_tech_req_button,
        FujiScope.bot_technical_request_territorial_manager: territorial_manager_tech_req_button,
    }


async def send_menu_by_scopes(message: Message, edit=None):
    """
    Sends specific menu for user by his role.

    If `edit = True` - calling `Message.edit_text` instead `Message.answer`
    """
    scopes = []
    worker = service.get_worker_by_telegram_id(message.chat.id)
    if worker:
        scopes = worker.post.scopes

    menus = []

    for scope, button in get_scope_menu_dict().items():
        if scope in scopes or FujiScope.admin in scopes:
            menus.append([button])

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


async def notify_workers_by_scope(scope: FujiScope, message: str) -> None:
    """
    Sends notify `message` to workers by their `scope`.
    """
    workers: list[WorkerSchema] = [
        *service.get_workers_by_scope(scope),
        *service.get_workers_by_scope(FujiScope.admin),
    ]

    for worker in workers:
        if not worker.telegram_id:
            continue
        msg = await notify_worker_by_telegram_id(id=worker.telegram_id, message=message)
        await send_menu_by_scopes(message=msg)


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


async def download_file(file: Document | PhotoSize) -> UploadFile:
    """Download the file (photo or document)"""
    raw_file: File = await get_bot().get_file(file.file_id)
    byte_file = await get_bot().download_file(raw_file.file_path)
    return UploadFile(file=byte_file, filename=raw_file.file_path.split("/")[-1])
