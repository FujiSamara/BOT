from fastapi.security import OAuth2PasswordBearer


_oauth2_schema = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"admin": "Full access"},
)
