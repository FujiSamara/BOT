from fastapi import FastAPI, Security
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.adapters.input.api.auth.schemas import Token
from app.adapters.input.api.auth.authentication import authorize_user, refresh_token

from app.adapters.input.api.auth.schemas import User
from app.adapters.input.api.auth.authentication import get_user


def register_general_routes(auth: FastAPI):
    """Registers base auth routes"""

    auth.post("/token", response_model=Token)(login)
    auth.get("/")(check_auth)


async def check_auth(
    user: User = Security(get_user, scopes=["authenticated"]),
) -> Token:
    token = refresh_token(user.username)

    return {"access_token": token, "token_type": "bearer"}


async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    token = authorize_user(form_data.username, form_data.password)
    if not token:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    return {"access_token": token, "token_type": "bearer"}
