from abc import abstractmethod

from common.contracts.clients.base import BaseClient
from common.schemas.token import TokenPayload


class SecurityClient(BaseClient):
    @abstractmethod
    def create_access_token(self, data: dict) -> str:
        """Creates access token with `data`."""

    @abstractmethod
    def parse_access_token(self, token: str) -> TokenPayload | None:
        """Parses access token.

        Returns:
            Token payload if it parse success, `None` otherwise.
        """
