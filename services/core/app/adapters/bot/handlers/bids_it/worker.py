from fastapi import UploadFile
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    Message,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    BufferedInputFile,
    InputMediaDocument,
    InlineKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
import asyncio

# bot imports
from app.adapters.bot.kb import (
    create_reply_keyboard_resize,
    create_inline_keyboard,
    create_bid_it_menu_button,
)
from app.adapters.bot.handlers.bids_it.kb import (
    get_create_bid_it_menu,
    settings_bid_it_menu_button,
    bid_it_create_history_button,
    bid_it_menu,
    bid_it_create_pending_button,
)

from app.adapters.bot.text import (
    bid_create_greet,
    format_err,
    notification_it_repairman,
)

from app.adapters.bot.states import BidITCreating, Base

from app.adapters.bot.handlers.bids_it.utils import (
    filter_media_by_done,
    filter_media_by_reopen,
    get_id_by_problem_type,
    get_bid_it_list_info,
    get_bid_it_info,
    create_buttons_for_worker,
)
from app.adapters.bot.handlers.utils import (
    try_edit_or_answer,
    try_edit_message,
    try_delete_message,
    download_file,
    handle_documents,
    handle_documents_form,
    notify_worker_by_telegram_id,
)

from app.adapters.bot.handlers.bids_it.schemas import (
    BidITViewMode,
    BidITCallbackData,
)

# database imports
from app.services import (
    get_problems_it_types,
    get_problems_it_schema,
    create_bid_it,
    get_history_bids_it_by_worker_telegram_id,
    get_bid_it_by_id,
    get_pending_bids_it_by_worker_telegram_id,
    get_repairman_telegram_id_by_department,
    get_worker_department_by_telegram_id,
)

from app.infra.config.settings import settings

router = Router(name="bid_it_creating")


async def clear_state_with_success_it(
    message: Message, state: FSMContext, sleep_time=1, edit=False
):
    ans = await message.answer(hbold("Успешно!"), reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(sleep_time)
    await ans.delete()
    await state.set_state(Base.none)
    if edit:
        await try_edit_message(
            message=message,
            text=hbold(bid_create_greet),
            reply_markup=await get_create_bid_it_menu(state),
        )
    else:
        await message.answer(
            hbold(bid_create_greet),
            reply_markup=await get_create_bid_it_menu(state),
        )


@router.callback_query(F.data == "get_create_bid_it_menu")
async def get_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(Base.none)
    await callback.message.edit_text(
        hbold("Заявка в IT отдел"), reply_markup=bid_it_menu
    )


# Create section
@router.callback_query(F.data == "get_bid_it_settings_menu")
async def get_settings_form(callback: CallbackQuery, state: FSMContext):
    await clear_state_with_success_it(callback.message, state, sleep_time=0, edit=True)


# Send bid to the IT department
@router.callback_query(F.data == "send_bid_it")
async def send_bid_it(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.set_state(Base.none)
    problem = data.get("problem")
    photos = data.get("photo")
    comment = data.get("comment")
    telegram_id = data.get("telegram_id")

    document_files: list[UploadFile] = []

    for doc in photos:
        document_files.append(await download_file(doc))

    problem_id = get_id_by_problem_type(problem, get_problems_it_schema())

    create_bid_it(
        problem_id=problem_id,
        comment=comment,
        files=document_files,
        telegram_id=telegram_id,
    )

    await try_edit_message(message=callback.message, text="Успешно!")
    await asyncio.sleep(1)
    await try_edit_message(
        message=callback.message,
        text=hbold("Заявка в IT отдел"),
        reply_markup=bid_it_menu,
    )
    await state.clear()

    department_name = get_worker_department_by_telegram_id(telegram_id).name
    repairman_id = get_repairman_telegram_id_by_department(department_name)

    await notify_worker_by_telegram_id(repairman_id, notification_it_repairman)


# Problem type
@router.callback_query(F.data == "get_problem_it")
async def get_problem_type(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidITCreating.problem)
    problems = get_problems_it_types()
    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        hbold("Выберите проблему из списка:"),
        reply_markup=create_reply_keyboard_resize("⏪ Назад", *problems),
    )
    await state.update_data(msg=msg)


@router.message(BidITCreating.problem)
async def set_problem_type(message: Message, state: FSMContext):
    await state.update_data(telegram_id=message.from_user.id)
    problems = get_problems_it_types()
    data = await state.get_data()
    msg = data.get("msg")
    if message.text == "⏪ Назад":
        await try_delete_message(message)
        await try_delete_message(msg)
        await clear_state_with_success_it(message, state, sleep_time=0)
    elif message.text in problems:
        await try_delete_message(message)
        await try_delete_message(msg)
        await state.update_data(problem=message.text)
        await clear_state_with_success_it(message, state)
    else:
        await message.answer(format_err)


# Photo
@router.callback_query(F.data == "get_photo")
async def get_photo(callback: CallbackQuery, state: FSMContext):
    await handle_documents_form(callback.message, state, BidITCreating.photo)


@router.message(BidITCreating.photo)
async def set_photo(message: Message, state: FSMContext):
    await handle_documents(
        message,
        state,
        "photo",
        clear_state_with_success_it,
    )


# Comment
@router.callback_query(F.data == "get_comment")
async def get_comment_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidITCreating.comment)
    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        hbold("Введите комментарий:"),
        reply_markup=create_inline_keyboard(settings_bid_it_menu_button),
    )
    await state.update_data(msg=msg)


@router.message(BidITCreating.comment)
async def set_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    await state.update_data(comment=message.text)
    # await asyncio.sleep(1)
    await try_delete_message(message)
    await try_delete_message(msg)
    await clear_state_with_success_it(message, state)


# Bid IT history
@router.callback_query(F.data == "get_create_history_bid_it")
async def get_bids_it_history(callback: CallbackQuery):
    bids = get_history_bids_it_by_worker_telegram_id(callback.message.chat.id)
    bids = sorted(bids, key=lambda bid: bid.opening_date, reverse=True)[:10]
    keyboard = create_inline_keyboard(
        *(
            InlineKeyboardButton(
                text=get_bid_it_list_info(bid),
                callback_data=BidITCallbackData(
                    id=bid.id,
                    mode=BidITViewMode.history,
                    endpoint_name="create_bid_it_info",
                ).pack(),
            )
            for bid in bids
        ),
        create_bid_it_menu_button,
    )
    await try_delete_message(callback.message)
    await callback.message.answer("История заявок:", reply_markup=keyboard)


@router.callback_query(
    BidITCallbackData.filter(F.mode == BidITViewMode.history),
    BidITCallbackData.filter(F.endpoint_name == "create_bid_it_info"),
)
async def get_bid(
    callback: CallbackQuery, callback_data: BidITCallbackData, state: FSMContext
):
    bid_it_id = callback_data.id
    bid_it = get_bid_it_by_id(bid_it_id)
    data = await state.get_data()
    if "msgs_for_delete" in data:
        for msg in data["msgs_for_delete"]:
            await try_delete_message(msg)
        await state.update_data(msgs_for_delete=[])

    caption = get_bid_it_info(bid_it)
    buttons = []
    create_buttons_for_worker(buttons, bid_it, callback_data)
    buttons.append([bid_it_create_history_button])

    await try_edit_message(
        message=callback.message,
        text=caption,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


# Show pending bids
@router.callback_query(
    BidITCallbackData.filter(F.mode == BidITViewMode.pending),
    BidITCallbackData.filter(F.endpoint_name == "create_bid_it_info"),
)
async def get_bid_state(callback: CallbackQuery, callback_data: BidITCallbackData):
    bid_id = callback_data.id
    bid = get_bid_it_by_id(bid_id)
    await try_delete_message(callback.message)
    text = get_bid_it_info(bid)
    buttons = []
    create_buttons_for_worker(buttons, bid, callback_data)
    buttons.append([bid_it_create_pending_button])
    await callback.message.answer(
        text=text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data == "get_create_pending_bid_it")
async def get_bids_it_pending(callback: CallbackQuery):
    bids = get_pending_bids_it_by_worker_telegram_id(callback.message.chat.id)
    bids = sorted(bids, key=lambda bid: bid.opening_date, reverse=True)[:10]
    keyboard = create_inline_keyboard(
        *(
            InlineKeyboardButton(
                text=get_bid_it_list_info(bid),
                callback_data=BidITCallbackData(
                    id=bid.id,
                    mode=BidITViewMode.pending,
                    endpoint_name="create_bid_it_info",
                ).pack(),
            )
            for bid in bids
        ),
        create_bid_it_menu_button,
    )
    await try_delete_message(callback.message)
    await callback.message.answer("Ожидающие заявки:", reply_markup=keyboard)


@router.callback_query(
    BidITCallbackData.filter(F.endpoint_name == "create_documents_problem"),
)
async def get_documents_problem(
    callback: CallbackQuery, callback_data: BidITCallbackData, state: FSMContext
):
    bid = get_bid_it_by_id(callback_data.id)
    media: list[InputMediaDocument] = []
    deleted_files_count = 0

    for document in bid.problem_photos:
        if document.document.filename != settings.stubname:
            media.append(
                InputMediaDocument(
                    media=BufferedInputFile(
                        file=document.document.file.read(),
                        filename=document.document.filename,
                    ),
                )
            )
        else:
            deleted_files_count += 1

    await try_delete_message(callback.message)

    if len(media) > 0:
        msgs = await callback.message.answer_media_group(media=media)
        await state.update_data(msgs_for_delete=msgs)
        await msgs[0].reply(
            text=hbold("Выберите действие:")
            + (
                f"\nУдаленно файлов: {deleted_files_count}"
                if deleted_files_count > 0
                else ""
            ),
            reply_markup=create_inline_keyboard(
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=BidITCallbackData(
                        id=bid.id,
                        mode=callback_data.mode,
                        endpoint_name="create_bid_it_info",
                    ).pack(),
                )
            ),
        )
    else:
        await try_edit_or_answer(
            message=callback.message,
            text=hbold("Выберите действие:")
            + (
                f"\nУдаленно файлов: {deleted_files_count}"
                if deleted_files_count > 0
                else ""
            ),
            reply_markup=create_inline_keyboard(
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=BidITCallbackData(
                        id=bid.id,
                        mode=callback_data.mode,
                        endpoint_name="create_bid_it_info",
                    ).pack(),
                )
            ),
        )


@router.callback_query(
    BidITCallbackData.filter(F.endpoint_name == "create_documents_done"),
)
async def get_documents_done(
    callback: CallbackQuery, callback_data: BidITCallbackData, state: FSMContext
):
    bid = get_bid_it_by_id(callback_data.id)
    media: list[InputMediaDocument] = []
    deleted_files_count = 0

    for document in bid.work_photos:
        if document.document.filename != settings.stubname:
            media.append(
                InputMediaDocument(
                    media=BufferedInputFile(
                        file=document.document.file.read(),
                        filename=document.document.filename,
                    ),
                )
            )
        else:
            deleted_files_count += 1

    filter_media_by_done(media)

    await try_delete_message(callback.message)

    if len(media) > 0:
        msgs = await callback.message.answer_media_group(media=media)
        await state.update_data(msgs_for_delete=msgs)
        await msgs[0].reply(
            text=hbold("Выберите действие:")
            + (
                f"\nУдаленно файлов: {deleted_files_count}"
                if deleted_files_count > 0
                else ""
            ),
            reply_markup=create_inline_keyboard(
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=BidITCallbackData(
                        id=bid.id,
                        mode=callback_data.mode,
                        endpoint_name="create_bid_it_info",
                    ).pack(),
                )
            ),
        )
    else:
        await try_edit_or_answer(
            message=callback.message,
            text=hbold("Выберите действие:")
            + (
                f"\nУдаленно файлов: {deleted_files_count}"
                if deleted_files_count > 0
                else ""
            ),
            reply_markup=create_inline_keyboard(
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=BidITCallbackData(
                        id=bid.id,
                        mode=callback_data.mode,
                        endpoint_name="create_bid_it_info",
                    ).pack(),
                )
            ),
        )


@router.callback_query(
    BidITCallbackData.filter(F.endpoint_name == "create_documents_done_reopen"),
)
async def get_documents_done_reopen(
    callback: CallbackQuery, callback_data: BidITCallbackData, state: FSMContext
):
    bid = get_bid_it_by_id(callback_data.id)
    media: list[InputMediaDocument] = []
    deleted_files_count = 0

    for document in bid.work_photos:
        if document.document.filename != settings.stubname:
            media.append(
                InputMediaDocument(
                    media=BufferedInputFile(
                        file=document.document.file.read(),
                        filename=document.document.filename,
                    ),
                )
            )
        else:
            deleted_files_count += 1

    filter_media_by_reopen(media)

    await try_delete_message(callback.message)

    if len(media) > 0:
        msgs = await callback.message.answer_media_group(media=media)
        await state.update_data(msgs_for_delete=msgs)
        await msgs[0].reply(
            text=hbold("Выберите действие:")
            + (
                f"\nУдаленно файлов: {deleted_files_count}"
                if deleted_files_count > 0
                else ""
            ),
            reply_markup=create_inline_keyboard(
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=BidITCallbackData(
                        id=bid.id,
                        mode=callback_data.mode,
                        endpoint_name="create_bid_it_info",
                    ).pack(),
                )
            ),
        )
    else:
        await try_edit_or_answer(
            message=callback.message,
            text=hbold("Выберите действие:")
            + (
                f"\nУдаленно файлов: {deleted_files_count}"
                if deleted_files_count > 0
                else ""
            ),
            reply_markup=create_inline_keyboard(
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=BidITCallbackData(
                        id=bid.id,
                        mode=callback_data.mode,
                        endpoint_name="create_bid_it_info",
                    ).pack(),
                )
            ),
        )
