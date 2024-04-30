from aiogram import Router
from bot.handlers.rate import main


router = Router(name="rate")
router.include_router(main.router)
