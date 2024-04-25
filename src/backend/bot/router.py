from aiogram import Router
from bot.handlers import auth_handler, main_handler, bid_handler


router = Router(name="main")


router.include_routers(
    auth_handler.router,
    bid_handler.router,
    main_handler.router
)
