from datetime import date, datetime, timedelta
from io import BytesIO
import base64

import aiohttp
from app.infra.config import settings
import app.infra.database.orm as orm
from app.infra.database.models import (
    WorkTime,
)
from app.schemas import (
    QuerySchema,
    WorkTimeSchema,
    WorkTimeSchemaFull,
    aliases,
)
from fastapi import HTTPException


def get_work_time_records_by_day_and_department(
    department_id: int, day: date
) -> list[WorkTimeSchema]:
    """
    Returns all work times records in database by `department_id`
    and `day`.
    """
    return orm.get_work_time_records_by_columns(
        [WorkTime.department_id, WorkTime.day],
        [department_id, day],
    )


def get_work_time_record_by_id(id: int) -> WorkTimeSchema:
    """
    Return work time record in database by `id`.

    If record not exist return `None`.
    """

    return orm.find_work_time_record_by_columns(
        [WorkTime.id],
        [id],
    )


def update_work_time_record(record: WorkTimeSchema) -> None:
    """
    Updates work time record if it exists.
    """
    orm.update_work_time(record)


def get_wortkime_count(
    query_schema: QuerySchema,
) -> int:
    """Returns worktime count in bd."""
    return orm.get_model_count(WorkTime, query_schema)


def get_worktimes_at_page(
    page: int,
    records_per_page: int,
    query_schema: QuerySchema,
) -> list[WorkTimeSchemaFull]:
    """Return budget records with applied instructions.

    See `QueryBuilder.apply` for more info applied instructions.
    """
    rows = orm.get_worktimes_without_photo(page, records_per_page, query_schema)

    for row in rows:
        if len(row.photo_b64) > 0:
            row.photo_b64 = f"{row.id}"

    return rows


def dump_worktime(record: WorkTimeSchema) -> dict:
    if (
        not hasattr(record, "worker")
        or not hasattr(record, "department")
        or not hasattr(record, "post")
        or not hasattr(record, "work_begin")
    ):
        raise HTTPException(status_code=400)

    dump = {
        "worker_id": record.worker.id,
        "company_id": record.department.company.id,
        "post_id": record.post.id,
        "department_id": record.department.id,
        "work_begin": record.work_begin.strftime(settings.date_time_format),
        "day": record.day.strftime(settings.date_format),
    }

    if hasattr(record, "work_end") and record.work_end is not None:
        dump["work_end"] = record.work_end.strftime(settings.date_time_format)
    if hasattr(record, "work_duration") and record.work_duration is not None:
        dump["work_duration"] = record.work_duration
    if hasattr(record, "salary") and record.salary is not None:
        dump["salary"] = record.salary
    if hasattr(record, "fine") and record.fine is not None:
        dump["fine"] = record.fine
    if hasattr(record, "rating") and record.rating is not None:
        dump["rating"] = record.rating

    return dump


async def remove_worktime(id: int) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"{settings.external_api}/connector/biosmart/work_times/{id}",
        ) as resp:
            if resp.status >= 400:
                raise HTTPException(status_code=resp.status)


async def update_worktime(record: WorkTimeSchema) -> None:
    """Updates worktime by `WorkTimeSchema.id`"""
    new = dump_worktime(record)
    old = dump_worktime(get_work_time_record_by_id(record.id))
    dif = dict(new.items() - old.items())

    async with aiohttp.ClientSession() as session:
        async with session.put(
            f"{settings.external_api}/connector/biosmart/work_times/{record.id}",
            json=dif,
        ) as resp:
            if resp.status >= 400:
                raise HTTPException(status_code=resp.status)


async def create_worktime(record: WorkTimeSchema) -> None:
    """Creates worktime"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.external_api}/connector/biosmart/work_times",
            json=dump_worktime(record),
        ) as resp:
            if resp.status >= 400:
                raise HTTPException(status_code=resp.status)


def export_worktimes(
    query_schema: QuerySchema,
) -> BytesIO:
    """Returns xlsx file with worktimes filtered by `query_schema`."""
    # Formatters
    return orm.export_models(
        WorkTime,
        query_schema,
        aliases=aliases[WorkTimeSchema],
        exclude_columns=["photo_b64"],
    )


def get_worktime_photo_by_id(id: int) -> BytesIO:
    photo_b64 = orm.get_worktime_photo(id)
    decoded_photo = base64.b64decode(photo_b64)
    return BytesIO(decoded_photo)


def get_opened_today_worktime(worker_id: int) -> WorkTimeSchema | None:
    """Return last open WorkTimeSchema | None by worker id"""
    return orm.get_openned_today_worktime(worker_id=worker_id)


def get_hours_sum_in_intervals(
    worker_id: int, begins: list[datetime], ends: list[datetime]
) -> float:
    return orm.get_sum_duration_for_worker_in_months(worker_id, begins, ends)


def get_hours_sum_in_month(worker_id: int, month: datetime | None = None) -> float:
    """Counts sum of work_duration for specified months.

    - Note: if months not specified then counts for current month.

    :return: Counted sum.
    """
    if month is None:
        month = datetime.now()

    begin_date = month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    month = begin_date.month % 12 + 1
    year = begin_date.year + 1 if begin_date.month // 12 == 1 else begin_date.year

    end_date = begin_date.replace(
        month=begin_date.month % 12 + 1,
        year=year,
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    ) - timedelta(days=1)

    return orm.get_sum_duration_for_worker_in_months(
        worker_id, [begin_date], [end_date]
    )


def get_last_completed_worktimes_by_tg_id(
    tg_id: int, limit: int = 10, offset: int = 0
) -> list[WorkTimeSchema] | None:
    """Return closed WorkTimeSchema's | None"""
    return orm.get_last_completed_worktimes_by_tg_id(
        tg_id=tg_id, limit=limit, offset=offset
    )
