from aiogram import Router
from bot.handlers.tech_request import main


router = Router(name="technical_request")

router.include_router(main.router)
