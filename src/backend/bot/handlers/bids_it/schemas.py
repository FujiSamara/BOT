from enum import Enum
from aiogram.filters.callback_data import CallbackData


class BidITViewMode(str, Enum):
    full = 1
    state_only = 2
    full_with_deny = 3


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
