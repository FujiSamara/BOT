import asyncio

from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
    InputMediaDocument,
    BufferedInputFile,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from bot.text import (
    format_err,
    notification_it_repairman_reopen,
    notification_it_worker,
)

from bot.kb import (
    create_reply_keyboard_resize,
    create_inline_keyboard,
    create_reply_keyboard_raw,
)
from bot.handlers.bids_it.kb import (
    tm_department_menu,
    tm_bids_it_menu,
    get_create_tm_bid_it_menu,
    bids_pending_for_tm,
    back_tm_button,
    bid_it_tm_create_history_button,
)
from bot.states import TMForm, Base

from bot.handlers.utils import (
    notify_worker_by_telegram_id,
    try_edit_or_answer,
    try_delete_message,
    try_edit_message,
)
from bot.handlers.bids_it.utils import (
    get_bid_it_list_info,
    get_bid_it_info,
    clear_state_with_success_it_tm,
    filter_media_by_reopen,
    create_buttons_for_territorial_manager,
)
from bot.handlers.bids_it.schemas import (
    BidITViewMode,
    BidITCallbackData,
)


from db.service import (
    update_bid_it_tm,
    get_departments_names_by_tm_telegram_id,
    get_pending_bids_it_for_territorial_manager,
    get_history_bids_it_for_territorial_manager,
    get_bid_it_by_id,
)
from db.models import ApprovalStatus

router = Router(name="bid_it_territorial_manager")


# Set department


@router.callback_query(F.data == "get_back_tm")
async def get_tm_menu(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department")
    await state.clear()
    await state.update_data(department=department_name)
    await state.set_state(Base.none)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f'IT заявки ТУ на производстве "{department_name}"'),
        reply_markup=tm_bids_it_menu,
    )


@router.callback_query(F.data == "get_it_tm_menu")
async def get_tm_it_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Base.none)
    await try_edit_message(
        message=callback.message,
        text="IT заявки ТУ",
        reply_markup=tm_department_menu,
    )


@router.callback_query(F.data == "get_department_it_tm")
async def get_tm_department_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TMForm.department)
    dep = get_departments_names_by_tm_telegram_id(callback.message.chat.id)
    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        hbold("Выберите производство:"),
        reply_markup=create_reply_keyboard_resize("⏪ Назад", *dep),
    )
    await state.update_data(msg=msg)


@router.message(TMForm.department)
async def set_department_type(message: Message, state: FSMContext):
    dep = get_departments_names_by_tm_telegram_id(message.from_user.id)
    data = await state.get_data()
    msg = data.get("msg")
    if message.text == "⏪ Назад":
        await state.clear()
        await state.set_state(Base.none)
        await try_delete_message(message)
        await try_delete_message(msg)
        await try_edit_or_answer(
            message=message,
            text="IT заявки ТУ",
            reply_markup=tm_department_menu,
        )
    elif message.text in dep:
        ans = await message.answer(
            hbold("Успешно!"), reply_markup=ReplyKeyboardRemove()
        )
        await asyncio.sleep(1)
        await ans.delete()
        await try_delete_message(message)
        await try_delete_message(msg)
        await state.set_state(Base.none)
        await state.update_data(department=message.text)
        await try_edit_or_answer(
            message=message,
            text=hbold(f'IT заявки ТУ на производстве "{message.text}"'),
            reply_markup=tm_bids_it_menu,
        )
    else:
        await message.answer(format_err)


# Get pending bids IT


@router.callback_query(F.data == "bids_pending_for_tm")
async def show_pending_bids_it_tm(callback: CallbackQuery, state: FSMContext):
    dep = (await state.get_data()).get("department")
    telegram_id = callback.message.chat.id
    bids = get_pending_bids_it_for_territorial_manager(telegram_id, dep)
    bids = sorted(bids, key=lambda bid: bid.opening_date, reverse=True)
    keyboard = create_inline_keyboard(
        *(
            InlineKeyboardButton(
                text=get_bid_it_list_info(bid),
                callback_data=BidITCallbackData(
                    id=bid.id,
                    mode=BidITViewMode.pending,
                    endpoint_name="create_bid_it_info_tm",
                ).pack(),
            )
            for bid in bids
        ),
        back_tm_button,
    )
    await try_delete_message(callback.message)
    dep = (await state.get_data()).get("department")
    await callback.message.answer(
        f"Производство: {dep}\nОжидающие заявки:", reply_markup=keyboard
    )


@router.callback_query(
    BidITCallbackData.filter(F.mode == BidITViewMode.pending),
    BidITCallbackData.filter(F.endpoint_name == "create_bid_it_info_tm"),
)
async def get_bid_state(
    callback: CallbackQuery, state: FSMContext, callback_data: BidITCallbackData
):
    bid_id = callback_data.id
    bid = get_bid_it_by_id(bid_id)
    await try_delete_message(callback.message)

    data = await state.get_data()
    await state.clear()
    await state.update_data(department=data.get("department"))

    text = get_bid_it_info(bid)
    buttons = []
    buttons.append(
        [
            InlineKeyboardButton(
                text="Выполнить заявку",
                callback_data=BidITCallbackData(
                    id=bid_id,
                    mode=BidITViewMode.pending,
                    endpoint_name="take_bid_it_for_tm",
                ).pack(),
            ),
        ]
    )
    create_buttons_for_territorial_manager(buttons, bid, callback_data)
    buttons.append([bids_pending_for_tm])

    await callback.message.answer(
        text=text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(
    BidITCallbackData.filter(F.mode == BidITViewMode.pending),
    BidITCallbackData.filter(F.endpoint_name == "take_bid_it_for_tm"),
)
async def get_bid_it_for_tm(
    callback: CallbackQuery,
    state: FSMContext,
    callback_data: BidITCallbackData,
):
    await state.update_data(bid_id=callback_data.id)
    await try_delete_message(callback.message)

    bid = get_bid_it_by_id(callback_data.id)
    problem_text = get_bid_it_info(bid)
    callback_data.endpoint_name = "create_bid_it_info_tm"
    await try_edit_or_answer(
        callback.message,
        problem_text,
        await get_create_tm_bid_it_menu(callback_data, state),
    )


# Set mark


@router.callback_query(F.data == "get_mark_tm")
async def get_mark_tm(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TMForm.mark)
    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        hbold("Поставьте оценку работе:"),
        reply_markup=create_reply_keyboard_raw(*[str(i) for i in range(1, 6)]),
    )
    await state.update_data(msg=msg)


@router.message(TMForm.mark)
async def set_mark_tm(message: Message, state: FSMContext):
    await state.update_data(mark=int(message.text))
    data = await state.get_data()
    msg = data.get("msg")
    await try_delete_message(message)
    await try_delete_message(msg)
    await clear_state_with_success_it_tm(message, state)


# Set work comment


@router.callback_query(F.data == "get_work_comment_tm")
async def get_work_comment_tm(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TMForm.work_comment)
    await try_delete_message(callback.message)
    msg = await callback.message.answer(hbold("Введите комментарий:"))
    await state.update_data(msg=msg)


@router.message(TMForm.work_comment)
async def set_work_comment_tm(message: Message, state: FSMContext):
    await state.update_data(work_comment=message.text)
    data = await state.get_data()
    msg = data.get("msg")
    await try_delete_message(message)
    await try_delete_message(msg)
    await clear_state_with_success_it_tm(message, state)


# Send bid


@router.callback_query(F.data == "send_bid_it_tm")
async def send_bid_it_tm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mark = data.get("mark")
    work_comment = data.get("work_comment")
    bid_id = data.get("bid_id")

    update_bid_it_tm(
        bid_id=bid_id,
        mark=mark,
        work_comment=work_comment,
    )

    await try_edit_message(message=callback.message, text="Успешно!")
    await asyncio.sleep(1)
    await state.clear()
    await state.update_data(department=data.get("department"))
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f'IT заявки ТУ на производстве "{data.get("department")}"'),
        reply_markup=tm_bids_it_menu,
    )

    bid = get_bid_it_by_id(bid_id)

    if bid.status == ApprovalStatus.denied:
        await notify_worker_by_telegram_id(
            bid.repairman.telegram_id, notification_it_repairman_reopen
        )
    await notify_worker_by_telegram_id(bid.worker.telegram_id, notification_it_worker)


# Get bids IT history


@router.callback_query(F.data == "get_create_history_bid_it_tm")
async def get_history_bids_for_tm(callback: CallbackQuery, state: FSMContext):
    telegram_id = callback.message.chat.id
    dep = (await state.get_data()).get("department")
    bids = get_history_bids_it_for_territorial_manager(telegram_id, dep)
    bids = sorted(bids, key=lambda bid: bid.opening_date, reverse=True)
    keyboard = create_inline_keyboard(
        *(
            InlineKeyboardButton(
                text=get_bid_it_list_info(bid),
                callback_data=BidITCallbackData(
                    id=bid.id,
                    mode=BidITViewMode.history,
                    endpoint_name="create_bid_it_info_tm",
                ).pack(),
            )
            for bid in bids
        ),
        back_tm_button,
    )
    await try_delete_message(callback.message)
    await callback.message.answer(
        f"Производство: {dep}\nИстория заявок:", reply_markup=keyboard
    )


@router.callback_query(
    BidITCallbackData.filter(F.mode == BidITViewMode.history),
    BidITCallbackData.filter(F.endpoint_name == "create_bid_it_info_tm"),
)
async def get_bid_tm(
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
    create_buttons_for_territorial_manager(buttons, bid_it, callback_data)
    buttons.append([bid_it_tm_create_history_button])

    await try_edit_message(
        message=callback.message,
        text=caption,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


# Get documents


@router.callback_query(
    BidITCallbackData.filter(F.endpoint_name == "create_documents_problem_tm"),
)
async def get_documents_problem_tm(
    callback: CallbackQuery, callback_data: BidITCallbackData, state: FSMContext
):
    bid = get_bid_it_by_id(callback_data.id)
    media: list[InputMediaDocument] = []

    for document in bid.problem_photos:
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
                callback_data=BidITCallbackData(
                    id=bid.id,
                    mode=callback_data.mode,
                    endpoint_name="create_bid_it_info_tm",
                ).pack(),
            )
        ),
    )


@router.callback_query(
    BidITCallbackData.filter(F.endpoint_name == "create_documents_done_tm"),
)
async def get_documents_done_tm(
    callback: CallbackQuery, callback_data: BidITCallbackData, state: FSMContext
):
    bid = get_bid_it_by_id(callback_data.id)
    media: list[InputMediaDocument] = []

    for document in bid.work_photos:
        media.append(
            InputMediaDocument(
                media=BufferedInputFile(
                    file=document.document.file.read(),
                    filename=document.document.filename,
                ),
            )
        )
    filter_media_by_reopen(media)

    await try_delete_message(callback.message)
    msgs = await callback.message.answer_media_group(media=media)
    await state.update_data(msgs_for_delete=msgs)
    await msgs[0].reply(
        text=hbold("Выберите действие:"),
        reply_markup=create_inline_keyboard(
            InlineKeyboardButton(
                text="Назад",
                callback_data=BidITCallbackData(
                    id=bid.id,
                    mode=callback_data.mode,
                    endpoint_name="create_bid_it_info_tm",
                ).pack(),
            )
        ),
    )


@router.callback_query(
    BidITCallbackData.filter(F.endpoint_name == "create_documents_done_reopen_tm"),
)
async def get_documents_done_reopen_tm(
    callback: CallbackQuery, callback_data: BidITCallbackData, state: FSMContext
):
    bid = get_bid_it_by_id(callback_data.id)
    media: list[InputMediaDocument] = []

    for document in bid.work_photos:
        media.append(
            InputMediaDocument(
                media=BufferedInputFile(
                    file=document.document.file.read(),
                    filename=document.document.filename,
                ),
            )
        )

    filter_media_by_reopen(media)

    await try_delete_message(callback.message)
    msgs = await callback.message.answer_media_group(media=media)
    await state.update_data(msgs_for_delete=msgs)
    await msgs[0].reply(
        text=hbold("Выберите действие:"),
        reply_markup=create_inline_keyboard(
            InlineKeyboardButton(
                text="Назад",
                callback_data=BidITCallbackData(
                    id=bid.id,
                    mode=callback_data.mode,
                    endpoint_name="create_bid_it_info_tm",
                ).pack(),
            )
        ),
    )
