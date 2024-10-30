from fastapi_utils.tasks import repeat_every
import logging
from datetime import datetime, timedelta
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup

from bot.handlers.rate.utils import shift_closed
from bot.text import unclosed_shift_notify, unclosed_shift_request
from bot.handlers.utils import notify_worker_by_telegram_id
from bot.kb import (
    rating_menu_button,
    create_inline_keyboard,
    get_personal_cabinet_button,
)
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


@repeat_every(
    seconds=60 * 60 * 24,
    logger=logging.getLogger("uvicorn.error"),
    wait_first=abs(
        datetime.now().hour * 60 * 60 + datetime.now().minute * 60 - 8 * 60 * 60
    ),
)
async def notify_and_droped_departments_teller_cash() -> None:
    """Notify all teller cash to change department"""
    logger = logging.getLogger("uvicorn.error")
    logger.info("Notifying all tellers cash to change department.")
    tellers = service.set_tellers_cash_department()
    for teller in tellers:
        await notify_worker_by_telegram_id(
            message="Актуализируйте производтсво",
            id=teller.telegram_id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[get_personal_cabinet_button]]
            ),
        )
    logger.info("Notifying tellers cash completed")
