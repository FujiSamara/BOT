# Department.territorial_manager_id

import asyncio
# from io import BytesIO
# from typing import Optional
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
    tm_department_menu,
    create_reply_keyboard_resize,
    tm_bids_it_menu,
    get_department_it_tm,
    create_inline_keyboard,
    get_create_tm_bid_it_menu,
    bids_pending_for_tm,
    create_reply_keyboard_raw,
)
from bot.states import TMForm, Base

from bot.handlers.utils import (
    try_edit_or_answer,
    try_delete_message,
    try_edit_message,
    # download_file,
    # handle_documents_form,
    # handle_documents,
)
from bot.handlers.bids_it.utils import (
    get_bid_it_list_info,
    get_short_bid_it_info,
    get_full_bid_it_info_tm,
    clear_state_with_success_it_tm,
)
from bot.handlers.bids_it.schemas import (
    BidITViewMode,
    BidITViewType,
    BidITCallbackData,
    WorkerBidITCallbackData,
)


from db.service import (
    update_bid_it_tm,
    get_departments_names_by_tm_telegram_id,
    get_bids_it_with_status,
    get_bid_it_by_id,
)
from db.models import ApprovalStatus

router = Router(name="bid_it_territorial_manager")

@router.callback_query(F.data == "get_it_tm_menu")
async def get_tm_it_menu(callback: CallbackQuery):
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
    await callback.message.answer(
        hbold("Выберите производство:"),
        reply_markup=create_reply_keyboard_resize("⏪ Назад", *dep),
    )


@router.message(TMForm.department)
async def set_department_type(message: Message, state: FSMContext):
    dep = get_departments_names_by_tm_telegram_id(message.from_user.id)
    if message.text == "⏪ Назад":
        await state.clear()
        await try_edit_or_answer(
            message=message,
            text="IT заявки ТУ",
            reply_markup=tm_department_menu,
        )
    elif message.text in dep:
        await state.update_data(department=message.text)
        await try_edit_or_answer(
            message=message,
            text=hbold(f'IT заявки ТУ на производстве "{message.text}"'),
            reply_markup=tm_bids_it_menu,
        )
    else:
        await message.answer(format_err)


@router.callback_query(F.data == "bids_pending_for_tm")
async def show_pending_bids_it_tm(callback: CallbackQuery, state: FSMContext):
    dep = (await state.get_data()).get("department")
    bids = get_bids_it_with_status(dep, ApprovalStatus.pending_approval)
    bids = sorted(bids, key=lambda bid: bid.opening_date, reverse=True)
    keyboard = create_inline_keyboard(
        *(
            InlineKeyboardButton(
                text=get_bid_it_list_info(bid),
                callback_data=BidITCallbackData(
                    id=bid.id,
                    mode=BidITViewMode.state_only,
                    type=BidITViewType.creation,
                    endpoint_name="create_bid_it_info_tm",
                ).pack(),
            )
            for bid in bids
        ),
        get_department_it_tm,
    )
    await try_delete_message(callback.message)
    dep = (await state.get_data()).get("department")
    await callback.message.answer(
        f"Производство: {dep}\nОжидающие заявки:", reply_markup=keyboard
    )


@router.callback_query(
    BidITCallbackData.filter(F.type == BidITViewType.creation),
    BidITCallbackData.filter(F.mode == BidITViewMode.state_only),
    BidITCallbackData.filter(F.endpoint_name == "create_bid_it_info_tm"),
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
                            endpoint_name="take_bid_it_for_tm",
                        ).pack(),
                    )
                ],
                [bids_pending_for_tm],
            ]
        ),
    )


@router.callback_query(
    WorkerBidITCallbackData.filter(F.endpoint_name == "take_bid_it_for_tm")
)
async def get_bid_it_for_tm(
    callback: CallbackQuery,
    state: FSMContext,
    callback_data: WorkerBidITCallbackData,
):
    print(callback_data.id)
    await state.update_data(bid_id=callback_data.id)
    await try_delete_message(callback.message)

    bid = get_bid_it_by_id(callback_data.id)
    problem_text = get_full_bid_it_info_tm(bid)
    await try_edit_or_answer(
        callback.message,
        f"Выполненная заявка:\n{problem_text}",
        await get_create_tm_bid_it_menu(state),
    )


# Mark

@router.callback_query(F.data == "get_mark_tm")
async def get_mark_tm(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TMForm.mark)
    await try_delete_message(callback.message)
    await callback.message.answer(
        hbold("Поставьте оценку работе:"),
        reply_markup=create_reply_keyboard_raw(*[str(i) for i in range(1, 6)])
    )


@router.message(TMForm.mark)
async def set_mark_tm(message: Message, state: FSMContext):
    await state.update_data(mark=int(message.text))
    await clear_state_with_success_it_tm(message, state)


# Work comment

@router.callback_query(F.data == "get_work_comment_tm")
async def get_work_comment_tm(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TMForm.work_comment)
    await try_delete_message(callback.message)
    await callback.message.answer(
        hbold("Введите комментарий:")
    )


@router.message(TMForm.work_comment)
async def set_work_comment_tm(message: Message, state: FSMContext):
    await state.update_data(work_comment=message.html_text)
    await clear_state_with_success_it_tm(message, state)


@router.callback_query(F.data == "send_bid_it_tm")
async def send_bid_it_rm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mark = data.get("mark")
    work_comment = data.get("work_comment")
    bid_id = data.get("bid_id")

    update_bid_it_tm(
        bid_id=bid_id,
        mark=mark,
        work_comment=work_comment,
        telegram_id=callback.message.chat.id,
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
