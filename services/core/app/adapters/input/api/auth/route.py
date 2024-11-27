from fastapi import FastAPI, Security
from datetime import timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api.auth.schemas import Token
from app.api.auth.authentication import authorize_user, create_access_token

from app.infra.config import settings

from app.api.auth.schemas import User
from app.api.auth.authentication import get_user


def register_general_routes(auth: FastAPI):
    """Registers base auth routes"""

    auth.post("/token", response_model=Token)(login)
    auth.get("/")(check_auth)


async def check_auth(_: User = Security(get_user, scopes=["authenticated"])):
    return


async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = authorize_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "scopes": [
                *user.scopes,
                "authenticated",
                "file_all",
            ],
        },
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}
