from typing import Any, Awaitable, Callable, Optional
from functools import cache
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    ContentType,
    Document,
    PhotoSize,
    File,
    CallbackQuery,
)
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup
from aiogram.utils.markdown import hbold
from fastapi import UploadFile
from app.infra.database.models import FujiScope
from app.schemas import WorkerSchema
import app.services as services
from app.adapters.bot.bot import get_bot
from app.adapters.bot.kb import (
    fac_cc_menu_button,
    create_bid_menu_button,
    create_bid_it_menu_button,
    teller_card_menu_button,
    teller_cash_menu_button,
    accountant_card_menu_button,
    accountant_cash_menu_button,
    owner_menu_button,
    kru_menu_button,
    rating_menu_button,
    worker_bid_menu_button,
    create_reply_keyboard,
    get_it_repairman_menu_btn,
    get_it_tm_menu_btn,
    get_personal_cabinet_button,
    get_monitoring_menu_btn,
    get_coordinate_worker_bids_SS_btn,
    get_coordinate_worker_bids_AS_btn,
    get_candidates_coordinate_menu_btn,
)
from app.adapters.bot.handlers.department_request.kb import (
    wr_menu_button,  # worker
    repairman_button,
    cleaner_button,
    ct_button,  # chief technician
    AP_TR_button,  # territorial manager tech req
    TM_CR_button,  # territorial manager cleaning req
    dd_button,  # department director
)
import asyncio


@cache
def get_scope_menu_dict() -> dict[FujiScope, InlineKeyboardMarkup]:
    """Returns cached scope-menu dict"""
    return {
        FujiScope.bot_bid_fac_cc: fac_cc_menu_button,
        FujiScope.bot_bid_kru: kru_menu_button,
        FujiScope.bot_bid_owner: owner_menu_button,
        FujiScope.bot_bid_accountant_card: accountant_card_menu_button,
        FujiScope.bot_bid_accountant_cash: accountant_cash_menu_button,
        FujiScope.bot_bid_teller_card: teller_card_menu_button,
        FujiScope.bot_bid_teller_cash: teller_cash_menu_button,
        FujiScope.bot_rate: rating_menu_button,
        FujiScope.bot_worker_bid: worker_bid_menu_button,
        FujiScope.bot_bid_create: create_bid_menu_button,
        FujiScope.bot_technical_request_worker: wr_menu_button,
        FujiScope.bot_technical_request_repairman: repairman_button,
        FujiScope.bot_technical_request_chief_technician: ct_button,
        FujiScope.bot_technical_request_appraiser: AP_TR_button,
        FujiScope.bot_technical_request_department_director: dd_button,
        FujiScope.bot_bid_it_worker: create_bid_it_menu_button,
        FujiScope.bot_bid_it_repairman: get_it_repairman_menu_btn,
        FujiScope.bot_bid_it_tm: get_it_tm_menu_btn,
        FujiScope.bot_personal_cabinet: get_personal_cabinet_button,
        FujiScope.bot_incident_monitoring: get_monitoring_menu_btn,
        FujiScope.bot_subordinates_menu: get_candidates_coordinate_menu_btn,
        FujiScope.bot_worker_bid_security_coordinate: get_coordinate_worker_bids_SS_btn,
        FujiScope.bot_worker_bid_accounting_coordinate: get_coordinate_worker_bids_AS_btn,
        FujiScope.bot_cleaning_request_cleaner: cleaner_button,
        FujiScope.bot_cleaning_request_territorial_manager: TM_CR_button,
    }


async def send_menu_by_scopes(message: Message, edit=None):
    """
    Sends specific menu for user by his role.

    If `edit = True` - calling `Message.edit_text` instead `Message.answer`
    """
    scopes = []
    worker = services.get_worker_by_telegram_id(message.chat.id)
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
        await try_answer(
            message=message,
            text=hbold("Фуджи team"),
            reply_markup=menu,
        )


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


async def try_answer(
    message: Message, text: str, reply_markup: Any = None, return_message: bool = False
) -> bool | Message:
    """
    Tries to answer message.

    If return_message = True then return Message

    Returns: `True` if message answered, `False` otherwise.
    """
    try:
        if return_message:
            return await message.answer(text=text, reply_markup=reply_markup)
        await message.answer(text=text, reply_markup=reply_markup)
        return True
    except TelegramAPIError:
        return False


async def try_edit_or_answer(
    message: Message, text: str, reply_markup: Any = None, return_message: bool = False
) -> bool | Message:
    """
    Tries to edit message.
    if the `message` unsuccessfully edited
    then answers message by `Message.answer_text`.

    If return_message = True then return Message

    Returns: `True` if message edited, `False` otherwise.
    """
    if not await try_edit_message(
        message=message, text=text, reply_markup=reply_markup
    ):
        if return_message:
            return await try_answer(message, text, reply_markup, return_message)
        await try_answer(message, text, reply_markup, return_message)
        return False
    if return_message:
        return message
    return True


async def notify_workers_by_scope(
    scope: FujiScope, message: str, reply_markup: InlineKeyboardMarkup | None = None
) -> None:
    """
    Sends notify `message` to workers by their `scope`.
    """
    telegram_ids: set[int] = {
        worker.telegram_id
        for worker in (
            *services.get_workers_by_scope(scope),
            *services.get_workers_by_scope(FujiScope.admin),
        )
        if worker.telegram_id is not None
    }

    for id in telegram_ids:
        msg = await notify_worker_by_telegram_id(
            id=id,
            message=message,
            reply_markup=reply_markup,
        )
        if not msg:
            continue
        await send_menu_by_scopes(message=msg)


async def notify_workers_in_department_by_scope(
    scope: FujiScope,
    department_id: int,
    message: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """
    Sends notify `message` to workers in department by their `scope`.
    """
    workers: list[WorkerSchema] = [
        *services.get_workers_in_department_by_scope(scope, department_id),
        *services.get_workers_by_scope(FujiScope.admin),
    ]

    for worker in workers:
        if not worker.telegram_id:
            continue
        msg = await notify_worker_by_telegram_id(
            id=worker.telegram_id,
            message=message,
            reply_markup=reply_markup,
        )
        if not msg:
            continue
        await send_menu_by_scopes(message=msg)


async def notify_worker_by_telegram_id(
    id: int, message: str, reply_markup: InlineKeyboardMarkup | None = None
) -> Optional[Message]:
    """
    Tries to sends notify `message` to worker by their `id`.

    Returns sended `Message`.
    """
    try:
        await get_bot().send_message(
            chat_id=id, text=message, reply_markup=reply_markup
        )
    except Exception:
        return None


async def handle_documents(
    message: Message,
    state: FSMContext,
    document_name: str,
    on_complete: Callable[[Any, Any], Awaitable[Any]],
    condition: Callable[[list[Document | PhotoSize]], str | None] | None = None,
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

        if condition is not None:
            error = condition(documents)
            if error is not None:
                await try_delete_message(message)
                msg = await message.answer(error)
                await asyncio.sleep(1)
                await try_delete_message(msg)
                return

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


def get_worker_my_message(message: Message | CallbackQuery) -> WorkerSchema | None:
    """:return: `message` owner if he exist in DB."""
    if isinstance(message, CallbackQuery):
        message = message.message

    return services.get_worker_by_telegram_id(message.chat.id)
