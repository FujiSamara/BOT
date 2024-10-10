from io import BytesIO

import aiohttp
from settings import get_settings
import db.orm as orm
from db.models import (
    WorkTime,
)
from db.schemas import (
    QuerySchema,
    WorkTimeSchema,
    aliases,
)
from fastapi import HTTPException


def get_work_time_records_by_day_and_department(
    department_id: int, day: str
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
) -> list[WorkTimeSchema]:
    """Return budget records with applied instructions.

    See `QueryBuilder.apply` for more info applied instructions.
    """
    return orm.get_models(
        WorkTime, WorkTimeSchema, page, records_per_page, query_schema
    )


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
        "work_begin": record.work_begin.strftime(get_settings().date_format),
        "day": record.day.strftime(get_settings().date_format).split()[0],
    }

    if hasattr(record, "work_end") and record.work_end is not None:
        dump["work_end"] = record.work_end.strftime(get_settings().date_format)
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
            f"{get_settings().external_api}/connector/biosmart/work_times/{id}",
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
            f"{get_settings().external_api}/connector/biosmart/work_times/{record.id}",
            json=dif,
        ) as resp:
            if resp.status >= 400:
                raise HTTPException(status_code=resp.status)


async def create_worktime(record: WorkTimeSchema) -> None:
    """Creates worktime"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{get_settings().external_api}/connector/biosmart/work_times",
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
    )
