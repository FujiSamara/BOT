from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import SecurityScopes
from jose import JWTError, jwt
from hashlib import sha256
from calendar import timegm

from pydantic import ValidationError

from api.auth.schemas import TokenData, User, UserWithScopes
from api.auth.permissions import _oauth2_schema, _to_auth_scope
from settings import get_settings
from db import service


def encrypt_password(password: str) -> str:
    """Returns encrypted password by"""
    return sha256(password.encode()).hexdigest()


def _authenticate_user(username: str, password: str) -> Optional[UserWithScopes]:
    """Authenticates user by his `username` and `password`.

    Returns corresponding `User` if `username` and `password` correct,
    `None` otherwise."""
    worker = service.get_worker_by_phone_number(username)

    if (
        not worker
        or not worker.can_use_crm
        or not worker.password
        or encrypt_password(password) != worker.password
    ):
        return

    return UserWithScopes(
        username=worker.phone_number,
        full_name=f"{worker.l_name} {worker.f_name}",
        scopes=[_to_auth_scope(fuji_scope) for fuji_scope in worker.post.scopes],
    )


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
    if security_scopes.scopes:
        authenticate_value = f"Bearer scope='{security_scopes.scope_str}'"
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(
            token,
            get_settings().secret_key,
            algorithms=[get_settings().token_algorithm],
        )

        expire: datetime = payload.get("exp")
        if timegm(datetime.now().utctimetuple()) > expire:
            raise credentials_exception

        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception

    worker = service.get_worker_by_phone_number(username)
    if not worker:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes and "admin" not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return User(
        username=worker.phone_number, full_name=f"{worker.l_name} {worker.f_name}"
    )
