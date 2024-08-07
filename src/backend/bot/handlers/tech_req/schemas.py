from aiogram.filters.callback_data import CallbackData


class ShowRequestCallbackData(CallbackData, prefix="tech_req"):
    request_id: int
    end_point: str
    last_end_point: str | None = None
