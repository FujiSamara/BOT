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
    async def request_put_links(self, files, expiration=3600):
        if len(files) == 0:
            return []
        authorization_header = await self._auth_client.get_authorization_header()
        async with aiohttp.ClientSession() as session:
            json = [file.model_dump() for file in files]
            async with session.post(
                f"{self._url}/api/files/?expiration={expiration}",
                json=json,
                headers={"Authorization": authorization_header},
                ssl=self._with_ssl,
            ) as resp:
                if 400 <= resp.status < 500:
                    raise RuntimeError(
                        f"Put links requested with errors: {resp.reason}"
                    )

                body: dict = await resp.json()
                return [FileLinkSchema.model_validate(file) for file in body]

    @retry()
    async def request_get_links(self, ids, expiration=3600):
        if len(ids) == 0:
            return []
        authorization_header = await self._auth_client.get_authorization_header()
        async with aiohttp.ClientSession() as session:
            params = "&".join([f"ids={id}" for id in ids])
            async with session.get(
                f"{self._url}/api/files/?{params}&expiration={expiration}",
                headers={"Authorization": authorization_header},
                ssl=self._with_ssl,
            ) as resp:
                if 400 <= resp.status < 500:
                    raise RuntimeError(
                        f"Get links requested with errors: {resp.reason}"
                    )

                body: dict = await resp.json()
                return [FileLinkSchema.model_validate(file) for file in body]
