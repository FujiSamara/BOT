from fastapi import FastAPI, Security
from datetime import timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from api.auth.schemas import Token
from api.auth.authentication import _authenticate_user, _create_access_token

from settings import get_settings

from api.auth.schemas import User
from api.auth.authentication import get_current_user


def configure(auth: FastAPI):
    """Configure fast api auth app."""

    auth.post("/token", response_model=Token)(login)
    auth.get("/")(check_auth)


async def check_auth(_: User = Security(get_current_user, scopes=["authenticated"])):
    return


async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = _authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=get_settings().access_token_expire_minutes)
    access_token = _create_access_token(
        data={"sub": user.username, "scopes": ["admin"]},  # TODO: Access refactoring
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}
