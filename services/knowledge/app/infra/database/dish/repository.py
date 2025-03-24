from common.sql.repository import SQLBaseRepository
from app.contracts.repositories import DishRepository


class SQLDishRepository(DishRepository, SQLBaseRepository):
    pass
