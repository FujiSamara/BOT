import asyncio
from io import BytesIO
from typing import Optional
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

# from fastapi import UploadFile

from bot.text import format_err

from bot.kb import (
    get_department_it_repairman,
    create_reply_keyboard_resize,
    repairman_bids_it_menu,
    repairman_department_menu,
    create_inline_keyboard,
    get_create_repairman_it_menu,
    bids_pending_for_repairman,
)
from bot.states import RepairmanBidForm

from bot.text import bid_create_greet
from bot.handlers.utils import (
    try_edit_or_answer,
    try_delete_message,
    try_edit_message,
    download_file,
    #     handle_documents_form,
    #     handle_documents,
)
from bot.handlers.bids_it.utils import (
    get_bid_it_list_info,
    get_short_bid_it_info,
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
)
from db.models import ApprovalStatus

router = Router(name="bid_it_repairman")


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
    print(callback.message.chat.id)
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
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Выполнить заявку",
                        callback_data=WorkerBidITCallbackData(
                            id=callback_data.id,
                            endpoint_name="take_bid_it_for_repairman",
                        ).pack(),
                    )
                ],
                [bids_pending_for_repairman],
            ]
        ),
    )


@router.callback_query(F.data == "bids_pending_for_repairman")
async def get_pending_bids_for_repairman(callback: CallbackQuery, state: FSMContext):
    dep = (await state.get_data()).get("department")
    bids = get_bids_it_with_status(dep, ApprovalStatus.pending)
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
        get_department_it_repairman,
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
    print(callback_data.id)
    await state.update_data(bid_id=callback_data.id)
    await try_delete_message(callback.message)
    await try_edit_or_answer(
        callback.message,
        hbold(bid_create_greet),
        await get_create_repairman_it_menu(state),
    )


@router.callback_query(F.data == "get_photo_rm")
async def get_photo_rm(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RepairmanBidForm.photo)
    await try_delete_message(callback.message)
    await callback.message.answer(
        hbold("Приложите фото выполненной работы:"),
        reply_markup=create_inline_keyboard(
            InlineKeyboardButton(
                text="Вернуться к заявке",
                callback_data=WorkerBidITCallbackData(
                    id=(await state.get_data()).get("bid_id"),
                    endpoint_name="take_bid_it_for_repairman",
                ).pack(),
            )
        ),
    )


@router.message(RepairmanBidForm.photo)
async def set_photo_rm(message: Message, state: FSMContext):
    if message.document or message.photo:
        content = None
        if message.content_type == "photo":
            content = message.photo[-1]
        elif message.content_type == "document":
            content = message.document
        await state.update_data(photo=content)
        await message.answer(
            hbold(bid_create_greet),
            reply_markup=await get_create_repairman_it_menu(state),
        )
    else:
        await message.answer(
            format_err, reply_markup=await get_create_repairman_it_menu(state)
        )


@router.callback_query(F.data == "send_bid_it_rm")
async def send_bid_it_rm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    photo = data.get("photo")
    bid_id = data.get("bid_id")
    file: Optional[BytesIO] = None

    if photo:
        file = await download_file(photo)

    await update_bid_it_rm(
        bid_id=bid_id,
        photo=file,
        telegram_id=callback.message.chat.id,
    )

    await try_edit_message(message=callback.message, text="Успешно!")
    await asyncio.sleep(1)
    await send_department_menu_for_repairman(callback.message, state)
