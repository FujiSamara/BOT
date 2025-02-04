from aiogram.types import CallbackQuery, BufferedInputFile, InputMediaDocument, Message
from typing import Callable
from aiogram import F, Router
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
import asyncio

# bot imports
from app.adapters.bot.kb import (
    create_inline_keyboard,
    main_menu_button,
    chief_pending_button,
    chief_dismissal_menu_button,
)
from app.adapters.bot.states import (
    Base,
    DismissalChief,
)

from app.adapters.bot.handlers.utils import (
    try_delete_message,
    try_edit_message,
)
from app.adapters.bot.handlers.dismissal.utils import (
    get_dismissal_blank_info,
    get_dismissal_list_info,
)
from app.adapters.bot.handlers.dismissal.schemas import (
    ActionType,
    DismissalCallbackData,
)

# db imports
from app.services import (
    get_dismissal_by_id,
    get_pending_dismissal_blanks_for_chief,
    update_dismissal_by_chief,
)
from app.infra.database.models import ApprovalStatus, Dismissal
from app.schemas import DismissalSchema

router = Router(name="chief")

name = "chief"
approving_endpoint_name = "chief_dismissal_approving"
documents_endpoint_name = "chief__dismissal_documents"


@router.callback_query(F.data == "get_create_chief_dismissal_menu")
async def get_chief_menu(callback: CallbackQuery):
    keyboard = create_inline_keyboard(chief_pending_button, main_menu_button)
    await try_edit_message(
        message=callback.message,
        text="Согласование увольнений",
        reply_markup=keyboard,
    )


def get_pending_dismissal_keyboard(callback: CallbackQuery) -> InlineKeyboardMarkup:
    blanks = []
    blanks = get_pending_dismissal_blanks_for_chief(callback.message.chat.id)
    blanks = sorted(blanks, key=lambda blank: blank.create_date, reverse=True)[:10]
    return create_inline_keyboard(
        *(
            InlineKeyboardButton(
                text=get_dismissal_list_info(blank),
                callback_data=DismissalCallbackData(
                    id=blank.id,
                    endpoint_name=name,
                ).pack(),
            )
            for blank in blanks
        ),
        chief_dismissal_menu_button,
    )


@router.callback_query(F.data == "chief_dismissal_pending")
async def get_pendings(callback: CallbackQuery):
    keyboard = get_pending_dismissal_keyboard(callback)
    await try_delete_message(callback.message)
    await callback.message.answer("Ожидающие согласования:", reply_markup=keyboard)


@router.callback_query(DismissalCallbackData.filter(F.endpoint_name == name))
async def get_dismissal_blank(
    callback: CallbackQuery,
    callback_data: DismissalCallbackData,
    state: FSMContext,
):
    blank = get_dismissal_by_id(callback_data.id)
    data = await state.get_data()
    if "msgs_for_delete" in data:
        for msg in data["msgs_for_delete"]:
            await try_delete_message(msg)
        await state.update_data(msgs_for_delete=[])

    caption = get_dismissal_blank_info(blank)

    buttons = [
        InlineKeyboardButton(
            text="Показать документы",
            callback_data=DismissalCallbackData(
                id=blank.id,
                endpoint_name=documents_endpoint_name,
            ).pack(),
        ),
        InlineKeyboardButton(
            text="Согласовать",
            callback_data=DismissalCallbackData(
                id=blank.id,
                action=ActionType.approving,
                endpoint_name=approving_endpoint_name,
            ).pack(),
        ),
        InlineKeyboardButton(
            text="Отказать",
            callback_data=DismissalCallbackData(
                id=blank.id,
                action=ActionType.declining,
                endpoint_name=approving_endpoint_name,
            ).pack(),
        ),
        chief_pending_button,
    ]
    await try_edit_message(
        message=callback.message,
        text=caption,
        reply_markup=create_inline_keyboard(*buttons),
    )


@router.callback_query(
    DismissalCallbackData.filter(F.action == ActionType.approving),
    DismissalCallbackData.filter(F.endpoint_name == approving_endpoint_name),
)
async def approve_dismissal(
    callback: CallbackQuery,
    callback_data: DismissalCallbackData,
):
    dismissal = get_dismissal_by_id(callback_data.id)

    await update_dismissal_by_chief(dismissal)

    msg = await callback.message.answer(text="Успешно!")
    await msg.delete()
    keyboard = get_pending_dismissal_keyboard(callback)
    await try_delete_message(callback.message)
    await asyncio.sleep(1)
    await try_edit_message(
        callback.message, text="Ожидающие согласования:", reply_markup=keyboard
    )


@router.callback_query(
    DismissalCallbackData.filter(F.action == ActionType.declining),
    DismissalCallbackData.filter(F.endpoint_name == approving_endpoint_name),
)
async def decline_dismissal(
    callback: CallbackQuery,
    callback_data: DismissalCallbackData,
    state: FSMContext,
):
    dismissal = get_dismissal_by_id(callback_data.id)
    await try_edit_message(callback.message, hbold("Введите причину отказа:"))
    await state.set_state(DismissalChief.comment)
    await state.update_data(
        generator=get_pendings,
        callback=callback,
        dismissal=dismissal,
        column_name=Dismissal.chief_state.name,
        callback_data=DismissalCallbackData(id=callback_data.id, endpoint_name=name),
    )


@router.message(DismissalChief.comment)
async def comment_decline(message: Message, state: FSMContext):
    data = await state.get_data()
    generator: Callable = data["generator"]
    callback: CallbackQuery = data["callback"]
    dismissal: DismissalSchema = data.get("dismissal")
    dismissal.chief_state = ApprovalStatus.denied
    await update_dismissal_by_chief(dismissal, message.text)
    ans = await message.answer(hbold("Успешно!"))
    await asyncio.sleep(1)
    await ans.delete()
    await state.clear()
    await state.set_state(Base.none)
    await try_delete_message(callback.message)
    await try_delete_message(message)
    await generator(callback)


@router.callback_query(
    DismissalCallbackData.filter(F.endpoint_name == documents_endpoint_name)
)
async def get_documents(
    callback: CallbackQuery,
    callback_data: DismissalCallbackData,
    state: FSMContext,
):
    blank = get_dismissal_by_id(callback_data.id)
    media: list[InputMediaDocument] = []

    for document in blank.documents:
        media.append(
            InputMediaDocument(
                media=BufferedInputFile(
                    file=document.document.file.read(),
                    filename=document.document.filename,
                ),
            )
        )
    await try_delete_message(callback.message)
    msgs = await callback.message.answer_media_group(media=media)
    await state.update_data(msgs_for_delete=msgs)
    await msgs[0].reply(
        text=hbold("Выберите действие:"),
        reply_markup=create_inline_keyboard(
            InlineKeyboardButton(
                text="Назад",
                callback_data=DismissalCallbackData(
                    id=blank.id,
                    endpoint_name=name,
                ).pack(),
            )
        ),
    )
