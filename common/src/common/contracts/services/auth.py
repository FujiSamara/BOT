from abc import abstractmethod

from common.contracts.services.base import BaseService
from common.schemas.token import TokenPayload


class AuthService(BaseService):
    @abstractmethod
    async def introspect(self, token: str) -> TokenPayload | None:
        """Introspects `token`.

        Returns:
            Token payload with token introspection
            if client authenticated, `None` otherwise.
        """
