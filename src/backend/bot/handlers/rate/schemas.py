from typing import Optional
from aiogram.filters.callback_data import CallbackData
from enum import Enum


class RateFormStatus(str, Enum):
    RATING = 1
    FINE = 2
    NONE = 3


class RateShiftCallbackData(CallbackData, prefix="rate_shift"):
    day: str
    record_id: int
    rating: Optional[int] = 0
    fine: Optional[int] = 0
    form_status: RateFormStatus = RateFormStatus.NONE
