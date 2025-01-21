from aiogram import Router
from app.adapters.bot.handlers.bids_it import (
    repairman,
    appraiser,
    worker,
)

router = Router(name="bid_it_main")

router.include_routers(worker.router, repairman.router, appraiser.router)
