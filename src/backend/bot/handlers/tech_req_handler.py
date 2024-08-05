from aiogram import Router
from bot.handlers.tech_req import main


router = Router(name="technical_request")

router.include_router(main.router)