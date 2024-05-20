from aiogram import F, Router
from aiogram.types import CallbackQuery, BufferedInputFile, InputMediaDocument
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext
import asyncio
from typing import Any

from bot.kb import (
    main_menu_button,
    create_inline_keyboard,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    kru_menu_button,
    owner_menu_button,
    accountant_card_menu_button,
    accountant_cash_menu_button,
    teller_card_menu_button,
    teller_cash_menu_button,
)

from db.models import Bid
from db.schemas import ApprovalStatus
from db.service import (
    get_pending_bids_by_column,
    get_history_bids_by_column,
    get_bid_by_id,
    update_bid_state,
)
from bot.handlers.bids.schemas import (
    BidCallbackData,
    BidViewMode,
    BidViewType,
    BidActionData,
    ActionType,
)
from bot.handlers.bids.utils import get_full_bid_info, get_bid_list_info
from bot.handlers.utils import try_delete_message, try_edit_message

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
    ):
        self.name = name
        self.coordinator_menu_button = coordinator_menu_button
        self.pending_button = InlineKeyboardButton(
            text="Ожидающие заявки", callback_data=f"{name}_pending"
        )
        self.history_button = InlineKeyboardButton(
            text="История заявок", callback_data=f"{name}_history"
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

    async def get_menu(self, callback: CallbackQuery):
        keyboard = create_inline_keyboard(
            self.pending_button, self.history_button, main_menu_button
        )

        await try_edit_message(
            message=callback.message,
            text="Согласование платежей",
            reply_markup=keyboard,
        )

    async def decline_bid(self, callback: CallbackQuery, callback_data: BidActionData):
        bid = get_bid_by_id(callback_data.bid_id)
        await update_bid_state(bid, self.state_column.name, ApprovalStatus.denied)
        msg = await callback.message.answer(text="Успешно!")
        await asyncio.sleep(1)
        await msg.delete()
        await self.get_pendings(callback)

    async def approve_bid(self, callback: CallbackQuery, callback_data: BidActionData):
        bid = get_bid_by_id(callback_data.bid_id)
        await update_bid_state(bid, self.state_column.name, ApprovalStatus.approved)
        msg = await callback.message.answer(text="Успешно!")
        await asyncio.sleep(1)
        await msg.delete()
        await self.get_pendings(callback)

    async def get_documents(
        self, callback: CallbackQuery, callback_data: BidCallbackData, state: FSMContext
    ):
        bid = get_bid_by_id(callback_data.id)
        media: list[InputMediaDocument] = [
            InputMediaDocument(
                media=BufferedInputFile(
                    file=bid.document.file.read(), filename=bid.document.filename
                ),
            )
        ]
        if bid.document1:
            media.append(
                InputMediaDocument(
                    media=BufferedInputFile(
                        file=bid.document1.file.read(), filename=bid.document1.filename
                    )
                )
            )
        if bid.document2:
            media.append(
                InputMediaDocument(
                    media=BufferedInputFile(
                        file=bid.document2.file.read(), filename=bid.document2.filename
                    )
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
        self, callback: CallbackQuery, callback_data: BidCallbackData, state: FSMContext
    ):
        bid = get_bid_by_id(callback_data.id)
        await try_delete_message(callback.message)
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

        if callback_data.mode == BidViewMode.full_with_approve:
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
        await callback.message.answer(
            text=caption, reply_markup=create_inline_keyboard(*buttons)
        )

    def get_specified_bids_keyboard(self, type: str) -> InlineKeyboardMarkup:
        bids = []
        if type == "pending":
            bids = get_pending_bids_by_column(self.state_column)
        else:
            bids = get_history_bids_by_column(self.state_column)
        bids = sorted(bids, key=lambda bid: bid.create_date, reverse=True)[:10]
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
        keyboard = self.get_specified_bids_keyboard("pending")
        await try_delete_message(callback.message)

        await callback.message.answer("Ожидающие согласования:", reply_markup=keyboard)

    async def get_history(self, callback: CallbackQuery):
        keyboard = self.get_specified_bids_keyboard("history")
        await try_delete_message(callback.message)

        await callback.message.answer("История согласования:", reply_markup=keyboard)


def build_coordinations():
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
        approve_button_text="Выдать",
    )
    CoordinationFactory(
        router=router,
        coordinator_menu_button=teller_cash_menu_button,
        state_column=Bid.teller_cash_state,
        name="teller_cash",
        without_decline=True,
        approve_button_text="Выдать",
    )
