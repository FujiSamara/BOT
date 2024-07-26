from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends
from fastapi.security import SecurityScopes
from jose import jwt

from api.auth.schemas import User
from api.auth.permissions import _oauth2_schema
from settings import get_settings


def _authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticates user by his `username` and `password`.

    Returns corresponding `User` if `username` and `password` correct,
    `None` otherwise."""
    return None


def _create_access_token(data: dict, expires_delta: timedelta) -> str:
    """Returns new access token with `data` and `expires_delta`."""
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, get_settings().secret_key, algorithm=get_settings().token_algorithm
    )
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes, token: str = Depends(_oauth2_schema)
) -> User:
    """Validates user permissions.
    Returns instance of `User` if user has enough permissions for `security scopes`,
    throw `HTTPException` with `401` status code otherwise."""
