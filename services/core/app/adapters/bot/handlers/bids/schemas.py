from enum import Enum
from aiogram.filters.callback_data import CallbackData


class BidViewMode(str, Enum):
    full = 1
    state_only = 2
    full_with_approve = 3


class BidViewType(str, Enum):
    creation = 1
    coordination = 2


class BidCallbackData(CallbackData, prefix="bid"):
    id: int
    mode: BidViewMode
    type: BidViewType
    endpoint_name: str
    without_decline:int = 0


class ActionType(str, Enum):
    approving = 1
    declining = 2


class BidActionData(CallbackData, prefix="bid_action"):
    bid_id: int
    action: ActionType
    endpoint_name: str
