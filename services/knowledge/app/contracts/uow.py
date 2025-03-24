from common.contracts.uow import BaseUnitOfWork

from app.contracts.repositories import (
    DishRepository,
    DivisionRepository,
    CardRepository,
)


class FullDivisionUnitOfWork(BaseUnitOfWork):
    card: CardRepository
    division: DivisionRepository
    dish: DishRepository
