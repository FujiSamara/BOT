from fastapi_utils.tasks import repeat_every
import logging
from datetime import datetime, timedelta

from bot.bot import get_bot
from bot.handlers.rate.utils import shift_closed
import db.service as service


@repeat_every(seconds=60 * 60 * 24, logger=logging.getLogger("uvicorn.error"))
def notify_with_unclosed_shift() -> None:
    """Notify all owners who has unclosed shifts."""
    logger = logging.getLogger("uvicorn.error")
    logger.info("Notifying owners with unclosed shift.")

    departments_ids = service.get_departments_ids()

    for deparment_id in departments_ids:
        day = datetime.now().date() - timedelta(days=1)

        if shift_closed(day, deparment_id):
            pass

    logger.info("Notifying owners completed.")
