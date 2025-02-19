from aiogram.filters.callback_data import CallbackData
from enum import Enum
from app.adapters.bot.kb import get_candidates_coordinate_menu_btn


class BidViewMode(str, Enum):
    full = 1
    state_only = 2
    full_with_approve = 3
    full_with_update = 4


class WorkerBidCallbackData(CallbackData, prefix="worker_bid"):
    id: int
    mode: BidViewMode
    endpoint_name: str
    doc_type: str = "0"
    page: int = 0
    state: int | None = None


class WorkerBidPagesCallbackData(CallbackData, prefix="worker_bid_pages"):
    page: int = 0
    state_name: str


class CandidatesCoordinationCallbackData(CallbackData, prefix="worker_coordination"):
    id: int | None = None
    page: int = 0
    endpoint_name: str = get_candidates_coordinate_menu_btn.callback_data
