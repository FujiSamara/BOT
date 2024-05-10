from datetime import date
from db import service
from settings import get_settings


def get_shift_status(day: date, department_id: int) -> bool:
    """
    Checks shift status (pending/closed).

    Returns `True` if shift closed `False` otherwise.
    """
    records = service.get_work_time_records_by_day_and_department(
        department_id, day.strftime(get_settings().date_format)
    )

    for record in records:
        if not record.fine and not record.rating:
            return False

    return True
