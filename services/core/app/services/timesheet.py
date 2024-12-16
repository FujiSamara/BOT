from io import BytesIO
from app.infra.database.models import Worker
import app.infra.database.orm as orm
from app.schemas import QuerySchema, TimeSheetSchema


def get_timesheet_count(
    query_schema: QuerySchema,
) -> int:
    """Returns timesheet count in bd."""
    query_schema.date_query = None
    return orm.get_model_count(Worker, query_schema)


def get_timesheets_at_page(
    page: int,
    records_per_page: int,
    query_schema: QuerySchema,
) -> list[TimeSheetSchema]:
    """Return timesheets with applied instructions.

    - Note: instructions applies to table `Workers`.

    See `QueryBuilder.apply` for more info applied instructions.
    """
    return orm.get_timesheets(
        query_schema,
        page,
        records_per_page,
    )


def export_timesheets(query_schema: QuerySchema) -> BytesIO:
    timesheets = orm.get_timesheets(query_schema)
