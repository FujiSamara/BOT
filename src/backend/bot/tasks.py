from fastapi_utils.tasks import repeat_every
import logging
from datetime import datetime, timedelta
from aiogram.exceptions import TelegramBadRequest

from bot.handlers.rate.utils import shift_closed
from bot.text import unclosed_shift_notify, unclosed_shift_request
from bot.handlers.utils import notify_worker_by_telegram_id
from bot.kb import rating_menu_button, create_inline_keyboard
import db.service as service


@repeat_every(seconds=60 * 60 * 24, logger=logging.getLogger("uvicorn.error"))
async def notify_with_unclosed_shift() -> None:
    """Notify all owners who has unclosed shifts."""
    logger = logging.getLogger("uvicorn.error")
    logger.info("Notifying owners with unclosed shift.")

    departments_ids = service.get_departments_ids()
    previous_day = datetime.now().date() - timedelta(days=1)

    for deparment_id in departments_ids:
        if not shift_closed(previous_day, deparment_id):
            chef = service.get_chef_by_department_id(deparment_id)
            if chef and chef.telegram_id:
                try:
                    logger.info(f"Notifying {chef.l_name} {chef.f_name}...")
                    msg = await notify_worker_by_telegram_id(
                        id=chef.telegram_id, message=unclosed_shift_notify
                    )
                    await msg.answer(
                        text=unclosed_shift_request,
                        reply_markup=create_inline_keyboard(rating_menu_button),
                    )
                except TelegramBadRequest as e:
                    logger.warning(
                        f"Chef {chef.l_name} {chef.f_name} notifying failed: {e}"
                    )
                except Exception as e:
                    logger.error(
                        f"Chef {chef.l_name} {chef.f_name} notifying failed: {e}"
                    )

    logger.info("Notifying owners completed.")
