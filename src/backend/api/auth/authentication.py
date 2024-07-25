from datetime import timedelta
from typing import Optional

from api.auth.schemas import User


def _authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticates user by his `username` and `password`
    Returns corresponding `User` if `username` and `password` correct,
    `None` otherwise."""
    return None


def _create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Returns new access token with `data` and `expires_delta`."""
    return ""
