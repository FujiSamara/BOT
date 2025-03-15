from sqlalchemy.ext.asyncio import AsyncSession
from common.contracts.repository import BaseRepository


class SQLBaseRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
