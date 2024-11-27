from datetime import datetime, timedelta
from typing import Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import SecurityScopes
from jose import JWTError, jwt
from hashlib import sha256
from calendar import timegm

from pydantic import ValidationError

from app.api.auth.schemas import TokenData, User, UserWithScopes
from app.api.auth.permissions import _oauth2_schema, _to_auth_scope
from app.db.models import FujiScope
from settings import get_settings
from app.db import service


def encrypt_password(password: str) -> str:
    """Returns encrypted password by"""
    return sha256(password.encode()).hexdigest()


def authorize_user(username: str, password: str) -> Optional[UserWithScopes]:
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


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """Returns new access token with `data` and `expires_delta`."""
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, get_settings().secret_key, algorithm=get_settings().token_algorithm
    )
    return encoded_jwt


def create_access_link(scopes: list[Union[str, FujiScope]] = None) -> str:
    """Returns guest temprorary access link for specified `scopes`

    :param scopes: Needed accesses, consists `["authenticated"]`
    """
    if scopes is None:
        scopes = []

    scopes = [
        *(
            _to_auth_scope(scope) if isinstance(scope, FujiScope) else scope
            for scope in scopes
        ),
        "authenticated",
    ]

    access_token_expires = timedelta(minutes=get_settings().access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": "guest",
            "scopes": scopes,
        },
        expires_delta=access_token_expires,
    )

    link = get_settings().crm_addr

    return f"{link}/crm/guest?token={access_token}&token_type=bearer"


async def get_user(
    security_scopes: SecurityScopes, token: str = Depends(_oauth2_schema)
) -> UserWithScopes:
    """Validates user permissions.
    Returns instance of `User` if user has enough permissions for `security scopes`,
    throw `HTTPException` with `401` status code otherwise."""
    required_all_scopes: list[str] = [
        scope for scope in security_scopes.scopes if "|" not in scope
    ]
    required_any_scopes_groups: list[list[str]] = [
        scope.split("|") for scope in security_scopes.scopes if "|" in scope
    ]

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

    user: UserWithScopes

    if username == "guest":
        user = UserWithScopes(
            username="guest", full_name="guest", scopes=token_data.scopes
        )
    else:
        worker = service.get_worker_by_phone_number(username)
        if not worker:
            raise credentials_exception
        user = User(
            username=worker.phone_number,
            full_name=f"{worker.l_name} {worker.f_name}",
            scopes=token_data.scopes,
        )

    # For & scopes.
    if (
        required_all_scopes
        and not all(scope in token_data.scopes for scope in required_all_scopes)
        and "admin" not in token_data.scopes
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": authenticate_value},
        )

    # For | scopes.
    for any_group in required_any_scopes_groups:
        if (
            not any(scope in token_data.scopes for scope in any_group)
            and "admin" not in token_data.scopes
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user
