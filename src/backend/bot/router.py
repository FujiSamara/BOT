from aiogram import Router
from bot.handlers import (
    auth_handler,
    main_handler,
    bid_handler,
    rate_handler,
    bid_it_handler,
)


router = Router(name="main")


router.include_routers(
    main_handler.router,
    auth_handler.router,
    bid_handler.router,
    rate_handler.router,
    bid_it_handler.router,
)
