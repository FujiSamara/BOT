from app.adapters.bot.handlers.worker_bids import (
    create,
    coordinate,
)
from aiogram import Router

from services.core.app.adapters.bot.handlers.worker_bids import workers_subordinate

router = Router(name="bid_main")

router.include_routers(
    create.router,
    coordinate.router,
    workers_subordinate.router,
)
