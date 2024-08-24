from enum import Enum
from aiogram.filters.callback_data import CallbackData


class BidITViewMode(str, Enum):
    history = 1
    pending = 2
    deny = 3


class BidITCallbackData(CallbackData, prefix="bid_it"):
    id: int
    mode: BidITViewMode
    endpoint_name: str
