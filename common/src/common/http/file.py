import aiohttp

from common.contracts.clients import RemoteFileClient
from common.http.retry import retry
from common.http.auth import AuthHTTPClient
from common.schemas.file import FileLinkSchema


class HTTPFileClient(RemoteFileClient):
    def __init__(
        self,
        auth_client: AuthHTTPClient,
        *,
        file_service_url: str,
        with_ssl: bool = True,
    ):
        self._url = file_service_url
        self._with_ssl = with_ssl
        self._auth_client = auth_client

    @retry()
    async def request_put_link(self, filename, key, size, expiration=3600):
        authorization_header = await self._auth_client.get_authorization_header()
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self._url}/api/file/?expiration={expiration}",
                json={filename: filename, key: key, size: size},
                headers={"Authorization": authorization_header},
                ssl=self._with_ssl,
            ) as resp:
                if resp.status != 200:
                    raise ValueError("Get link requested with error.")
                body: dict = await resp.json()

                return FileLinkSchema.model_validate(body)

    @retry()
    async def request_get_link(self, id, expiration=3600):
        authorization_header = await self._auth_client.get_authorization_header()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self._url}/api/file/{id}?expiration={expiration}",
                headers={"Authorization": authorization_header},
                ssl=self._with_ssl,
            ) as resp:
                if resp.status != 200:
                    raise ValueError("Get link requested with error.")
                body: dict = await resp.json()

                return FileLinkSchema.model_validate(body)
