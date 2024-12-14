from datetime import datetime
from app.infra.database.models import Worker
import app.infra.database.orm as orm
from app.schemas import QuerySchema, TimeSheetSchema, WorkerSchema

from app.services import worktime


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
    """Return budget records with applied instructions.

    See `QueryBuilder.apply` for more info applied instructions.
    """
    interval = query_schema.date_query
    query_schema.date_query = None
    workers = orm.get_models(Worker, WorkerSchema, page, records_per_page, query_schema)

    if interval is not None:
        return get_timesheets_by_workers_in_month(
            workers, [interval.start], [interval.end]
        )

    return get_timesheets_by_workers_in_month(workers)


def get_timesheets_by_workers_in_month(
    workers: list[WorkerSchema],
    begins: list[datetime] | None = None,
    ends: list[datetime] | None = None,
) -> list[TimeSheetSchema]:
    timesheets: list[TimeSheetSchema] = []

    for worker in workers:
        hours = 0
        if begins is None or ends is None:
            hours = worktime.get_sum_hours_in_months(worker.id)
        else:
            hours = worktime.get_hours_sum_in_intervals(worker.id, begins, ends)

        fullname = f"{worker.f_name} {worker.l_name} {worker.o_name}"
        timesheet = TimeSheetSchema(
            worker_fullname=fullname, post_name=worker.post.name, hours=hours
        )

        timesheets.append(timesheet)

    return timesheets
