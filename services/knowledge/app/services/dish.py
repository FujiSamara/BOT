from common.contracts.clients import RemoteFileClient
from common.schemas import ErrorSchema
from common.schemas.file import FileLinkSchema, FileInSchema, FileDeleteResultSchema
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
            dish = await uow.dish.get_by_id(dish_id)
            if dish is None:
                raise ValueError(f"Dish {dish_id} not found.")

            return await uow.dish.get_modifiers(dish_id)

    async def get_dish_materials(self, dish_id):
        async with self._uow as uow:
            dish = await uow.dish.get_by_id(dish_id)
            if dish is None:
                raise ValueError(f"Dish {dish_id} not found.")

            materials_dto = await uow.dish.get_dish_materials(dish_id)

            video = None
            if materials_dto.video is not None:
                video = await self._file_client.request_get_links([materials_dto.video])
                if len(video) == 0:
                    video = None
                else:
                    video = video[0]

            materials = await self._file_client.request_get_links(
                materials_dto.materials
            )

            return DishMaterialsSchema(video=video, materials=materials)

    async def add_dish_video(self, dish_id, video):
        async with self._uow as uow:
            dish = await uow.dish.get_by_id(dish_id)
            if dish is None:
                raise ValueError(f"Dish {dish_id} not found.")

            key = f"dish/{dish_id}/video/{video.filename}"

            meta = (
                await self._file_client.request_put_links(
                    [FileInSchema(filename=video.filename, key=key, size=video.size)]
                )
            )[0]

            await uow.dish.update(dish_id, DishUpdateSchema(video=meta.id))

            return meta

    async def add_dish_materials(self, dish_id, materials):
        async with self._uow as uow:
            dish = await uow.dish.get_by_id(dish_id)
            if dish is None:
                raise ValueError(f"Dish {dish_id} not found.")

            old_materials = await uow.dish.get_dish_materials(dish_id)
            old_links = await self._file_client.request_get_links(
                old_materials.materials
            )
            old_names_set = set([old_link.name for old_link in old_links])
            new_names_set = set([material.filename for material in materials])

            if len(old_names_set & set(new_names_set)) != 0:
                raise ValueError("Provided material already exist.")

            meta_list: list[FileLinkSchema] = await self._file_client.request_put_links(
                [
                    FileInSchema(
                        filename=material.filename,
                        key=f"card/{dish_id}/materials/{material.filename}",
                        size=material.size,
                    )
                    for material in materials
                ]
            )

            await uow.dish.add_dish_materials(dish_id, [meta.id for meta in meta_list])

            return meta_list

    async def delete_dish_materials(self, dish_id, material_ids):
        async with self._uow as uow:
            dish = await uow.dish.get_by_id(dish_id)
            if dish is None:
                raise ValueError(f"Dish {dish_id} not found.")

            actual_materials_dto = await uow.dish.get_dish_materials(dish_id)
            actual_materials = actual_materials_dto.materials

            not_exist_materials = set(material_ids) - set(actual_materials)
            exist_materials = set(material_ids) & set(actual_materials)

            results = await self._file_client.delete_files(list(exist_materials))
            deleted_with_error = set(
                result.file_id for result in results if result.error is not None
            )

            for id in not_exist_materials:
                results.append(
                    FileDeleteResultSchema(
                        file_id=id,
                        error=ErrorSchema(message="Material does not exist in dish."),
                    )
                )

            await self._uow.dish.delete_dish_materials_by_external_id(
                dish_id, list(exist_materials - deleted_with_error)
            )

            return results

    async def delete_dish_video(self, dish_id):
        async with self._uow as uow:
            dish = await uow.dish.get_by_id(dish_id)
            if dish is None:
                raise ValueError(f"Dish {dish_id} not found.")

            materials = await uow.dish.get_dish_materials(dish_id)

            if materials.video is None:
                raise ValueError(f"Video for dish {dish_id} not found.")

            (delete_result,) = await self._file_client.delete_files([materials.video])
            if delete_result.error is None:
                await uow.dish.update(dish_id, DishUpdateSchema(video=None))

            return delete_result
