from aiogram.filters.callback_data import CallbackData
from enum import Enum


class BidViewMode(str, Enum):
    full = 1
    state_only = 2
    full_with_approve = 3


class WorkerBidCallbackData(CallbackData, prefix="worker_bid"):
    id: int
    mode: BidViewMode
    endpoint_name: str
    doc_type: str = "0"
    state: int | None = None
