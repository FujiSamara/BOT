from datetime import date
from app.db import service


def shift_closed(day: date, department_id: int) -> bool:
    """
    Checks shift status (pending/closed).

    Returns `True` if shift closed `False` otherwise.
    """
    records = service.get_work_time_records_by_day_and_department(department_id, day)

    for record in records:
        if not record.work_begin or not record.work_end:
            continue
        if record.worker:
            if record.worker.post.level != 4 and record.worker.post.level != 6:
                continue
        if not record.fine and not record.rating:
            return False

    return True
