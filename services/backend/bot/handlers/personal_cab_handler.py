from aiogram import Router
from bot.handlers.perconal_cab import main

router = Router(name="personal_cabinet_handler")

router.include_router(main.router)
