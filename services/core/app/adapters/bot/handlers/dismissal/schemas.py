from enum import Enum
from aiogram.filters.callback_data import CallbackData


class ActionType(str, Enum):
    approving = 1
    declining = 2


class DismissalCallbackData(CallbackData, prefix="dismissal"):
    id: int
    endpoint_name: str
    action: ActionType | None = None
