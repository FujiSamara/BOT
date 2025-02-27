from common.contracts.services import AuthService
from common.contracts.clients import SecurityClient
from common.schemas.client_credential import ClientCredentials


class LocalAuthService(AuthService):
    def __init__(self, security_client: SecurityClient):
        self.security_client = security_client

        self._cached_credentials: dict[str, ClientCredentials] = {}

    async def process_update(self, credentials: ClientCredentials):
        """Processes scopes updates."""
        self._cached_credentials[credentials.external_client_id] = credentials

    async def introspect(self, token):
        payload = self.security_client.parse_access_token(token)

        if payload.external_client_id in self._cached_credentials:
            payload.scopes = self._cached_credentials[payload.external_client_id].scopes

        return payload
