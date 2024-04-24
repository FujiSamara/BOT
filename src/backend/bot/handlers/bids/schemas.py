from enum import Enum
from aiogram.filters.callback_data import CallbackData

class BidViewMode(str, Enum):
    full = 1
    state_only = 2

class BidViewType(str, Enum):
    creation = 1
    coordination = 2

class BidCallbackData(CallbackData, prefix="bid"):
    id: int
    mode: BidViewMode
    type: BidViewType