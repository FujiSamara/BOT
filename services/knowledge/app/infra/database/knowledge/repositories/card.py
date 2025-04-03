from sqlalchemy import select, and_

from common.sql.repository import SQLBaseRepository
from app.contracts.repositories import CardRepository
from app.infra.database.knowledge import converters
from app.infra.database.knowledge.models import BusinessCard, BusinessCardMaterial


class SQLCardRepository(CardRepository, SQLBaseRepository):
    async def get_by_id(self, id):
        s = select(BusinessCard).where(BusinessCard.id == id)

        card = (await self._session.execute(s)).scalars().first()
        if card is None:
            return None

        return converters.card_to_card_schema(card)

    async def get_by_division_id(self, id):
        s = select(BusinessCard).where(BusinessCard.division_id == id)

        cards = (await self._session.execute(s)).scalars().all()

        return [converters.card_to_card_schema(c) for c in cards]

    async def get_by_division_id_with_name(self, id, name):
        s = select(BusinessCard).where(
            and_(BusinessCard.division_id == id, BusinessCard.name == name)
        )

        card = (await self._session.execute(s)).scalars().first()
        if card is None:
            return None

        return converters.card_to_card_schema(card)

    async def find_by_name(self, term):
        s = select(BusinessCard).where(BusinessCard.name.ilike(f"%{term}%"))
        cards = (await self._session.execute(s)).scalars().all()

        return [converters.card_to_card_schema(c) for c in cards]

    async def get_card_materials(self, card_id):
        s = select(BusinessCardMaterial.external_id).where(
            BusinessCardMaterial.card_id == card_id
        )

        return list((await self._session.execute(s)).scalars().all())

    async def add_card_materials(self, card_id, materials):
        for material in materials:
            dm = BusinessCardMaterial(card_id=card_id, external_id=material)
            self._session.add(dm)

        await self._session.flush()
