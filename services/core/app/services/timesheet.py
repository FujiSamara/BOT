import calendar
from io import BytesIO
from app.infra.database.models import Worker
import app.infra.database.orm as orm
from app.schemas import QuerySchema, TimeSheetSchema, aliases
from app.adapters.output.file.export import XlSXWriterExporter


def get_timesheet_count(
    query_schema: QuerySchema,
) -> int:
    """Returns timesheet count in bd."""
    return orm.get_timesheet_count(query_schema)
    query_schema.date_query = None
    return orm.get_model_count(Worker, query_schema)


def get_timesheets_at_page(
    page: int,
    records_per_page: int,
    query_schema: QuerySchema,
) -> list[dict]:
    """Return timesheets with applied instructions.

    - Note: instructions applies to table `Workers`.

    See `QueryBuilder.apply` for more info applied instructions.
    """
    start = query_schema.date_query.start
    _, last_day = calendar.monthrange(start.year, start.month)
    timesheets = orm.get_timesheets(
        query_schema,
        page,
        records_per_page,
    )
    for timesheet in timesheets:
        timesheet.last_day = last_day

    return [timesheet.model_dump() for timesheet in timesheets]


def export_timesheets(query_schema: QuerySchema) -> BytesIO:
    start = query_schema.date_query.start
    _, last_day = calendar.monthrange(start.year, start.month)
    timesheets = orm.get_timesheets(query_schema)
    for timesheet in timesheets:
        timesheet.last_day = last_day

    exporter = XlSXWriterExporter(
        exclude_columns=[],
        field_formatters=[],
        aliases=aliases[TimeSheetSchema],
    )

    return exporter.export(timesheets, with_dump=True)
