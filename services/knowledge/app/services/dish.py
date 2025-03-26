from app.contracts.services import DishService
from app.contracts.uow import DishUnitOfWork


class DishServiceImpl(DishService):
    def __init__(self, dish_uow: DishUnitOfWork):
        self._uow = dish_uow

    async def get_dish_by_id(self, id):
        async with self._uow as uow:
            return await uow.dish.get_by_id(id)

    async def get_dish_modifiers(self, dish_id):
        async with self._uow as uow:
            return await uow.dish.get_modifiers(dish_id)
