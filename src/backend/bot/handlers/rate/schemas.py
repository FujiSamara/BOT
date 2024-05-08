from aiogram.filters.callback_data import CallbackData
from datetime import date
from enum import Enum


class RateFormStatus(str, Enum):
    RATING = 1
    FINE = 2
    NONE = 3


class RateShiftCallbackData(CallbackData, prefix="rate_shift"):
    day: date
    record_id: int
    rating: int = 0
    fine: int = 0
    form_status: RateFormStatus = RateFormStatus.NONE
