from typing import Optional
from aiogram.filters.callback_data import CallbackData


class ShowLoginCallbackData(CallbackData, prefix="pers_cab"):
    end_point: str
    login: Optional[str] = None
    service: Optional[str] = None
    inventory_number: Optional[str] = None
    department: Optional[str] = None


class ShowWorkTimeCallbackData(CallbackData, prefix="pers_cab"):
    end_point: str
    id: int | None = None
    page: int | None = None
