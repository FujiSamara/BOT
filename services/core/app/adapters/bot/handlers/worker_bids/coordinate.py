from asyncio import sleep
from typing import Any, Callable
from aiogram import Router, F
from app.adapters.bot.kb import (
    get_coordinate_worker_bids_SS_btn,
    get_coordinate_worker_bids_AS_btn,
    main_menu_button,
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
from app.infra.database.models import ApprovalStatus, WorkerBid

from app.services import (
    get_pending_approval_bids,
    get_worker_bid_by_id,
    update_worker_bid_bot,
)

router = Router(name="coordinate_worker_bid")


class WorkerBidCoordinationFactory:
    def __init__(
        self,
        router: Router,
        name: str,
        coordinator_menu_button: InlineKeyboardButton,
        state_column: Any,
        approve_button_text: str = "Согласовать",
        pending_text: str = "Ожидающие заявки",
    ):
        self.router = router
        self.name = name
        self.coordinator_menu_button = coordinator_menu_button
        self.state_column = state_column
        self.approve_button_text = approve_button_text
        self.pending_text = pending_text
        self.get_pending_worker_bids_btn = InlineKeyboardButton(
            text="Ожидающие заявки",
            callback_data=f"get_pending_coordinate_worker_bids_{self.name}",
        )
        self.coordinate_worker_bid_menu = create_inline_keyboard(
            self.get_pending_worker_bids_btn,
            main_menu_button,
        )
        router.callback_query.register(
            self.get_menu,
            F.data == coordinator_menu_button.callback_data,
        )
        router.callback_query.register(
            self.get_pending_worker_bids,
            F.data == self.get_pending_worker_bids_btn.callback_data,
        )
        router.callback_query.register(
            self.get_pending_bid,
            WorkerBidCallbackData.filter(
                F.endpoint_name == f"get_pending_bid_{self.name}",
            ),
            WorkerBidCallbackData.filter(
                F.mode == BidViewMode.full_with_approve,
            ),
        )
        router.callback_query.register(
            self.show_docs,
            WorkerBidCallbackData.filter(F.endpoint_name == f"show_docs_{self.name}"),
        )
        router.callback_query.register(
            self.get_comment,
            WorkerBidCallbackData.filter(F.endpoint_name == f"get_comment_{self.name}"),
            WorkerBidCallbackData.filter(F.mode == BidViewMode.full_with_approve),
        )

    async def get_menu(self, message: CallbackQuery | Message):
        if isinstance(message, CallbackQuery):
            message = message.message
        await try_edit_or_answer(
            message=message,
            text=hbold(self.coordinator_menu_button.text),
            reply_markup=self.coordinate_worker_bid_menu,
        )

    async def get_pending_worker_bids(self, message: CallbackQuery | Message):
        if isinstance(message, CallbackQuery):
            message = message.message
        bids = get_pending_approval_bids(self.state_column) or []
        buttons = []
        for bid in bids:
            buttons.append(
                InlineKeyboardButton(
                    text=f"{bid.id} {bid.l_name} {bid.f_name[0]} {bid.o_name[0]} {bid.post.name}",
                    callback_data=WorkerBidCallbackData(
                        id=bid.id,
                        mode=BidViewMode.full_with_approve,
                        endpoint_name=f"get_pending_bid_{self.name}",
                    ).pack(),
                )
            )
        buttons.append(
            InlineKeyboardButton(
                text=text.back,
                callback_data=self.coordinator_menu_button.callback_data,
            ),
        )
        await try_edit_or_answer(
            message=message,
            text=hbold(self.get_pending_worker_bids_btn.text),
            reply_markup=create_inline_keyboard(
                *buttons,
            ),
        )

    async def get_pending_bid(
        self,
        callback: CallbackQuery,
        callback_data: WorkerBidCallbackData,
        state: FSMContext,
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
                        endpoint_name=f"show_docs_{self.name}",
                        doc_type="worksheet",
                    ).pack(),
                )
            )
        if bid.passport != []:
            buttons.append(
                InlineKeyboardButton(
                    text="Паспорт",
                    callback_data=WorkerBidCallbackData(
                        id=callback_data.id,
                        mode=callback_data.mode,
                        endpoint_name=f"show_docs_{self.name}",
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
                        endpoint_name=f"show_docs_{self.name}",
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
                        endpoint_name=f"get_comment_{self.name}",
                        state=1,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="Отказать",
                    callback_data=WorkerBidCallbackData(
                        id=callback_data.id,
                        mode=callback_data.mode,
                        endpoint_name=f"get_comment_{self.name}",
                        state=0,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text=text.back,
                    callback_data=self.coordinator_menu_button.callback_data,
                ),
            ),
        )

    async def show_docs(
        self,
        callback: CallbackQuery,
        callback_data: WorkerBidCallbackData,
        state: FSMContext,
    ):
        bid = get_worker_bid_by_id(callback_data.id)
        media: list[InputMediaDocument] = []
        for photo in getattr(bid, callback_data.doc_type):
            media.append(
                InputMediaDocument(
                    media=BufferedInputFile(
                        file=await photo.document.read(),
                        filename=photo.document.filename,
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
                        endpoint_name=f"get_pending_bid_{self.name}",
                    ).pack(),
                ),
            ),
        )

    async def get_comment(
        self,
        callback: CallbackQuery,
        callback_data: WorkerBidCallbackData,
        state: FSMContext,
    ):
        await state.update_data(id=callback_data.id, status=callback_data.state)
        message = await try_edit_or_answer(
            callback.message, text=hbold("Введите комментарий:"), return_message=True
        )
        await state.update_data(
            msg=message, get_menu=self.get_menu, state_column_name=self.name
        )
        await state.set_state(WorkerBidCoordination.comment)


@router.message(
    WorkerBidCoordination.comment,
)
async def set_comment(message: Message, state: FSMContext):
    # Save approval status
    data = await state.get_data()
    if "id" not in data:
        raise KeyError("Worker bid id not exist")
    if "status" not in data:
        raise KeyError("Status not exist")
    if "state_column_name" not in data:
        raise KeyError("State column name not exist")
    if "get_menu" not in data:
        raise KeyError("Generator not exist")
    await state.set_state(Base.none)

    id: int = data["id"]
    state: int = data["status"]
    await try_delete_message(message)
    state_column_name: str = data["state_column_name"]
    get_menu: Callable = data["get_menu"]

    if not await update_worker_bid_bot(
        bid_id=id,
        state_column_name=state_column_name,
        state=ApprovalStatus.approved if state == 1 else ApprovalStatus.denied,
        comment=message.text,
    ):
        msg = await try_edit_or_answer(
            message=message, text=text.err, return_message=True
        )
    else:
        msg = await try_edit_or_answer(
            message=message, text=hbold("Успешно!"), return_message=True
        )
    await try_delete_message(data["msg"])
    await sleep(3)
    await try_delete_message(msg)
    await get_menu(message)


def build_coordinations():
    WorkerBidCoordinationFactory(
        router=router,
        coordinator_menu_button=get_coordinate_worker_bids_SS_btn,
        state_column=WorkerBid.security_service_state,
        name="security_service",
    )
    WorkerBidCoordinationFactory(
        router=router,
        coordinator_menu_button=get_coordinate_worker_bids_AS_btn,
        state_column=WorkerBid.accounting_service_state,
        name="accounting_service",
    )
