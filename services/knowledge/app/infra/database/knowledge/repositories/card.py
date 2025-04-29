from sqlalchemy import ColumnElement, func, select, and_

from common.sql.repository import SQLBaseRepository
from app.contracts.repositories import CardRepository
from app.infra.database.knowledge import converters
from app.infra.database.knowledge.models import BusinessCard, BusinessCardMaterial


class SQLCardRepository(CardRepository, SQLBaseRepository):
    async def _get_by_criteria(self, element: ColumnElement) -> list[BusinessCard]:
        s = select(BusinessCard).where(element)
        s_files = (
            select(
                BusinessCard.id, func.coalesce(func.count(BusinessCardMaterial.id), 0)
            )
            .join(BusinessCardMaterial, BusinessCard.id == BusinessCardMaterial.card_id)
            .group_by(BusinessCard.id)
            .where(element)
        )

        cards = (await self._session.execute(s)).scalars().all()
        card_files = (await self._session.execute(s_files)).all()

        card_files_dict = {card_id: files_count for card_id, files_count in card_files}

        return [
            converters.card_to_card_schema(
                card, materials_count=card_files_dict.get(card.id, 0)
            )
            for card in cards
        ]

    async def get_by_id(self, id):
        cards = await self._get_by_criteria(BusinessCard.id == id)
        if len(cards) == 0:
            return

        return cards[0]

    async def get_by_division_id(self, id):
        return await self._get_by_criteria(BusinessCard.division_id == id)

    async def get_by_division_id_with_name(self, id, name):
        cards = await self._get_by_criteria(
            and_(BusinessCard.division_id == id, BusinessCard.name == name)
        )
        if len(cards) == 0:
            return

        return cards[0]

    async def find_by_name(self, term):
        return await self._get_by_criteria(BusinessCard.name.ilike(f"%{term}%"))

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

    async def update(self, id, card_update):
        s = select(BusinessCard).where(BusinessCard.id == id)
        card = (await self._session.execute(s)).scalars().first()

        if card is None:
            raise ValueError(f"Card {id} not found.")

        for field, value in card_update.model_dump(exclude_unset=True).items():
            setattr(card, field, value)

        await self._session.flush()
        await self._session.refresh(card)

        return converters.card_to_card_schema(card)

    async def delete_card_materials_by_external_id(self, id, material_ids):
        s = select(BusinessCard).where(BusinessCard.id == id)
        card = (await self._session.execute(s)).scalars().first()

        if card is None:
            raise ValueError(f"Card {id} not found.")

        s = select(BusinessCardMaterial).where(
            BusinessCardMaterial.external_id.in_(material_ids)
        )

        materials = (await self._session.execute(s)).scalars().all()

        for material in materials:
            await self._session.delete(material)

        await self._session.flush()
