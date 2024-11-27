import logging
import app.db.orm as orm
from app.db.models import (
    Expenditure,
)
from app.db.schemas import (
    BudgetRecordSchema,
    ExpenditureSchema,
    QuerySchema,
    WorkerSchema,
)
from app.db.service.budget import create_budget_record


def get_chapters() -> list[str]:
    """Returns list of all unique chapters in db"""
    expenditures = orm.get_expenditures()
    return list(set(expenditure.chapter for expenditure in expenditures))


def get_expenditures_names_by_chapter(chapter: str) -> list[str]:
    """Returns list of all expenditure names in db"""
    expenditures = orm.get_expenditures()

    result = []

    for expenditure in expenditures:
        if expenditure.chapter == chapter:
            result.append(expenditure.name)

    return result


def get_expenditure_count(
    query_schema: QuerySchema,
) -> int:
    """Return expenditure count in bd."""
    return orm.get_model_count(Expenditure, query_schema)


def get_expenditures_at_page(
    page: int,
    records_per_page: int,
    query_schema: QuerySchema,
) -> list[ExpenditureSchema]:
    """Return expenditures with applied instructions.

    See `QueryBuilder.apply` for more info applied instructions.
    """
    return orm.get_models(
        Expenditure, ExpenditureSchema, page, records_per_page, query_schema
    )


def find_expenditures(record: str) -> list[WorkerSchema]:
    """Finds expenditures by given `record`.

    Search is carried out by name and chapter.
    """
    return orm.find_expenditures_by_name(record)


def get_expenditures() -> list[ExpenditureSchema]:
    """Returns all expenditures in database."""
    return orm.get_expenditures()


def create_expenditure(expenditure: ExpenditureSchema) -> None:
    """Creates expenditure"""
    if not orm.create_expenditure(expenditure):
        logging.getLogger("uvicorn.error").error("Expenditure wasn't created.")
    updated_expenditure = get_last_expenditure()
    budget_record = BudgetRecordSchema(
        expenditure=updated_expenditure,
        department=None,
        limit=None,
        last_update=None,
    )
    create_budget_record(budget_record)


def remove_expenditure(id: int) -> None:
    orm.remove_expenditure(id)


def update_expenditure(expenditure: ExpenditureSchema) -> None:
    """Updates expenditure by `ExpenditureSchema.id`"""
    if not orm.update_expenditure(expenditure):
        logging.getLogger("uvicorn.error").error("Expenditure wasn't updated.")


def get_expenditure_by_id(id: int) -> ExpenditureSchema:
    """Finds expenditure by this `id`."""
    return orm.find_expenditure_by_column(Expenditure.id, id)


def get_last_expenditure() -> ExpenditureSchema:
    """Returns last expenditure in db."""
    return orm.get_last_expenditrure()
