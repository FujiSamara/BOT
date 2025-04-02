from common.contracts.clients import RemoteFileClient
from common.schemas.file import FileLinkSchema
from app.contracts.services import DishService
from app.contracts.uow import DishUnitOfWork
from app.schemas.dish import DishMaterialsSchema, DishUpdateSchema


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
                try:
                    video = await self._file_client.request_get_link(
                        materials_dto.video
                    )
                except Exception:
                    video = None

            materials = []

            for id in materials_dto.materials:
                try:
                    material = await self._file_client.request_get_link(id)
                    materials.append(material)
                except Exception:
                    pass

            return DishMaterialsSchema(video=video, materials=materials)

    async def add_dish_video(self, dish_id, video):
        async with self._uow as uow:
            dish = await uow.dish.get_by_id(dish_id)
            if dish is None:
                raise ValueError(f"Dish {dish_id} not found.")

            key = f"dish/{dish_id}/video/{video.filename}"

            meta = await self._file_client.request_put_link(
                video.filename, key, video.size
            )

            await uow.dish.update(dish_id, DishUpdateSchema(video=meta.id))

            return meta

    async def add_dish_materials(self, dish_id, materials):
        async with self._uow as uow:
            dish = await uow.dish.get_by_id(dish_id)
            if dish is None:
                raise ValueError(f"Dish {dish_id} not found.")

            old_materials = await uow.dish.get_dish_materials(dish_id)
            old_names_set = set(
                [
                    (await self._file_client.request_get_link(id)).name
                    for id in old_materials.materials
                ]
            )
            new_names_set = set([material.filename for material in materials])

            if len(old_names_set & set(new_names_set)) != 0:
                raise ValueError("Provided material already exist.")

            meta_list: list[FileLinkSchema] = []

            for material in materials:
                key = f"dish/{dish_id}/materials/{material.filename}"
                meta = await self._file_client.request_put_link(
                    material.filename, key, material.size
                )
                meta_list.append(meta)

            await uow.dish.add_dish_materials(dish_id, [meta.id for meta in meta_list])

            return meta_list
