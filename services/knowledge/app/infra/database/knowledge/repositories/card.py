from common.sql.repository import SQLBaseRepository
from app.contracts.repositories import CardRepository


class SQLCardRepository(CardRepository, SQLBaseRepository):
    pass
