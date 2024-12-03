from fastapi import FastAPI
from typing import AsyncGenerator
from aiogram import Dispatcher
from aiogram.loggers import dispatcher, event, middlewares, scene, webhook
from aiogram.types import BotCommand
from datetime import datetime

from app.infra.config import settings
from app.infra.logging import logger

from app.adapters.bot.bot import get_bot, get_dispatcher, _bot_webhook, _check_webhook

from app.adapters.bot.router import router
from app.adapters.bot.tasks import (
    TaskScheduler,
    notify_with_unclosed_shift,
    notify_and_droped_departments_teller_cash,
    update_repairman_worktimes,
)


def configure(bot_api: FastAPI):
    """Configures fast api admin app."""
    bot_api.add_api_route(path="/webhook", endpoint=_bot_webhook, methods=["POST"])
    _configure_dispatcher(get_dispatcher())

    # Disables aiogram loggers
    dispatcher.propagate = False
    event.propagate = False
    middlewares.propagate = False
    scene.propagate = False
    webhook.propagate = False


async def lifespan(_: FastAPI) -> AsyncGenerator:
    # Bot webhooks
    await get_bot().delete_webhook(drop_pending_updates=True)
    await get_bot().set_webhook(
        url=settings.bot_webhook_url,
        secret_token=settings.telegram_token,
        allowed_updates=get_dispatcher().resolve_used_update_types(),
        drop_pending_updates=True,
    )
    await get_bot().set_my_commands(
        [BotCommand(command="start", description="Запускает бота")]
    )
    logger.info("Webhook info: " + str(await _check_webhook()).split()[0])
    # Tasks
    tasks = TaskScheduler()
    YMD = {"year": 1, "month": 1, "day": 1}
    tasks.register_task(
        task=notify_with_unclosed_shift,
        time=datetime(**YMD, hour=2, minute=0, second=0),
        name="notify_with_unclosed_shift",
    )
    tasks.register_task(
        task=notify_and_droped_departments_teller_cash,
        time=datetime(**YMD, hour=8, minute=0, second=0),
        name="notify_and_droped_departments_teller_cash",
    )
    tasks.register_task(
        task=update_repairman_worktimes,
        time=datetime(**YMD, hour=16, minute=6, second=20),
        name="update_repairman_worktimes",
    )
    await tasks.run_tasks()

    yield
    await get_bot().delete_webhook(drop_pending_updates=True)
    await tasks.stop_tasks()
    yield


def _configure_dispatcher(dp: Dispatcher):
    """Configures telegram dispatcher"""
    dp.include_router(router)
