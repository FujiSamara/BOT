import app.db.orm as orm
from app.db.models import (
    BudgetRecord,
)
from app.db.schemas import (
    BudgetRecordSchema,
    QuerySchema,
)
import logging


def get_budget_records_count(
    query_schema: QuerySchema,
) -> int:
    """Return budget records count in bd."""
    return orm.get_model_count(BudgetRecord, query_schema)


def get_budget_records_at_page(
    page: int,
    records_per_page: int,
    query_schema: QuerySchema,
) -> list[BudgetRecordSchema]:
    """Return budget records with applied instructions.

    See `QueryBuilder.apply` for more info applied instructions.
    """
    return orm.get_models(
        BudgetRecord, BudgetRecordSchema, page, records_per_page, query_schema
    )


def get_budget_records() -> list[BudgetRecordSchema]:
    """Returns all budget records in database."""
    return orm.get_budget_records()


def create_budget_record(record: BudgetRecordSchema) -> None:
    """Creates budget record"""
    if not orm.create_budget_record(record):
        logging.getLogger("uvicorn.error").error("Budget record wasn't created.")


def remove_budget_record(id: int) -> None:
    orm.remove_budget_record(id)


def update_budget_record(record: BudgetRecordSchema) -> None:
    """Updates expenditure by `ExpenditureSchema.id`"""
    if not orm.update_budget_record(record):
        logging.getLogger("uvicorn.error").error("Budget record wasn't updated.")


def get_budget_record_by_id(id: int) -> BudgetRecordSchema:
    """Finds budget record by this `id`."""
    return orm.find_budget_record_by_column(BudgetRecord.id, id)


def get_last_budget_record() -> BudgetRecordSchema:
    """Returns last budget record in db."""
    return orm.get_last_budget_record()
