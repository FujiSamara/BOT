from common.contracts.clients import RemoteFileClient
from common.schemas import ErrorSchema
from common.schemas.file import FileLinkSchema, FileInSchema, FileDeleteResultSchema
from app.contracts.services import CardService
from app.contracts.uow import CardUnitOfWork

from app.schemas.card import BusinessCardSchema


class CardServiceImpl(CardService):
    def __init__(self, card_uow: CardUnitOfWork, file_client: RemoteFileClient):
        self._uow = card_uow
        self._file_client = file_client

    async def get_card_by_id(self, id):
        async with self._uow as uow:
            card = await uow.card.get_by_id(id)
            if card is None:
                return None

            return BusinessCardSchema(
                id=card.id,
                name=card.name,
                description=card.description,
            )

    async def get_card_materials(self, card_id):
        async with self._uow as uow:
            materials = await uow.card.get_card_materials(card_id)
            return await self._file_client.request_get_links(materials)

    async def add_card_materials(self, card_id, materials):
        async with self._uow as uow:
            card = await uow.card.get_by_id(card_id)
            if card is None:
                raise ValueError(f"Dish {card_id} not found.")

            old_materials = await uow.card.get_card_materials(card_id)
            old_links = await self._file_client.request_get_links(old_materials)
            old_names_set = set([old_link.name for old_link in old_links])
            new_names_set = set([material.filename for material in materials])

            if len(old_names_set & set(new_names_set)) != 0:
                raise ValueError("Provided material already exist.")

            meta_list: list[FileLinkSchema] = await self._file_client.request_put_links(
                [
                    FileInSchema(
                        filename=material.filename,
                        key=f"card/{card_id}/materials/{material.filename}",
                        size=material.size,
                    )
                    for material in materials
                ]
            )

            await uow.card.add_card_materials(card_id, [meta.id for meta in meta_list])

            return meta_list

    async def update_card(self, card_id, card_update):
        async with self._uow as uow:
            return await uow.card.update(card_id, card_update)

    async def deleta_card_materials(self, card_id, material_ids):
        async with self._uow as uow:
            card = await uow.card.get_by_id(card_id)
            if card is None:
                raise ValueError(f"Dish {card_id} not found.")

            actual_materials = await uow.card.get_card_materials(card_id)

            not_exist_materials = set(material_ids) - set(actual_materials)
            exist_materials = set(material_ids) & set(actual_materials)

            results = await self._file_client.delete_files(list(exist_materials))

            for id in not_exist_materials:
                results.append(
                    FileDeleteResultSchema(
                        file_id=id,
                        error=ErrorSchema(message="Material does not exist in card."),
                    )
                )

            await self._uow.card.delete_card_materials(card_id, exist_materials)

            return results
