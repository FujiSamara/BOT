from aiogram import F, Router
from aiogram.types import CallbackQuery, BufferedInputFile, InputMediaDocument, Message
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext
import asyncio
from typing import Any, Callable
import app.adapters.bot.handlers.utils as utils

from app.adapters.bot.kb import (
    main_menu_button,
    create_inline_keyboard,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    fac_cc_menu_button,
    kru_menu_button,
    owner_menu_button,
    accountant_card_menu_button,
    accountant_cash_menu_button,
    teller_card_menu_button,
    teller_cash_menu_button,
)
from app.adapters.bot import text

from app.infra.database.models import Bid
from app.schemas import ApprovalStatus, BidSchema
from app.services import (
    get_pending_bids_by_column,
    get_pending_bids_for_teller_cash,
    get_pending_bids_for_cc_fac,
    get_history_bids_by_column,
    get_history_bids_for_teller_cash,
    get_history_bids_for_cc_fac,
    get_bid_by_id,
    update_bid_state,
    update_bid,
    get_departments_names,
    find_bid_for_worker,
)
from app.adapters.bot.handlers.bids.schemas import (
    BidCallbackData,
    BidViewMode,
    BidViewType,
    BidActionData,
    ActionType,
)
from app.adapters.bot.states import BidCoordination, Base
from app.adapters.bot.handlers.bids.utils import get_full_bid_info, get_bid_list_info
from app.adapters.bot.handlers.utils import (
    try_delete_message,
    try_edit_message,
    try_edit_or_answer,
    create_reply_keyboard,
)

router = Router(name="bid_coordination")


class CoordinationFactory:
    def __init__(
        self,
        router: Router,
        name: str,
        coordinator_menu_button: InlineKeyboardButton,
        state_column: Any,
        without_decline: bool = False,
        approve_button_text: str = "Согласовать",
        pending_text: str = "Ожидающие заявки",
    ):
        self.name = name
        self.coordinator_menu_button = coordinator_menu_button
        self.pending_button = InlineKeyboardButton(
            text=pending_text, callback_data=f"{name}_pending"
        )
        self.history_button = InlineKeyboardButton(
            text="История заявок", callback_data=f"{name}_history"
        )
        self.find_bid_button = InlineKeyboardButton(
            text="Найти заявку", callback_data=f"{name}_search"
        )
        self.approving_endpoint_name = f"{name}_approving"
        self.documents_endpoint_name = f"{name}_documents"
        self.without_decline = without_decline
        self.state_column = state_column
        self.approve_button_text = approve_button_text

        router.callback_query.register(
            self.get_menu, F.data == coordinator_menu_button.callback_data
        )
        router.callback_query.register(self.get_pendings, F.data == f"{name}_pending")
        router.callback_query.register(self.get_history, F.data == f"{name}_history")
        router.callback_query.register(
            self.get_bid,
            BidCallbackData.filter(F.type == BidViewType.coordination),
            BidCallbackData.filter(F.endpoint_name == self.name),
        )
        router.callback_query.register(
            self.get_documents,
            BidCallbackData.filter(F.type == BidViewType.coordination),
            BidCallbackData.filter(F.endpoint_name == self.documents_endpoint_name),
        )
        if state_column == Bid.accountant_cash_state:
            router.callback_query.register(
                self.approve_bid_accountant_cash,
                BidActionData.filter(F.action == ActionType.approving),
                BidActionData.filter(F.endpoint_name == self.approving_endpoint_name),
            )
        elif state_column == Bid.teller_card_state:
            router.callback_query.register(
                self.approve_bid_teller_card,
                BidActionData.filter(F.action == ActionType.approving),
                BidActionData.filter(F.endpoint_name == self.approving_endpoint_name),
            )
        else:
            router.callback_query.register(
                self.approve_bid,
                BidActionData.filter(F.action == ActionType.approving),
                BidActionData.filter(F.endpoint_name == self.approving_endpoint_name),
            )
        if not without_decline:
            self.declining_endpoint_name = f"{name}_declining"
            router.callback_query.register(
                self.decline_bid,
                BidActionData.filter(F.action == ActionType.declining),
                BidActionData.filter(F.endpoint_name == self.declining_endpoint_name),
            )
        router.callback_query.register(self.search_bid, F.data == f"{name}_search")

    async def get_menu(self, message: CallbackQuery | Message, state: FSMContext):
        if isinstance(message, CallbackQuery):
            message = message.message
        keyboard = create_inline_keyboard(
            self.pending_button,
            self.history_button,
            self.find_bid_button,
            main_menu_button,
        )

        message = await try_edit_or_answer(
            message=message,
            text=hbold("Заявки на согласования платежей"),
            reply_markup=keyboard,
            return_message=True,
        )

        await state.update_data(msg=message)

    async def decline_bid(
        self, callback: CallbackQuery, callback_data: BidActionData, state: FSMContext
    ):
        bid = get_bid_by_id(callback_data.bid_id)
        await try_edit_message(callback.message, hbold("Введите причину отказа:"))
        await state.set_state(BidCoordination.comment)
        await state.update_data(
            generator=self.get_pendings,
            callback=callback,
            bid=bid,
            column_name=self.state_column.name,
        )

    async def approve_bid(self, callback: CallbackQuery, callback_data: BidActionData):
        bid = get_bid_by_id(callback_data.bid_id)
        worker = utils.get_worker_my_message(callback)
        if worker is not None:
            if self.state_column == Bid.fac_state:
                match ApprovalStatus.pending_approval:
                    case bid.fac_state:
                        await update_bid_state(
                            bid,
                            Bid.fac_state.name,
                            ApprovalStatus.approved,
                            worker.id,
                        )
                    case bid.cc_state:
                        await update_bid_state(
                            bid,
                            Bid.cc_state.name,
                            ApprovalStatus.approved,
                            worker.id,
                        )
            else:
                await update_bid_state(
                    bid, self.state_column.name, ApprovalStatus.approved, worker.id
                )
        msg = await callback.message.answer(text="Успешно!")
        await asyncio.sleep(1)
        await msg.delete()
        await self.get_pendings(callback)

    async def approve_bid_accountant_cash(
        self,
        callback: CallbackQuery,
        callback_data: BidActionData,
        state: FSMContext,
    ):
        bid = get_bid_by_id(callback_data.bid_id)
        await state.update_data(
            generator=self.get_pendings,
            callback=callback,
            bid=bid,
            column_name=self.state_column.name,
        )
        await state.set_state(BidCoordination.department)
        await try_delete_message(callback.message)
        msg = await callback.message.answer(
            message=callback.message,
            text=hbold(
                f"Выберите предприятие на котором будут выданы деньги.\n Заявка с производства: {bid.department.name}."
            ),
            reply_markup=create_reply_keyboard(
                text.back,
                *[
                    department_name
                    for department_name in sorted(get_departments_names())
                ],
            ),
        )
        await state.update_data(msg=msg)

    async def approve_bid_teller_card(
        self,
        callback: CallbackQuery,
        callback_data: BidCallbackData,
        state: FSMContext,
    ):
        bid = get_bid_by_id(callback_data.bid_id)
        await state.update_data(
            generator=self.get_pendings,
            callback=callback,
            bid=bid,
            column_name=self.state_column.name,
        )
        await try_delete_message(callback.message)
        msg = await callback.message.answer(
            text=hbold("Введите комментарий:"),
            reply_markup=create_reply_keyboard(text.back),
        )

        await state.update_data(msg=msg)
        await state.set_state(BidCoordination.paying_comment)

    async def get_documents(
        self, callback: CallbackQuery, callback_data: BidCallbackData, state: FSMContext
    ):
        bid = get_bid_by_id(callback_data.id)
        media: list[InputMediaDocument] = []

        for document in bid.documents:
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
                    callback_data=BidCallbackData(
                        id=bid.id,
                        mode=callback_data.mode,
                        type=BidViewType.coordination,
                        endpoint_name=self.name,
                    ).pack(),
                )
            ),
        )

    async def get_bid(
        self,
        message: CallbackQuery | Message,
        callback_data: BidCallbackData,
        state: FSMContext,
    ):
        if isinstance(message, CallbackQuery):
            message = message.message
        bid = get_bid_by_id(callback_data.id)
        data = await state.get_data()
        if "msgs_for_delete" in data:
            for msg in data["msgs_for_delete"]:
                await try_delete_message(msg)
            await state.update_data(msgs_for_delete=[])

        caption = get_full_bid_info(bid)

        buttons = [
            self.pending_button,
            self.history_button,
            InlineKeyboardButton(
                text="Показать документы",
                callback_data=BidCallbackData(
                    id=bid.id,
                    mode=callback_data.mode,
                    type=BidViewType.coordination,
                    endpoint_name=self.documents_endpoint_name,
                ).pack(),
            ),
        ]
        condition = (
            getattr(bid, self.name + "_state") == ApprovalStatus.pending_approval
        )
        if self.name == "fac":
            condition = (
                getattr(bid, "fac_state") == ApprovalStatus.pending_approval
                or getattr(bid, "cc_state") == ApprovalStatus.pending_approval
            )
        if callback_data.mode == BidViewMode.full_with_approve and condition:
            buttons.append(
                InlineKeyboardButton(
                    text=self.approve_button_text,
                    callback_data=BidActionData(
                        bid_id=bid.id,
                        action=ActionType.approving,
                        endpoint_name=self.approving_endpoint_name,
                    ).pack(),
                )
            )
            if not self.without_decline:
                buttons.append(
                    InlineKeyboardButton(
                        text="Отказать",
                        callback_data=BidActionData(
                            bid_id=bid.id,
                            action=ActionType.declining,
                            endpoint_name=self.declining_endpoint_name,
                        ).pack(),
                    )
                )
        await try_edit_or_answer(
            message=message,
            text=caption,
            reply_markup=create_inline_keyboard(*buttons),
        )

    def get_specified_bids_keyboard(
        self, type: str, tg_id: int
    ) -> InlineKeyboardMarkup:
        bids = []
        if type == "pending":
            if self.state_column == Bid.teller_cash_state:
                bids = get_pending_bids_for_teller_cash(tg_id)
            elif self.state_column == Bid.fac_state:
                bids = get_pending_bids_for_cc_fac(tg_id)
            else:
                bids = get_pending_bids_by_column(self.state_column)
        else:
            if self.state_column == Bid.teller_cash_state:
                bids = get_history_bids_for_teller_cash(tg_id, 10)
            elif self.state_column == Bid.fac_state:
                bids = get_history_bids_for_cc_fac(tg_id, 10)
            else:
                bids = get_history_bids_by_column(self.state_column, 10)
        return create_inline_keyboard(
            *(
                InlineKeyboardButton(
                    text=get_bid_list_info(bid),
                    callback_data=BidCallbackData(
                        id=bid.id,
                        mode=BidViewMode.full
                        if type == "history"
                        else BidViewMode.full_with_approve,
                        type=BidViewType.coordination,
                        endpoint_name=self.name,
                    ).pack(),
                )
                for bid in bids
            ),
            self.coordinator_menu_button,
        )

    async def get_pendings(self, callback: CallbackQuery):
        keyboard = self.get_specified_bids_keyboard("pending", callback.message.chat.id)
        await try_delete_message(callback.message)

        await callback.message.answer("Ожидающие согласования:", reply_markup=keyboard)

    async def get_history(self, callback: CallbackQuery):
        keyboard = self.get_specified_bids_keyboard("history", callback.message.chat.id)
        await try_delete_message(callback.message)

        await callback.message.answer("История согласования:", reply_markup=keyboard)

    async def search_bid(self, message: CallbackQuery | Message, state: FSMContext):
        if isinstance(message, CallbackQuery):
            message = message.message
        await state.set_state(BidCoordination.search)
        await state.update_data(
            get_bid=self.get_bid,
            get_menu=self.get_menu,
            search_bid=self.search_bid,
            state_column=self.state_column,
            message=message,
        )

        data = await state.get_data()
        await try_delete_message(data["msg"])

        msg = await message.answer(
            message=message,
            text=hbold("Введите номер заявки:"),
            reply_markup=create_reply_keyboard(text.back),
        )
        await state.update_data(msg=msg)


@router.message(BidCoordination.comment)
async def set_comment_after_decline(message: Message, state: FSMContext):
    data = await state.get_data()
    if "generator" not in data:
        raise KeyError("Pending generator not exist")
    if "callback" not in data:
        raise KeyError("Callback not exist")
    if "bid" not in data:
        raise KeyError("Bid not exist")
    if "column_name" not in data:
        raise KeyError("Column name not exist")

    generator: Callable = data["generator"]
    callback: CallbackQuery = data["callback"]
    bid: BidSchema = data["bid"]
    column_name = data["column_name"]
    bid.denying_reason = message.text
    update_bid(bid)
    worker = utils.get_worker_my_message(callback)
    if worker is not None:
        await update_bid_state(bid, column_name, ApprovalStatus.denied, worker.id)

    await try_delete_message(message)
    await generator(callback)


@router.message(BidCoordination.department)
async def set_department(message: Message, state: FSMContext):
    data = await state.get_data()
    await try_delete_message(data["msg"])

    if "generator" not in data:
        raise KeyError("Pending generator not exist")
    if "callback" not in data:
        raise KeyError("Callback not exist")
    if "bid" not in data:
        raise KeyError("Bid not exist")
    if "column_name" not in data:
        raise KeyError("Column name not exist")

    generator: Callable = data["generator"]
    callback: CallbackQuery = data["callback"]
    bid: BidSchema = data["bid"]
    column_name = data["column_name"]

    await state.set_state(Base.none)
    if message.text == text.back:
        await try_delete_message(message)
        await CoordinationFactory(
            router=router,
            coordinator_menu_button=accountant_cash_menu_button,
            state_column=Bid.accountant_cash_state,
            name="accountant_cash",
        ).get_bid(
            callback=callback,
            callback_data=BidCallbackData(
                id=bid.id,
                mode=BidViewMode.full_with_approve,
                type=BidViewType.coordination,
                endpoint_name="accountant_cash",
            ),
            state=state,
        )
    elif message.text in get_departments_names():
        update_bid(bid, paying_department_name=message.text)
        bid = get_bid_by_id(bid.id)
        worker = utils.get_worker_my_message(callback)
        if worker is not None:
            await update_bid_state(bid, column_name, ApprovalStatus.approved, worker.id)

        await try_delete_message(message)

        msg = await message.answer(hbold("Успешно"))
        await asyncio.sleep(1)
        await try_delete_message(msg)

        await generator(callback)
    else:
        await try_delete_message(message)

        msg = await message.answer(hbold(text.format_err[:-1] + "."))
        await asyncio.sleep(3)
        await msg.delete()

        await state.update_data(
            generator=generator,
            callback=callback,
            bid=bid,
            column_name=column_name,
        )
        await state.set_state(BidCoordination.department)

        msg = await message.answer(
            text=hbold(
                f"\nВыберите предприятие на котором будут выданы деньги.\n Заявка с производства: {bid.department.name}."
            ),
            reply_markup=create_reply_keyboard(
                text.back,
                *[
                    department_name
                    for department_name in sorted(get_departments_names())
                ],
            ),
        )

        await state.update_data(msg=msg)


@router.message(BidCoordination.paying_comment)
async def set_paying_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    await try_delete_message(data["msg"])

    if "generator" not in data:
        raise KeyError("Pending generator not exist")
    if "callback" not in data:
        raise KeyError("Callback not exist")
    if "bid" not in data:
        raise KeyError("Bid not exist")
    if "column_name" not in data:
        raise KeyError("Column name not exist")

    await state.set_state(Base.none)

    generator: Callable = data["generator"]
    callback: CallbackQuery = data["callback"]
    bid: BidSchema = data["bid"]
    column_name = data["column_name"]

    if message.text == text.back:
        await generator(callback)
        await state.set_state()
    else:
        bid.paying_comment = message.text
        update_bid(bid)
        bid = get_bid_by_id(bid.id)
        worker = utils.get_worker_my_message(callback)
        if worker is not None:
            await update_bid_state(bid, column_name, ApprovalStatus.approved, worker.id)

        msg = await message.answer(hbold("Успешно"))
        await asyncio.sleep(1)
        await try_delete_message(msg)
        await generator(callback)


@router.message(BidCoordination.search)
async def set_bid(message: Message, state: FSMContext):
    data = await state.get_data()
    await try_delete_message(message)
    await try_delete_message(data["msg"])

    await state.set_state(Base.none)
    get_menu: Callable = data["get_menu"]

    if message.text == text.back:
        await get_menu(message, state)
    else:
        try:
            msg_text = int(message.text)
            state_column = data["state_column"].name
            bid_with_access = find_bid_for_worker(msg_text, message.chat.id)
            if bid_with_access is None:
                msg = await message.answer(text=hbold("Заявка не найдена!"))
                await asyncio.sleep(2)
                search_bid: Callable = data["search_bid"]
                await search_bid(message, state)
                await msg.delete()

            elif not bid_with_access[1]:
                msg = await message.answer(
                    text=hbold("У Вас нет доступа к этой заявке!")
                )
                await asyncio.sleep(2)
                search_bid: Callable = data["search_bid"]
                await search_bid(message, state)
                await msg.delete()

            else:
                msg = await message.answer("Успешно!")
                await asyncio.sleep(1)

                get_bid: Callable = data["get_bid"]
                await get_bid(
                    message,
                    BidCallbackData(
                        id=bid_with_access[0].id,
                        mode=BidViewMode.full_with_approve
                        if getattr(bid_with_access[0], state_column)
                        == ApprovalStatus.pending_approval
                        else BidViewMode.full,
                        type=BidViewType.coordination,
                        endpoint_name=state_column.split("_state")[0],
                    ),
                    state,
                )
                await msg.delete()

        except ValueError:
            await try_delete_message(message)
            msg = await message.answer(hbold(text.format_err))

            search_bid: Callable = data["search_bid"]
            await asyncio.sleep(2)
            await search_bid(message, state)
            await msg.delete()


def build_coordinations():
    CoordinationFactory(
        router=router,
        coordinator_menu_button=fac_cc_menu_button,
        state_column=Bid.fac_state,
        name="fac",
        pending_text="На согласование",
    )
    CoordinationFactory(
        router=router,
        coordinator_menu_button=kru_menu_button,
        state_column=Bid.kru_state,
        name="kru",
    )
    CoordinationFactory(
        router=router,
        coordinator_menu_button=owner_menu_button,
        state_column=Bid.owner_state,
        name="owner",
    )
    CoordinationFactory(
        router=router,
        coordinator_menu_button=accountant_card_menu_button,
        state_column=Bid.accountant_card_state,
        name="accountant_card",
    )
    CoordinationFactory(
        router=router,
        coordinator_menu_button=accountant_cash_menu_button,
        state_column=Bid.accountant_cash_state,
        name="accountant_cash",
    )
    CoordinationFactory(
        router=router,
        coordinator_menu_button=teller_card_menu_button,
        state_column=Bid.teller_card_state,
        name="teller_card",
        without_decline=True,
        approve_button_text="Оплатить",
    )
    CoordinationFactory(
        router=router,
        coordinator_menu_button=teller_cash_menu_button,
        state_column=Bid.teller_cash_state,
        name="teller_cash",
        without_decline=True,
        approve_button_text="Выдать",
    )
