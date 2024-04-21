from aiogram import Router
from bot.handlers.bids import main

router = Router(name="bid")

router.include_router(main.router)