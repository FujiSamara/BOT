from app.adapters.bot.handlers.worker_bids import (
    create,
    coordinate,
    candidate_coordination,
)
from aiogram import Router

router = Router(name="bid_main")

router.include_routers(
    create.router,
    coordinate.router,
    candidate_coordination.router,
)
