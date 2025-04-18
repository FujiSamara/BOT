from typing import Optional
from aiogram.filters.callback_data import CallbackData
from enum import Enum


class RequestType(Enum):
    TR = 1  # Technical
    CR = 2  # Cleaning


class ShowRequestCallbackData(CallbackData, prefix="dep_req"):
    request_id: int
    end_point: str
    last_end_point: Optional[str] = None
    req_type: int | None = None


class PageCallbackData(CallbackData, prefix="dep_req_page"):
    page: int = 0
    requests_endpoint: str | None = None
