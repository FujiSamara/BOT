from aiogram import Router
from app.adapters.bot.handlers.bids_it import (
    repairman,
    worker,
    territorial_manager,
)

router = Router(name="bid_it_main")

router.include_routers(worker.router, repairman.router, territorial_manager.router)
