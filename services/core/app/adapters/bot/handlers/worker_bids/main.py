from app.adapters.bot.handlers.worker_bids import (
    create,
    coordinate,
)
from aiogram import Router

from app.adapters.bot.handlers.worker_bids import candidates_subordinate

router = Router(name="workers_bids")


coordinate.build_coordinations()

router.include_routers(
    create.router,
    coordinate.router,
    candidates_subordinate.router,
)
