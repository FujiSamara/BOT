from io import BytesIO
from typing import Optional
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    Message,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
import asyncio

# bot imports
from bot.kb import (
    get_create_bid_it_menu,
    create_reply_keyboard,
    settings_bid_it_menu_button,
    bid_it_create_history_button,
    create_inline_keyboard,
    bid_it_menu,
    create_bid_it_menu_button,
    bid_it_create_pending_button,
)

from bot.text import bid_create_greet, format_err

from bot.states import BidITCreating, Base

from bot.handlers.bids_it.utils import (
    get_id_by_problem_type,
    get_bid_it_list_info,
    get_full_bid_it_info,
    get_short_bid_it_info,
)
from bot.handlers.utils import (
    try_edit_message,
    try_delete_message,
    download_file,
)

from bot.handlers.bids_it.schemas import (
    BidITViewMode,
    BidITViewType,
    BidITCallbackData,
)

# db imports
from db.service import (
    get_problems_it_types,
    get_problems_it_schema,
    create_bid_it,
    get_bids_it_by_worker_telegram_id,
    get_bid_it_by_id,
    get_pending_bids_it_by_worker_telegram_id,
)


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
    photo = data.get("photo")
    comment = data.get("comment")
    telegram_id = data.get("telegram_id")
    file: Optional[BytesIO] = None

    if photo:
        file = await download_file(photo)

    problem_id = get_id_by_problem_type(problem, get_problems_it_schema())

    await create_bid_it(
        problem_id=problem_id,
        comment=comment,
        photo=file,
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


# Problem type
@router.callback_query(F.data == "get_problem_it")
async def get_problem_type(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidITCreating.problem)
    problems = get_problems_it_types()
    await try_delete_message(callback.message)
    await callback.message.answer(
        hbold("Выберите тип проблемы:"),
        reply_markup=create_reply_keyboard("⏪ Назад", *problems),
    )


@router.message(BidITCreating.problem)
async def set_problem_type(message: Message, state: FSMContext):
    print(message.from_user.id, message.from_user.is_bot)
    await state.update_data(telegram_id=message.from_user.id)
    problems = get_problems_it_types()
    if message.text == "⏪ Назад":
        await clear_state_with_success_it(message, state, sleep_time=0)
    elif message.text in problems:
        await state.update_data(problem=message.text)
        await clear_state_with_success_it(message, state)
    else:
        await message.answer(format_err)


# Photo
@router.callback_query(F.data == "get_photo")
async def get_photo(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidITCreating.photo)
    await try_delete_message(callback.message)
    await callback.message.answer(
        hbold("Приложите фото:"),
        reply_markup=create_inline_keyboard(settings_bid_it_menu_button),
    )


@router.message(BidITCreating.photo)
async def set_photo(message: Message, state: FSMContext):
    if message.document or message.photo:
        content = None
        if message.content_type == "photo":
            content = message.photo[-1]
        elif message.content_type == "document":
            content = message.document
        await state.update_data(photo=content)
        await clear_state_with_success_it(message, state)
    else:
        await message.answer(
            format_err, reply_markup=create_inline_keyboard(settings_bid_it_menu_button)
        )


# Comment
@router.callback_query(F.data == "get_comment")
async def get_comment_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BidITCreating.comment)
    await try_delete_message(callback.message)
    await callback.message.answer(
        hbold("Введите комментарий:"),
        reply_markup=create_inline_keyboard(settings_bid_it_menu_button),
    )


@router.message(BidITCreating.comment)
async def set_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.html_text)
    await clear_state_with_success_it(message, state)


# Bid IT history
@router.callback_query(F.data == "get_create_history_bid_it")
async def get_bids_it_history(callback: CallbackQuery):
    bids = get_bids_it_by_worker_telegram_id(callback.message.chat.id)
    bids = sorted(bids, key=lambda bid: bid.opening_date, reverse=True)[:10]
    keyboard = create_inline_keyboard(
        *(
            InlineKeyboardButton(
                text=get_bid_it_list_info(bid),
                callback_data=BidITCallbackData(
                    id=bid.id,
                    mode=BidITViewMode.full,
                    type=BidITViewType.creation,
                    endpoint_name="create_bid_it_info",
                ).pack(),
            )
            for bid in bids
        ),
        create_bid_it_menu_button,
    )
    await try_delete_message(callback.message)
    await callback.message.answer("История заявок в IT отдел:", reply_markup=keyboard)


@router.callback_query(
    BidITCallbackData.filter(F.type == BidITViewType.creation),
    BidITCallbackData.filter(F.mode == BidITViewMode.full),
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

    caption = get_full_bid_it_info(bid_it)

    await try_edit_message(
        message=callback.message,
        text=caption,
        reply_markup=create_inline_keyboard(
            bid_it_create_history_button,
            InlineKeyboardButton(
                text="Показать документы",
                callback_data=BidITCallbackData(
                    id=bid_it.id,
                    mode=callback_data.mode,
                    type=BidITViewType.creation,
                    endpoint_name="create_documents",
                ).pack(),
            ),
        ),
    )


# Show pending bids
@router.callback_query(
    BidITCallbackData.filter(F.type == BidITViewType.creation),
    BidITCallbackData.filter(F.mode == BidITViewMode.state_only),
    BidITCallbackData.filter(F.endpoint_name == "create_bid_it_info"),
)
async def get_bid_state(callback: CallbackQuery, callback_data: BidITCallbackData):
    bid_id = callback_data.id
    bid = get_bid_it_by_id(bid_id)
    await try_delete_message(callback.message)

    text = get_short_bid_it_info(bid)

    await callback.message.answer(
        text=text, reply_markup=create_inline_keyboard(bid_it_create_pending_button)
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
                    mode=BidITViewMode.state_only,
                    type=BidITViewType.creation,
                    endpoint_name="create_bid_it_info",
                ).pack(),
            )
            for bid in bids
        ),
        create_bid_it_menu_button,
    )
    await try_delete_message(callback.message)
    await callback.message.answer("Ожидающие заявки:", reply_markup=keyboard)
