from sqlalchemy import select
from sqlalchemy.orm import selectinload

from common.sql.repository import SQLBaseRepository
from app.contracts.repositories import CardRepository
from app.infra.database.knowledge import converters
from app.infra.database.knowledge.models import BusinessCard


class SQLCardRepository(CardRepository, SQLBaseRepository):
    async def get_by_id(self, id):
        raise NotImplementedError

    async def get_by_division_id(self, id):
        s = (
            select(BusinessCard)
            .filter(BusinessCard.division_id == id)
            .options(selectinload(BusinessCard.materials))
        )

        cards = (await self._session.execute(s)).scalars().all()

        return [converters.card_to_card_schema(c) for c in cards]
