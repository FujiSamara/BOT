from aiogram.filters.callback_data import CallbackData


class IncidentCallbackData(CallbackData, prefix="incident"):
    id: int
    with_confirm: bool
    callback_from: str


class ConfirmIncidentCallbackData(CallbackData, prefix="incident_confirm"):
    id: int
