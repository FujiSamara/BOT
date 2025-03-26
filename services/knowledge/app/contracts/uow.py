from common.contracts.uow import BaseUnitOfWork

from app.contracts.repositories import (
    DishRepository,
    DivisionRepository,
    CardRepository,
)


class CardUnitOfWork(BaseUnitOfWork):
    card: CardRepository


class DishUnitOfWork(BaseUnitOfWork):
    dish: DishRepository


class DivisionUnitOfWork(DishUnitOfWork):
    division: DivisionRepository
