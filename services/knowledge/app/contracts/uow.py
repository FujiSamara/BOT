from common.contracts.uow import BaseUnitOfWork

from app.contracts.repositories import (
    DishRepository,
    DivisionRepository,
    CardRepository,
)


class CardUnitOfWork(BaseUnitOfWork):
    card: CardRepository


class DivisionUnitOfWork(CardUnitOfWork):
    division: DivisionRepository
    dish: DishRepository
