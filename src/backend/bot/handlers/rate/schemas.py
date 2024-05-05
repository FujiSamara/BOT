from aiogram.filters.callback_data import CallbackData
from datetime import date


class RateShiftCallbackData(CallbackData, prefix="rate_shift"):
    day: date
    worker_id: int
