from aiogram import F, Router
from aiogram.types import CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from typing import Any

from bot.kb import (
    main_menu_button,
    create_inline_keyboard,
    InlineKeyboardButton,
    kru_menu_button
)

from db.models import Bid
from db.service import (
    get_kru_pending_bids,
    get_bid_by_id
)
from bot.handlers.bids.schemas import BidCallbackData, BidViewMode, BidViewType, BidActionData, ActionType
from bot.handlers.bids.utils import get_full_bid_info

router = Router(name="bid_coordination")

class CoordinationFactory():

    def __init__(
            self,
            router: Router,
            name: str,
            coordinator_menu_button: InlineKeyboardButton,
            state_column: Any,
        ):
        
        self.name = name
        self.coordinator_menu_button = coordinator_menu_button
        self.pending_button = InlineKeyboardButton(text="Ожидающие заявки", callback_data=f"{name}_pending")
        self.history_button = InlineKeyboardButton(text="История заявок", callback_data=f"{name}_history")
        self.approving_endpoint_name = f"{name}_approving"
        self.declining_endpoint_name = f"{name}_declining"
        self.decline_button = InlineKeyboardButton(text="Отказать", callback_data=f"{name}_decline")

        router.callback_query.register(self.get_menu, F.data == coordinator_menu_button.callback_data)
        router.callback_query.register(self.get_pendings, F.data == f"{name}_pending")
        router.callback_query.register(
            self.get_bid,
            BidCallbackData.filter(F.type == BidViewType.coordination)
        )
        router.callback_query.register(
            self.approve_bid,
            BidActionData.filter(F.action == ActionType.approving),
            BidActionData.filter(F.endpoint_name == self.approving_endpoint_name)
        )

    async def get_menu(self, callback: CallbackQuery):
        keyboard = create_inline_keyboard(
            self.pending_button,
            main_menu_button
        )

        await callback.message.edit_text(text="Добро пожаловать!", reply_markup=keyboard)

    async def approve_bid(self, callback: CallbackQuery, callback_data: BidActionData):
        data = callback_data.bid_id
        pass

    async def get_bid(self, callback: CallbackQuery, callback_data: BidCallbackData):
        bid = get_bid_by_id(callback_data.id)
        await callback.message.delete()
        document = BufferedInputFile(file=bid.document.file.read(), filename=bid.document.filename)

        caption = get_full_bid_info(bid)

        buttons = [self.pending_button, self.history_button]

        if callback_data.mode == BidViewMode.full_with_approve:
            buttons.append(
                InlineKeyboardButton(
                    text="Согласовать",
                    callback_data=BidActionData(
                        bid_id=bid.id,
                        action=ActionType.approving,
                        endpoint_name=self.approving_endpoint_name
                    ).pack()
                )
            )
            buttons.append(self.decline_button)

        await callback.message.answer_document(
            document=document,
            caption=caption,
            reply_markup=create_inline_keyboard(*buttons)
        )

    async def get_pendings(self, callback: CallbackQuery):
        bids = get_kru_pending_bids()
        keyboard = create_inline_keyboard(
            *(InlineKeyboardButton(
                text=f"Заявка от {bid.create_date.date()} на cумму {bid.amount}",
                callback_data=BidCallbackData(
                    id=bid.id,
                    mode=BidViewMode.full_with_approve,
                    type=BidViewType.coordination
                ).pack()
            ) for bid in bids),
            self.coordinator_menu_button
        )
        await callback.message.delete()
        await callback.message.answer("Ожидающие согласования:", reply_markup=keyboard)

    async def get_history(self, callback: CallbackQuery):
        pass




def build_coordinations():
    kru_factory = CoordinationFactory(
        router=router,
        coordinator_menu_button=kru_menu_button,
        state_column=Bid.kru_state,
        name="kru"
    )