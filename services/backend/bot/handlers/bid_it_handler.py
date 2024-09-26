from aiogram import Router
from bot.handlers.bids_it import main

router = Router(name="bid_it")

router.include_router(main.router)
