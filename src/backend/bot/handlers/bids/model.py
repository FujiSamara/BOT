from enum import Enum
from aiogram.filters.callback_data import CallbackData

class BidViewMove(str, Enum):
    full = 1
    state_only = 2

class BidCallbackData(CallbackData, prefix="bid"):
    id: int
    mode: BidViewMove