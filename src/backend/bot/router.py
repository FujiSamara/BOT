from aiogram import Router


router = Router(name="main")

from bot.handlers import auth_handler, main_handler, bid_handler

router.include_routers(
    auth_handler.router,
    bid_handler.router,
    main_handler.router
)