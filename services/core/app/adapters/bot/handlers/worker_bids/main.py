from services.core.app.adapters.bot.handlers.worker_bids import create
from aiogram import Router

router = Router(name="bid_main")

router.include_routers(
    create.router,
)
