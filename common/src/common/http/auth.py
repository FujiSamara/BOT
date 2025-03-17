import aiohttp

from common.contracts.clients import BaseClient
from common.contracts.services import AuthService
from common.schemas.token import TokenPayload
from common.auth import expired
from common.http.retry import retry


class AuthHTTPClient(BaseClient):
    def __init__(
        self,
        auth_service: AuthService,
        *,
        auth_url: str,
        client_id: str,
        client_secret: str,
        with_ssl: bool = True,
    ):
        self._payload: TokenPayload | None = None
        self._token_type: str | None = None
        self._token: str | None = None
        self._auth_url = auth_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._auth_service = auth_service
        self._with_ssl = with_ssl

    async def get_authorization_header(self) -> str:
        if self._payload is None or expired(self._payload):
            await self._update_token()

        return f"{self._token_type} {self._token}"

    @retry()
    async def _update_token(self):
        async with aiohttp.ClientSession() as session:
            mp = aiohttp.FormData()
            mp.add_field("username", self._client_id)
            mp.add_field("password", self._client_secret)

            async with session.post(
                f"{self._auth_url}/api/auth/token/",
                data=mp,
                ssl=self._with_ssl,
            ) as resp:
                if resp.status != 200:
                    raise ValueError("Token requested with error.")
                body: dict = await resp.json()
                self._token = body.get("access_token")
                self._token_type: str = body.get("token_type")
                self._token_type = self._token_type.capitalize()
                self._payload = await self._auth_service.introspect(self._token)
                if self._payload is None:
                    raise ValueError("Token created with error.")
