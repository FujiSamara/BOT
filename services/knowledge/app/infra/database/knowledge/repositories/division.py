from common.sql.repository import SQLBaseRepository
from app.contracts.repositories import DivisionRepository


class SQLDivisionRepository(DivisionRepository, SQLBaseRepository):
    pass
