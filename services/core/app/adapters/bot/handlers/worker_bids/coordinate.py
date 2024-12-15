from asyncio import sleep
from aiogram import Router, F
from app.adapters.bot.kb import (
    get_coordinate_worker_bid_btn,
    coordinate_worker_bid_menu,
    get_pending_coordinate_worker_bid_btn,
    create_inline_keyboard,
)
from aiogram.utils.markdown import hbold
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
    InputMediaDocument,
    BufferedInputFile,
)
from aiogram.fsm.context import FSMContext
from app.adapters.bot.handlers.utils import (
    try_edit_or_answer,
    try_delete_message,
)
from app.adapters.bot.states import (
    Base,
    WorkerBidCoordination,
)
from app.adapters.bot.handlers.worker_bids.utils import get_full_worker_bid_info
from app.adapters.bot import text
from app.adapters.bot.handlers.worker_bids.schemas import (
    WorkerBidCallbackData,
    BidViewMode,
)
from app.infra.database.models import ApprovalStatus

from app.services import (
    get_pending_approval_bids,
    get_worker_bid_by_id,
    update_worker_bid_bot,
)

router = Router(name="coordinate_worker_bid")


@router.callback_query(F.data == get_coordinate_worker_bid_btn.callback_data)
async def get_coordinate_worker_bid(message: CallbackQuery | Message):
    if isinstance(message, CallbackQuery):
        message = message.message
    await try_edit_or_answer(
        message=message,
        text=hbold(get_coordinate_worker_bid_btn.text),
        reply_markup=coordinate_worker_bid_menu,
    )


@router.callback_query(F.data == get_pending_coordinate_worker_bid_btn.callback_data)
async def get_pending_coordinate_worker_bid(message: CallbackQuery | Message):
    if isinstance(message, CallbackQuery):
        message = message.message
    bids = get_pending_approval_bids() or []
    buttons = []
    for bid in bids:
        buttons.append(
            InlineKeyboardButton(
                text=f"{bid.id} {bid.l_name} {bid.f_name[0]} {bid.o_name[0]} {bid.post.name}",
                callback_data=WorkerBidCallbackData(
                    id=bid.id,
                    mode=BidViewMode.full_with_approve,
                    endpoint_name="get_pending_bid",
                ).pack(),
            )
        )
    buttons.append(
        InlineKeyboardButton(
            text=text.back,
            callback_data=get_coordinate_worker_bid_btn.callback_data,
        ),
    )
    await try_edit_or_answer(
        message=message,
        text=hbold(get_pending_coordinate_worker_bid_btn.text),
        reply_markup=create_inline_keyboard(
            *buttons,
        ),
    )


@router.callback_query(
    WorkerBidCallbackData.filter(
        F.endpoint_name == "get_pending_bid",
    ),
    WorkerBidCallbackData.filter(
        F.mode == BidViewMode.full_with_approve,
    ),
)
async def get_pending_bid(
    callback: CallbackQuery, callback_data: WorkerBidCallbackData, state: FSMContext
):
    data = await state.get_data()
    if "msgs" in data.keys():
        for msg in data["msgs"]:
            await try_delete_message(msg)
    bid = get_worker_bid_by_id(callback_data.id)
    buttons = []
    if bid.worksheet != []:
        buttons.append(
            InlineKeyboardButton(
                text="Анкета",
                callback_data=WorkerBidCallbackData(
                    id=callback_data.id,
                    mode=callback_data.mode,
                    endpoint_name="show_docs",
                    doc_type="worksheet",
                ).pack(),
            )
        )
    if bid.passport != []:
        buttons.append(
            InlineKeyboardButton(
                text="Пасспорт",
                callback_data=WorkerBidCallbackData(
                    id=callback_data.id,
                    mode=callback_data.mode,
                    endpoint_name="show_docs",
                    doc_type="passport",
                ).pack(),
            )
        )
    if bid.work_permission != []:
        buttons.append(
            InlineKeyboardButton(
                text="Разрешение на работу",
                callback_data=WorkerBidCallbackData(
                    id=callback_data.id,
                    mode=callback_data.mode,
                    endpoint_name="show_docs",
                    doc_type="work_permission",
                ).pack(),
            )
        )

    await try_edit_or_answer(
        message=callback.message,
        text=get_full_worker_bid_info(bid),
        reply_markup=create_inline_keyboard(
            *buttons,
            InlineKeyboardButton(
                text="Согласовать",
                callback_data=WorkerBidCallbackData(
                    id=callback_data.id,
                    mode=callback_data.mode,
                    endpoint_name="get_comment",
                    state=1,
                ).pack(),
            ),
            InlineKeyboardButton(
                text="Отказать",
                callback_data=WorkerBidCallbackData(
                    id=callback_data.id,
                    mode=callback_data.mode,
                    endpoint_name="get_comment",
                    state=0,
                ).pack(),
            ),
            InlineKeyboardButton(
                text=text.back,
                callback_data=get_pending_coordinate_worker_bid_btn.callback_data,
            ),
        ),
    )


@router.callback_query(WorkerBidCallbackData.filter(F.endpoint_name == "show_docs"))
async def show_docs(
    callback: CallbackQuery, callback_data: WorkerBidCallbackData, state: FSMContext
):
    bid = get_worker_bid_by_id(callback_data.id)
    media: list[InputMediaDocument] = []
    for photo in getattr(bid, callback_data.doc_type):
        media.append(
            InputMediaDocument(
                media=BufferedInputFile(
                    file=await photo.document.read(), filename=photo.document.filename
                )
            )
        )
    await try_delete_message(callback.message)
    msgs = await callback.message.answer_media_group(
        media=media,
        protect_content=True,
    )
    await state.update_data(msgs=msgs)
    await msgs[0].reply(
        text=hbold("Выберите действие:"),
        reply_markup=create_inline_keyboard(
            InlineKeyboardButton(
                text=text.back,
                callback_data=WorkerBidCallbackData(
                    id=callback_data.id,
                    mode=callback_data.mode,
                    endpoint_name="get_pending_bid",
                ).pack(),
            ),
        ),
    )


@router.callback_query(
    WorkerBidCallbackData.filter(F.endpoint_name == "get_comment"),
    WorkerBidCallbackData.filter(F.mode == BidViewMode.full_with_approve),
)
async def get_comment(
    callback: CallbackQuery, callback_data: WorkerBidCallbackData, state: FSMContext
):
    await state.update_data(id=callback_data.id, status=callback_data.state)
    message = await try_edit_or_answer(
        callback.message, text=hbold("Введите комментарий:"), return_message=True
    )
    await state.update_data(msg=message)
    await state.set_state(WorkerBidCoordination.comment)


@router.message(WorkerBidCoordination.comment)
async def set_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    if "id" not in data:
        raise KeyError("Worker bid id not exist")
    if "status" not in data:
        raise KeyError("Status not exist")
    await state.set_state(Base.none)

    id: int = data["id"]
    state: int = data["status"]
    await update_worker_bid_bot(
        bid_id=id,
        state=ApprovalStatus.approved if state == 1 else ApprovalStatus.denied,
        comment=message.text,
    )

    await try_delete_message(data["msg"])
    await try_delete_message(message)

    msg = await try_edit_or_answer(
        message=message, text=hbold("Успешно!"), return_message=True
    )
    await sleep(3)
    await try_delete_message(msg)
    await get_coordinate_worker_bid(message)
