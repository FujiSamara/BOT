from common.contracts.clients import RemoteFileClient
from app.contracts.services import DishService
from app.contracts.uow import DishUnitOfWork
from app.schemas.dish import DishMaterialsSchema


class DishServiceImpl(DishService):
    def __init__(self, dish_uow: DishUnitOfWork, file_client: RemoteFileClient):
        self._uow = dish_uow
        self._file_client = file_client

    async def get_dish_by_id(self, id):
        async with self._uow as uow:
            return await uow.dish.get_by_id(id)

    async def get_dish_modifiers(self, dish_id):
        async with self._uow as uow:
            return await uow.dish.get_modifiers(dish_id)

    async def get_dish_materials(self, dish_id):
        async with self._uow as uow:
            materials_dto = await uow.dish.get_dish_materials(dish_id)

            video = None
            if materials_dto.video is not None:
                video = await self._file_client.request_get_link(materials_dto.video)
            materials = [
                await self._file_client.request_get_link(id)
                for id in materials_dto.materials
            ]

            return DishMaterialsSchema(video=video, materials=materials)
