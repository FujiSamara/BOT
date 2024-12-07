from fastapi_utils.tasks import repeat_every
import asyncio
from typing import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup

from app.infra.logging import logger
import app.services as services

from app.adapters.bot.handlers.rate.utils import shift_closed
from app.adapters.bot.text import unclosed_shift_notify, unclosed_shift_request
from app.adapters.bot.handlers.utils import notify_worker_by_telegram_id
from app.adapters.bot.kb import (
    rating_menu_button,
    create_inline_keyboard,
    get_personal_cabinet_button,
)


@dataclass
class _Task:
    callback: Callable
    time: datetime
    name: str
    task: asyncio.Task | None = None


class TaskScheduler:
    def __init__(self):
        self.tasks: list[_Task] = []
        self.logger = logger

    def register_task(self, task: Callable, time: datetime, name: str):
        try:
            self.logger.info(f"Register task: [{name}]")
            self.tasks.append(
                _Task(
                    callback=task,
                    time=time,
                    name=name,
                )
            )
        except Exception as e:
            self.logger.error(f"Register task {name} except error: {e}")

    async def run_tasks(self):
        self.logger.info("Running tasks.")
        for task_data in self.tasks:
            asyncio.create_task(self._run_task(task_data))
        self.logger.info("Running tasks are completed.")

    async def _run_task(self, task_data: _Task):
        await asyncio.sleep(
            abs(
                (
                    (datetime.now().hour - task_data.time.hour) * 60
                    + (datetime.now().minute - task_data.time.minute)
                )
                * 60
                + (datetime.now().second - task_data.time.second)
            )
        )
        try:
            task_data.task = asyncio.create_task(task_data.callback())
        except Exception as e:
            self.logger.error(f"Task {task_data.name} didn't runned: {e}")

    async def stop_tasks(self):
        self.logger.info("Termination tasks.")
        for runned_task in self.tasks:
            try:
                runned_task.task.cancel()
                await runned_task.task
            except Exception as e:
                self.logger.error(f"Task didn't stopped: {e}")
        self.logger.info("Termination tasks are completed.")


@repeat_every(seconds=60 * 60 * 24, logger=logger)
async def notify_with_unclosed_shift() -> None:
    """Notify all owners who has unclosed shifts."""
    logger.info("Notifying owners with unclosed shift.")

    departments_ids = services.get_departments_ids()
    previous_day = datetime.now().date() - timedelta(days=1)

    for deparment_id in departments_ids:
        if not shift_closed(previous_day, deparment_id):
            chef = services.get_chef_by_department_id(deparment_id)
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
    logger=logger,
)
async def notify_and_droped_departments_teller_cash() -> None:
    """Notify all teller cash to change department"""
    logger.info("Notifying all tellers cash to change department.")
    tellers = services.set_tellers_cash_department()
    for teller in tellers:
        await notify_worker_by_telegram_id(
            message="Актуализируйте производтсво",
            id=teller.telegram_id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[get_personal_cabinet_button]]
            ),
        )
    logger.info("Notifying tellers cash completed")


@repeat_every(
    seconds=60 * 60 * 24,
    logger=logger,
)
async def update_repairman_worktimes() -> None:  # Technical requests
    if datetime.now().weekday() <= 4:
        logger.info("Updating the working hours of the repairmen.")
        services.update_repairman_worktimes(9, 18)
        logger.info("Updating the working hours of the repairmen. Completed")
