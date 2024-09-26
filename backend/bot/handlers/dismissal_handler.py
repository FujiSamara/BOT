from aiogram import Router
from bot.handlers.dismissal import main

router = Router(name="dismissal")

router.include_router(main.router)
