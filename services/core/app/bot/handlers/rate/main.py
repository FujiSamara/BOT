from aiogram import Router
from app.bot.handlers.rate import rate_worker


router = Router(name="rating_main")

router.include_routers(rate_worker.router)
