import asyncio
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
    BufferedInputFile,
    InputMediaDocument,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from fastapi import UploadFile

from app.adapters.bot.text import (
    format_err,
    notification_it_territorial_manager,
    notification_it_worker,
)
from app.adapters.bot.kb import (
    create_reply_keyboard_resize,
    create_inline_keyboard,
)
from app.adapters.bot.handlers.bids_it.kb import (
    repairman_bids_it_menu,
    repairman_department_menu,
    bids_pending_for_repairman,
    bid_it_rm_create_history_button,
    back_repairman_button,
    bids_it_denied_for_repairman,
)
from app.adapters.bot.states import RepairmanBidForm, Base

from app.adapters.bot.handlers.utils import (
    try_edit_or_answer,
    try_delete_message,
    try_edit_message,
    download_file,
    handle_documents_form,
    handle_documents,
    notify_worker_by_telegram_id,
)
from app.adapters.bot.handlers.bids_it.utils import (
    clear_state_with_success_rm_rework,
    clear_state_with_success_rm_work,
    create_buttons_for_repairman,
    get_bid_it_list_info,
    get_bid_it_info,
    filter_media_by_reopen,
    filter_media_by_done,
)
from app.adapters.bot.handlers.bids_it.schemas import (
    BidITViewMode,
    BidITCallbackData,
)


from app.services import (
    update_bid_it_rm,
    get_departments_names_by_repairman_telegram_id,
    get_pending_bids_it_by_repairman,
    get_denied_bids_it_by_repairman,
    get_bid_it_by_id,
    get_history_bids_it_by_repairman,
)

router = Router(name="bid_it_repairman")


# Set department


async def send_department_menu_for_repairman(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Base.none)
    await try_edit_or_answer(
        message=message,
        text=hbold("IT заявки"),
        reply_markup=repairman_department_menu,
    )


@router.callback_query(F.data == "get_it_repairman_menu")
async def get_repairman_department_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Base.none)
    await try_edit_message(
        message=callback.message,
        text=hbold("IT заявки"),
        reply_markup=repairman_department_menu,
    )


@router.callback_query(F.data == "get_department_it_repairman")
async def get_department_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RepairmanBidForm.department)
    dep = get_departments_names_by_repairman_telegram_id(callback.message.chat.id)
    await try_delete_message(callback.message)
    msg = await callback.message.answer(
        hbold("Выберите предприятие:"),
        reply_markup=create_reply_keyboard_resize("⏪ Назад", *dep),
    )
    await state.update_data(msg=msg)


@router.message(RepairmanBidForm.department)
async def set_department_type(message: Message, state: FSMContext):
    dep = get_departments_names_by_repairman_telegram_id(message.from_user.id)
    data = await state.get_data()
    msg = data.get("msg")
    if message.text == "⏪ Назад":
        ans = await message.answer(
            hbold("Успешно!"), reply_markup=ReplyKeyboardRemove()
        )
        await asyncio.sleep(1)
        await ans.delete()
        await try_delete_message(message)
        await try_delete_message(msg)
        await send_department_menu_for_repairman(message, state)
    elif message.text in dep:
        ans = await message.answer(
            hbold("Успешно!"), reply_markup=ReplyKeyboardRemove()
        )
        await asyncio.sleep(1)
        await ans.delete()
        await state.set_state(Base.none)
        await state.update_data(department=message.text)
        await try_delete_message(message)  #########
        await try_delete_message(msg)  ##########
        await try_edit_or_answer(
            message=message,
            text=hbold(f'Заявки на производстве "{message.text}"'),
            reply_markup=repairman_bids_it_menu,
        )
    else:
        await message.answer(format_err)


# Pending bids IT


@router.callback_query(
    BidITCallbackData.filter(F.mode == BidITViewMode.pending),
    BidITCallbackData.filter(F.endpoint_name == "create_bid_it_info_rm"),
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

    await callback.message.answer(
        text=text,
        reply_markup=create_inline_keyboard(
            InlineKeyboardButton(
                text="Выполнить заявку",
                callback_data=BidITCallbackData(
                    id=callback_data.id,
                    mode=callback_data.mode,
                    endpoint_name="take_bid_it_for_repairman",
                ).pack(),
            ),
            InlineKeyboardButton(
                text="Показать фото проблемы",
                callback_data=BidITCallbackData(
                    id=bid_id,
                    mode=callback_data.mode,
                    endpoint_name="create_documents_problem_rm",
                ).pack(),
            ),
            bids_pending_for_repairman,
        ),
    )


@router.callback_query(F.data == "get_back_rm")
async def get_repairman_menu(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department")
    await state.clear()
    await state.update_data(department=department_name)
    await state.set_state(Base.none)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f'Заявки на производстве "{department_name}"'),
        reply_markup=repairman_bids_it_menu,
    )


@router.callback_query(F.data == "bids_pending_for_repairman")
async def get_pending_bids_for_repairman(callback: CallbackQuery, state: FSMContext):
    dep = (await state.get_data()).get("department")
    telegtram_id = callback.message.chat.id
    bids = get_pending_bids_it_by_repairman(telegtram_id, dep)
    bids = sorted(bids, key=lambda bid: bid.opening_date, reverse=True)
    keyboard = create_inline_keyboard(
        *(
            InlineKeyboardButton(
                text=get_bid_it_list_info(bid),
                callback_data=BidITCallbackData(
                    id=bid.id,
                    mode=BidITViewMode.pending,
                    endpoint_name="create_bid_it_info_rm",
                ).pack(),
            )
            for bid in bids
        ),
        back_repairman_button,
    )
    await try_delete_message(callback.message)
    dep = (await state.get_data()).get("department")
    await callback.message.answer(
        f"Предприятие: {dep}\nОжидающие заявки:", reply_markup=keyboard
    )


@router.callback_query(
    BidITCallbackData.filter(F.endpoint_name == "take_bid_it_for_repairman")
)
async def get_bid_it_for_repairman(
    callback: CallbackQuery,
    state: FSMContext,
    callback_data: BidITCallbackData,
):
    await state.update_data(bid_id=callback_data.id)
    await try_delete_message(callback.message)
    if callback_data.mode == BidITViewMode.pending:
        await clear_state_with_success_rm_work(callback.message, state)
    elif callback_data.mode == BidITViewMode.deny:
        await clear_state_with_success_rm_rework(callback.message, state)


# Set photo


@router.callback_query(F.data == "get_photo_work_rm")
async def get_photo_work_rm(callback: CallbackQuery, state: FSMContext):
    await handle_documents_form(callback.message, state, RepairmanBidForm.photo_work)


@router.message(RepairmanBidForm.photo_work)
async def set_photo_work_rm(message: Message, state: FSMContext):
    await handle_documents(
        message,
        state,
        "photo_work",
        clear_state_with_success_rm_work,
    )


@router.callback_query(F.data == "get_photo_rework_rm")
async def get_photo_rework_rm(callback: CallbackQuery, state: FSMContext):
    await handle_documents_form(callback.message, state, RepairmanBidForm.photo_rework)


@router.message(RepairmanBidForm.photo_rework)
async def set_photo_rework_rm(message: Message, state: FSMContext):
    await handle_documents(
        message,
        state,
        "photo_rework",
        clear_state_with_success_rm_rework,
    )


# Send bid


@router.callback_query(BidITCallbackData.filter(F.endpoint_name == "send_bid_it_rm"))
async def send_bid_it_rm(
    callback: CallbackQuery, state: FSMContext, callback_data: BidITCallbackData
):
    data = await state.get_data()
    await state.set_state(Base.none)
    department_name = data.get("department")
    photos = ""
    if callback_data == BidITViewMode.pending:
        photos = data.get("photo_work")
    elif callback_data == BidITViewMode.deny:
        photos = data.get("photo_rework")
    bid_id = data.get("bid_id")

    document_files: list[UploadFile] = []

    for doc in photos:
        document_files.append(await download_file(doc))

    update_bid_it_rm(
        bid_id=bid_id,
        files=document_files,
    )

    await try_edit_message(message=callback.message, text="Успешно!")
    await asyncio.sleep(1)
    await state.clear()
    await state.update_data(department=department_name)
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f'Заявки на производстве "{department_name}"'),
        reply_markup=repairman_bids_it_menu,
    )

    bid = get_bid_it_by_id(bid_id)

    await notify_worker_by_telegram_id(
        bid.territorial_manager.telegram_id, notification_it_territorial_manager
    )
    await notify_worker_by_telegram_id(bid.worker.telegram_id, notification_it_worker)


# Denied bids IT


@router.callback_query(F.data == "bids_it_denied_for_repairman")
async def get_denied_bids_for_repairman(callback: CallbackQuery, state: FSMContext):
    telegram_id = callback.message.chat.id
    dep = (await state.get_data()).get("department")
    bids = get_denied_bids_it_by_repairman(telegram_id, dep)
    bids = sorted(bids, key=lambda bid: bid.reopening_date, reverse=True)
    keyboard = create_inline_keyboard(
        *(
            InlineKeyboardButton(
                text=get_bid_it_list_info(bid),
                callback_data=BidITCallbackData(
                    id=bid.id,
                    mode=BidITViewMode.deny,
                    endpoint_name="create_bid_it_info_rm",
                ).pack(),
            )
            for bid in bids
        ),
        back_repairman_button,
    )
    await try_delete_message(callback.message)
    await callback.message.answer(
        f"Предприятие: {dep}\nОтклоненные заявки:", reply_markup=keyboard
    )


@router.callback_query(
    BidITCallbackData.filter(F.mode == BidITViewMode.deny),
    BidITCallbackData.filter(F.endpoint_name == "create_bid_it_info_rm"),
)
async def get_denied_bid_repairman(
    callback: CallbackQuery, callback_data: BidITCallbackData, state: FSMContext
):
    bid_it_id = callback_data.id
    bid_it = get_bid_it_by_id(bid_it_id)
    data = await state.get_data()
    if "msgs_for_delete" in data:
        for msg in data["msgs_for_delete"]:
            await try_delete_message(msg)
        await state.update_data(msgs_for_delete=[])

    data = await state.get_data()
    await state.clear()
    await state.update_data(department=data.get("department"))

    caption = get_bid_it_info(bid_it)

    buttons = []
    buttons.append(
        [
            InlineKeyboardButton(
                text="Выполнить заявку",
                callback_data=BidITCallbackData(
                    id=callback_data.id,
                    mode=callback_data.mode,
                    endpoint_name="take_bid_it_for_repairman",
                ).pack(),
            )
        ],
    )
    create_buttons_for_repairman(buttons, bid_it, callback_data)
    buttons.append([bids_it_denied_for_repairman])

    await try_edit_message(
        message=callback.message,
        text=caption,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


# Bids history


@router.callback_query(F.data == "get_create_history_bid_it_rm")
async def get_history_bids_for_repairman(callback: CallbackQuery, state: FSMContext):
    telegram_id = callback.message.chat.id
    dep = (await state.get_data()).get("department")
    bids = get_history_bids_it_by_repairman(telegram_id, dep)
    bids = sorted(bids, key=lambda bid: bid.opening_date, reverse=True)
    keyboard = create_inline_keyboard(
        *(
            InlineKeyboardButton(
                text=get_bid_it_list_info(bid),
                callback_data=BidITCallbackData(
                    id=bid.id,
                    mode=BidITViewMode.history,
                    endpoint_name="create_bid_it_info_rm",
                ).pack(),
            )
            for bid in bids
        ),
        back_repairman_button,
    )
    await try_delete_message(callback.message)
    await callback.message.answer(
        f"Предприятие: {dep}\nИстория заявок:", reply_markup=keyboard
    )


@router.callback_query(
    BidITCallbackData.filter(F.mode == BidITViewMode.history),
    BidITCallbackData.filter(F.endpoint_name == "create_bid_it_info_rm"),
)
async def get_bid_repairman(
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
    create_buttons_for_repairman(buttons, bid_it, callback_data)
    buttons.append([bid_it_rm_create_history_button])

    await try_edit_message(
        message=callback.message,
        text=caption,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


# Get documents


@router.callback_query(
    BidITCallbackData.filter(F.endpoint_name == "create_documents_problem_rm"),
)
async def get_documents_problem_rm(
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
                    endpoint_name="create_bid_it_info_rm",
                ).pack(),
            )
        ),
    )


@router.callback_query(
    BidITCallbackData.filter(F.endpoint_name == "create_documents_done_rm"),
)
async def get_documents_done_rm(
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

    filter_media_by_done(media)

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
                    endpoint_name="create_bid_it_info_rm",
                ).pack(),
            )
        ),
    )


@router.callback_query(
    BidITCallbackData.filter(F.endpoint_name == "create_documents_done_reopen_rm"),
)
async def get_documents_done_reopen_rm(
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
                    endpoint_name="create_bid_it_info_rm",
                ).pack(),
            )
        ),
    )
