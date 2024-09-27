from enum import Enum
from aiogram.filters.callback_data import CallbackData


class ActionType(str, Enum):
    approving = 1
    declining = 2


class DismissalActionData(CallbackData, prefix="dismissal_action"):
    dismissal_id: int
    action: ActionType
    endpoint_name: str


class DismissalCallbackData(CallbackData, prefix="dismissal"):
    id: int
    endpoint_name: str
