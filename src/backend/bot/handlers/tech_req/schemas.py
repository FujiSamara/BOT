from aiogram.filters.callback_data import CallbackData
from enum import Enum


class TechRequestStatus(Enum):
    CREATE = 1
    SHOW = 2
    DOCS = 3
    NONE = 4


class ShowRequestCallbackData(CallbackData, prefix="tech_req"):
    request_id: int
    end_point: str
    last_end_point: str | None = None
