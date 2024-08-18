import asyncio
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
    BufferedInputFile,
    InputMediaDocument,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from fastapi import UploadFile

from bot.text import format_err

from bot.kb import (
    create_reply_keyboard_resize,
    repairman_bids_it_menu,
    repairman_department_menu,
    create_inline_keyboard,
    bids_pending_for_repairman,
    bid_it_rm_create_history_button,
    back_repairman_button,
)
from bot.states import RepairmanBidForm, Base

from bot.handlers.utils import (
    try_edit_or_answer,
    try_delete_message,
    try_edit_message,
    download_file,
    handle_documents_form,
    handle_documents,
)
from bot.handlers.bids_it.utils import (
    get_bid_it_list_info,
    get_short_bid_it_info,
    clear_state_with_success_rm,
    get_full_bid_it_info,
)
from bot.handlers.bids_it.schemas import (
    BidITViewMode,
    BidITViewType,
    BidITCallbackData,
    WorkerBidITCallbackData,
)


from db.service import (
    update_bid_it_rm,
    get_departments_names_by_repairman_telegram_id,
    get_bids_it_with_status,
    get_bid_it_by_id,
    get_bids_it_by_repairman,
)
from db.models import ApprovalStatus

router = Router(name="bid_it_repairman")


# Set department


async def send_department_menu_for_repairman(message: Message, state: FSMContext):
    await state.clear()
    await try_edit_or_answer(
        message=message,
        text=hbold("IT заявки"),
        reply_markup=repairman_department_menu,
    )


@router.callback_query(F.data == "get_it_repairman_menu")
async def get_repairman_department_menu(callback: CallbackQuery):
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
    await callback.message.answer(
        hbold("Выберите производство:"),
        reply_markup=create_reply_keyboard_resize("⏪ Назад", *dep),
    )


@router.message(RepairmanBidForm.department)
async def set_department_type(message: Message, state: FSMContext):
    dep = get_departments_names_by_repairman_telegram_id(message.from_user.id)
    if message.text == "⏪ Назад":
        await send_department_menu_for_repairman(message, state)
    elif message.text in dep:
        await state.update_data(department=message.text)
        await try_edit_or_answer(
            message=message,
            text=hbold(f'Заявки на производстве "{message.text}"'),
            reply_markup=repairman_bids_it_menu,
        )
    else:
        await message.answer(format_err)


# Pending bids IT


@router.callback_query(
    BidITCallbackData.filter(F.type == BidITViewType.creation),
    BidITCallbackData.filter(F.mode == BidITViewMode.state_only),
    BidITCallbackData.filter(F.endpoint_name == "create_bid_it_info_rm"),
)
async def get_bid_state(callback: CallbackQuery, callback_data: BidITCallbackData):
    bid_id = callback_data.id
    bid = get_bid_it_by_id(bid_id)
    await try_delete_message(callback.message)

    text = get_short_bid_it_info(bid)

    await callback.message.answer(
        text=text,
        reply_markup=create_inline_keyboard(
            InlineKeyboardButton(
                text="Выполнить заявку",
                callback_data=WorkerBidITCallbackData(
                    id=callback_data.id,
                    endpoint_name="take_bid_it_for_repairman",
                ).pack(),
            ),
            InlineKeyboardButton(
                text="Показать фото проблемы",
                callback_data=BidITCallbackData(
                    id=bid_id,
                    mode=callback_data.mode,
                    type=BidITViewType.creation,
                    endpoint_name="create_bid_it_info_rm",
                ).pack(),
            ),
            bids_pending_for_repairman,
        ),
    )


@router.callback_query(F.data == "get_back_rm")
async def get_repairman_menu(callback: CallbackQuery, state: FSMContext):
    department_name = (await state.get_data()).get("department")
    await try_edit_or_answer(
        message=callback.message,
        text=hbold(f'Заявки на производстве "{department_name}"'),
        reply_markup=repairman_bids_it_menu,
    )


@router.callback_query(F.data == "bids_pending_for_repairman")
async def get_pending_bids_for_repairman(callback: CallbackQuery, state: FSMContext):
    dep = (await state.get_data()).get("department")
    telegtram_id = callback.message.chat.id
    bids = get_bids_it_with_status(telegtram_id, dep, ApprovalStatus.pending)
    bids = sorted(bids, key=lambda bid: bid.opening_date, reverse=True)
    keyboard = create_inline_keyboard(
        *(
            InlineKeyboardButton(
                text=get_bid_it_list_info(bid),
                callback_data=BidITCallbackData(
                    id=bid.id,
                    mode=BidITViewMode.state_only,
                    type=BidITViewType.creation,
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
        f"Производство: {dep}\nОжидающие заявки:", reply_markup=keyboard
    )


@router.callback_query(
    WorkerBidITCallbackData.filter(F.endpoint_name == "take_bid_it_for_repairman")
)
async def get_bid_it_for_repairman(
    callback: CallbackQuery,
    state: FSMContext,
    callback_data: WorkerBidITCallbackData,
):
    await state.update_data(bid_id=callback_data.id)
    await try_delete_message(callback.message)
    await clear_state_with_success_rm(callback.message, state)


# Set photo


@router.callback_query(F.data == "get_photo_rm")
async def get_photo_rm(callback: CallbackQuery, state: FSMContext):
    await handle_documents_form(callback.message, state, RepairmanBidForm.photo)


@router.message(RepairmanBidForm.photo)
async def set_photo_rm(message: Message, state: FSMContext):
    await handle_documents(
        message,
        state,
        "photo",
        clear_state_with_success_rm,
    )


# Send bid


@router.callback_query(F.data == "send_bid_it_rm")
async def send_bid_it_rm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.set_state(Base.none)
    photos = data.get("photo")
    bid_id = data.get("bid_id")

    document_files: list[UploadFile] = []

    for doc in photos:
        document_files.append(await download_file(doc))

    await update_bid_it_rm(
        bid_id=bid_id,
        files=document_files,
        telegram_id=callback.message.chat.id,
    )

    await try_edit_message(message=callback.message, text="Успешно!")
    await asyncio.sleep(1)
    await send_department_menu_for_repairman(callback.message, state)


# Bids history


@router.callback_query(F.data == "get_create_history_bid_it_rm")
async def get_history_bids_for_repairman(callback: CallbackQuery, state: FSMContext):
    telegram_id = callback.message.chat.id
    dep = (await state.get_data()).get("department")
    bids = get_bids_it_by_repairman(telegram_id, dep)
    bids = sorted(bids, key=lambda bid: bid.opening_date, reverse=True)
    keyboard = create_inline_keyboard(
        *(
            InlineKeyboardButton(
                text=get_bid_it_list_info(bid),
                callback_data=BidITCallbackData(
                    id=bid.id,
                    mode=BidITViewMode.full,
                    type=BidITViewType.creation,
                    endpoint_name="create_bid_it_info_rm",
                ).pack(),
            )
            for bid in bids
        ),
        back_repairman_button,
    )
    await try_delete_message(callback.message)
    await callback.message.answer(
        f"Производство: {dep}\nОжидающие заявки:", reply_markup=keyboard
    )


@router.callback_query(
    BidITCallbackData.filter(F.type == BidITViewType.creation),
    BidITCallbackData.filter(F.mode == BidITViewMode.full),
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

    caption = get_full_bid_it_info(bid_it)

    await try_edit_message(
        message=callback.message,
        text=caption,
        reply_markup=create_inline_keyboard(
            InlineKeyboardButton(
                text="Показать фото проблемы",
                callback_data=BidITCallbackData(
                    id=bid_it.id,
                    mode=callback_data.mode,
                    type=BidITViewType.creation,
                    endpoint_name="create_documents_problem_rm",
                ).pack(),
            ),
            InlineKeyboardButton(
                text="Показать фото выполненной работы",
                callback_data=BidITCallbackData(
                    id=bid_it.id,
                    mode=callback_data.mode,
                    type=BidITViewType.creation,
                    endpoint_name="create_documents_solve_rm",
                ).pack(),
            ),
            bid_it_rm_create_history_button,
        ),
    )


# Get documents


@router.callback_query(
    BidITCallbackData.filter(F.type == BidITViewType.creation),
    BidITCallbackData.filter(F.endpoint_name == "create_documents_problem_rm"),
)
async def get_documents_problem_rm(
    callback: CallbackQuery, callback_data: BidITCallbackData, state: FSMContext
):
    bid = get_bid_it_by_id(callback_data.id)
    media: list[InputMediaDocument] = [
        InputMediaDocument(
            media=BufferedInputFile(
                file=bid.problem_photo[i].document.file.read(),
                filename=bid.problem_photo[i].document.filename,
            )
        )
        for i in range(len(bid.problem_photo))
    ]
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
                    type=BidITViewType.creation,
                    endpoint_name="create_bid_it_info_rm",
                ).pack(),
            )
        ),
    )


@router.callback_query(
    BidITCallbackData.filter(F.type == BidITViewType.creation),
    BidITCallbackData.filter(F.endpoint_name == "create_documents_solve_rm"),
)
async def get_documents_solve_rm(
    callback: CallbackQuery, callback_data: BidITCallbackData, state: FSMContext
):
    bid = get_bid_it_by_id(callback_data.id)
    media: list[InputMediaDocument] = [
        InputMediaDocument(
            media=BufferedInputFile(
                file=bid.work_photo[i].document.file.read(),
                filename=bid.work_photo[i].document.filename,
            )
        )
        for i in range(len(bid.work_photo))
    ]
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
                    type=BidITViewType.creation,
                    endpoint_name="create_bid_it_info_rm",
                ).pack(),
            )
        ),
    )
