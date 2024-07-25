from datetime import timedelta
from typing import Optional
from fastapi import Depends
from fastapi.security import SecurityScopes

from api.auth.schemas import User
from api.auth.permissions import _oauth2_schema


def _authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticates user by his `username` and `password`.

    Returns corresponding `User` if `username` and `password` correct,
    `None` otherwise."""
    return None


def _create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Returns new access token with `data` and `expires_delta`."""
    return ""


async def get_current_user(
    security_scopes: SecurityScopes, token: str = Depends(_oauth2_schema)
):
    """Validates user permissions.
    Returns instance of `User` if user has enough permissions for `security scopes`,
    throw `HTTPException` with `401` status code otherwise."""
