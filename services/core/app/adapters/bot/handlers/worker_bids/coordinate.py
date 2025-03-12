from asyncio import sleep
from typing import Any, Callable
from aiogram import Router, F
from app.adapters.bot.kb import (
    get_coordinate_worker_bids_SS_btn,
    get_coordinate_worker_bids_AS_btn,
    get_coordinate_worker_bids_iiko_btn,
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
    send_menu_by_scopes,
)
from app.adapters.bot.states import (
    Base,
    WorkerBidCoordination,
)
from app.adapters.bot.handlers.worker_bids.utils import (
    get_full_worker_bid_info,
    get_worker_pending_bids_btns,
)
from app.adapters.bot import text
from app.adapters.bot.handlers.worker_bids.schemas import (
    WorkerBidCallbackData,
    WorkerBidPagesCallbackData,
    BidViewMode,
)
from app.infra.database.models import ApprovalStatus, WorkerBid, ViewStatus

from app.services.worker_bid import (
    get_worker_bid_by_id,
    update_worker_bid_bot,
    add_worker_bids_documents_requests,
    update_view_state_worker_bid,
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
            callback_data=WorkerBidPagesCallbackData(
                page=0, state_name=self.name
            ).pack(),
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
            WorkerBidPagesCallbackData.filter(F.state_name == self.name),
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
        router.callback_query.register(
            self.download_all_docs,
            WorkerBidCallbackData.filter(
                F.endpoint_name == f"download_all_docs_{self.name}"
            ),
            WorkerBidCallbackData.filter(F.mode == BidViewMode.full_with_approve),
        )
        router.callback_query.register(
            self.seek_docs_accounting_service,
            WorkerBidCallbackData.filter(F.mode == BidViewMode.full_with_approve),
            WorkerBidCallbackData.filter(F.endpoint_name == f"seek_docs_{self.name}"),
        )

    async def get_menu(self, message: CallbackQuery | Message):
        if isinstance(message, CallbackQuery):
            message = message.message
        await try_edit_or_answer(
            message=message,
            text=hbold(self.coordinator_menu_button.text),
            reply_markup=self.coordinate_worker_bid_menu,
        )

    async def get_pending_worker_bids(
        self,
        message: CallbackQuery | Message,
        state: FSMContext,
        callback_data: WorkerBidPagesCallbackData | None = None,
    ):
        if isinstance(message, CallbackQuery):
            message = message.message
            await state.update_data(page=callback_data.page)
        else:
            callback_data = WorkerBidPagesCallbackData(
                (await state.get_data()).get("page") or 0, state_name=self.name
            )
        buttons = []
        get_worker_pending_bids_btns(
            state_column=self.state_column,
            buttons=buttons,
            name=self.name,
            page_callback_data=callback_data,
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
        await state.set_state(Base.none)
        data = await state.get_data()
        if "msgs" in data.keys():
            for msg in data["msgs"]:
                await try_delete_message(msg)

        bid = get_worker_bid_by_id(callback_data.id)
        if bid.view_state == ViewStatus.pending_approval:
            update_view_state_worker_bid(
                worker_bid_id=callback_data.id, state=ViewStatus.viewed
            )

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
                    text="Документы",
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
        buttons.append(
            InlineKeyboardButton(
                text="Скачать все документы",
                callback_data=WorkerBidCallbackData(
                    id=callback_data.id,
                    mode=callback_data.mode,
                    endpoint_name=f"download_all_docs_{self.name}",
                ).pack(),
            )
        )
        if getattr(bid, self.name + "_state") == ApprovalStatus.pending_approval:
            buttons.append(
                InlineKeyboardButton(
                    text="Согласовать",
                    callback_data=WorkerBidCallbackData(
                        id=callback_data.id,
                        mode=callback_data.mode,
                        endpoint_name=f"get_comment_{self.name}",
                        state=1,
                    ).pack(),
                )
            )
            buttons.append(
                InlineKeyboardButton(
                    text="Отказать",
                    callback_data=WorkerBidCallbackData(
                        id=callback_data.id,
                        mode=callback_data.mode,
                        endpoint_name=f"get_comment_{self.name}",
                        state=0,
                    ).pack(),
                ),
            )

        if self.state_column == WorkerBid.accounting_service_state:
            buttons.append(
                InlineKeyboardButton(
                    text="Запросить документы",
                    callback_data=WorkerBidCallbackData(
                        id=callback_data.id,
                        mode=callback_data.mode,
                        endpoint_name=f"seek_docs_{self.name}",
                    ).pack(),
                ),
            )

        buttons.append(
            InlineKeyboardButton(
                text=text.back,
                callback_data=self.get_pending_worker_bids_btn.callback_data,
            ),
        )
        await try_edit_or_answer(
            message=callback.message,
            text=get_full_worker_bid_info(bid),
            reply_markup=create_inline_keyboard(
                *buttons,
            ),
        )

    async def show_docs(
        self,
        callback: CallbackQuery,
        callback_data: WorkerBidCallbackData,
        state: FSMContext,
    ):
        bid = get_worker_bid_by_id(callback_data.id)
        msgs: list[Message] = []
        docs_len = len(getattr(bid, callback_data.doc_type))

        for iteration in range(docs_len // 10 + (1 if docs_len % 10 != 0 else 0)):
            media: list[InputMediaDocument] = []

            for photo in getattr(bid, callback_data.doc_type)[
                iteration * 10 : iteration * 10 + 9
            ]:
                media.append(
                    InputMediaDocument(
                        media=BufferedInputFile(
                            file=await photo.document.read(),
                            filename=photo.document.filename,
                        )
                    )
                )

            msgs += await callback.message.answer_media_group(
                media=media,
            )

        await try_delete_message(callback.message)
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
        if (
            callback_data.state == 0
            or self.state_column != WorkerBid.iiko_service_state
        ):
            comment_state = WorkerBidCoordination.comment_str
            t = "Введите комментарий:"
        else:
            comment_state = WorkerBidCoordination.comment_int
            t = "Введите табельный номер:"

        message = await try_edit_or_answer(
            callback.message,
            text=hbold(t),
            return_message=True,
            reply_markup=create_inline_keyboard(
                InlineKeyboardButton(
                    text="К заявке",
                    callback_data=WorkerBidCallbackData(
                        id=callback_data.id,
                        mode=BidViewMode.full_with_approve,
                        endpoint_name=f"get_pending_bid_{self.name}",
                    ).pack(),
                )
            ),
        )
        await state.update_data(
            msg=message, get_menu=self.get_menu, state_column_name=self.name
        )
        await state.set_state(comment_state)

    async def download_all_docs(
        self,
        callback: CallbackQuery,
        callback_data: WorkerBidCallbackData,
        state: FSMContext,
    ):
        from app.adapters.output.file.zip_file import ZipFileManager

        bid = get_worker_bid_by_id(callback_data.id)
        zip_manager = ZipFileManager(
            [*bid.passport, *bid.work_permission, *bid.worksheet],
        )
        await try_edit_or_answer(callback.message, text="Ожидайте.")

        media: list[InputMediaDocument] = [
            InputMediaDocument(
                media=BufferedInputFile(
                    file=zip_manager.create_zip(),
                    filename=f"Документы_{bid.l_name}_{bid.f_name[0]}_{bid.o_name[0] or 'о'}.zip",
                )
            )
        ]

        msgs = await callback.message.answer_media_group(media=media)
        await try_delete_message(callback.message)
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

    async def seek_docs_accounting_service(
        self,
        callback: CallbackQuery,
        callback_data: WorkerBidCallbackData,
        state: FSMContext,
    ):
        msg = await try_edit_or_answer(
            message=callback.message,
            text=hbold("Перечислите документы"),
            return_message=True,
            reply_markup=create_inline_keyboard(
                InlineKeyboardButton(
                    text=text.back,
                    callback_data=WorkerBidCallbackData(
                        id=callback_data.id,
                        mode=callback_data.mode,
                        endpoint_name=f"get_pending_bid_{self.name}",
                    ).pack(),
                )
            ),
        )
        await state.update_data(id=callback_data.id, msg=msg)

        await state.set_state(WorkerBidCoordination.seek_documents)


@router.message(
    WorkerBidCoordination.comment_str,
)
async def set_comment_str(message: Message, state: FSMContext):
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
    status: int = data["status"]
    await try_delete_message(message)
    state_column_name: str = data["state_column_name"]
    get_menu: Callable = data["get_menu"]
    await state.clear()

    if not await update_worker_bid_bot(
        bid_id=id,
        state_column_name=state_column_name,
        state=ApprovalStatus.approved if status == 1 else ApprovalStatus.denied,
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


@router.message(
    WorkerBidCoordination.comment_int,
)
async def set_comment_int(message: Message, state: FSMContext):
    data = await state.get_data()
    if "id" not in data:
        raise KeyError("Worker bid id not exist")
    if "status" not in data:
        raise KeyError("Status not exist")
    if "state_column_name" not in data:
        raise KeyError("State column name not exist")
    if "get_menu" not in data:
        raise KeyError("Generator not exist")

    await try_delete_message(message)
    await try_delete_message(data["msg"])

    id: int = data["id"]
    status: int = data["status"]
    state_column_name: str = data["state_column_name"]
    get_menu: Callable = data["get_menu"]
    await state.clear()

    try:
        iiko_id = int(message.text)

        if not await update_worker_bid_bot(
            bid_id=id,
            state_column_name=state_column_name,
            state=ApprovalStatus.approved if status == 1 else ApprovalStatus.denied,
            comment=iiko_id,
        ):
            msg = await try_edit_or_answer(
                message=message, text=text.err, return_message=True
            )
        else:
            msg = await try_edit_or_answer(
                message=message, text=hbold("Успешно!"), return_message=True
            )

        await state.set_state(Base.none)
        await sleep(3)
        await try_delete_message(msg)
        await get_menu(message)

    except ValueError:
        await state.set_state(WorkerBidCoordination.comment_int)
        await try_edit_or_answer(
            message=message,
            text=text.format_err,
            reply_markup=create_inline_keyboard(
                InlineKeyboardButton(
                    text="К заявке",
                    callback_data=WorkerBidCallbackData(
                        id=id,
                        mode=BidViewMode.full_with_approve,
                        endpoint_name=f"get_pending_bid_{state_column_name}",
                    ).pack(),
                )
            ),
        )


@router.message(WorkerBidCoordination.seek_documents)
async def set_docs_accounting_service(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.set_state(Base.none)
    await try_delete_message(message=message)
    if "msg" in data:
        await try_delete_message(message=data.get("msg"))
    bid_id = data.get("id")
    if bid_id is None:
        raise KeyError("Worker bid id not exist")
    await state.clear()

    if not await add_worker_bids_documents_requests(
        bid_id=bid_id,
        tg_id=message.chat.id,
        message=message.text,
    ):
        msg = await try_edit_or_answer(
            message=message, text=text.err, return_message=True
        )
        await send_menu_by_scopes(message=msg)
    else:
        update_view_state_worker_bid(worker_bid_id=bid_id, state=ViewStatus.pending)
        msg = await try_edit_or_answer(
            message=message, text="Успешно!", return_message=True
        )
        await try_delete_message(msg)
        await send_menu_by_scopes(message=message)


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
    WorkerBidCoordinationFactory(
        router=router,
        coordinator_menu_button=get_coordinate_worker_bids_iiko_btn,
        state_column=WorkerBid.iiko_service_state,
        name="iiko_service",
    )
