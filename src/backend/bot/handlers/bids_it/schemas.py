from enum import Enum
from aiogram.filters.callback_data import CallbackData


class BidITViewMode(str, Enum):
    full = 1
    state_only = 2
    full_with_approve = 3


class BidITViewType(str, Enum):
    creation = 1
    coordination = 2


class BidITCallbackData(CallbackData, prefix="bid_it"):
    id: int
    mode: BidITViewMode
    type: BidITViewType
    endpoint_name: str


class WorkerBidITCallbackData(CallbackData, prefix="worker_bid_it"):
    id: int
    endpoint_name: str


class ActionType(str, Enum):
    approving = 1
    declining = 2


class BidActionData(CallbackData, prefix="bid_it_action"):
    bid_id: int
    action: ActionType
    endpoint_name: str
