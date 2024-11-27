from aiogram import Router
import app.bot.handlers as handlers
from app.bot.handlers import (
    auth_handler,
    main_handler,
)


router = Router(name="main")


router.include_routers(
    main_handler.router,
    auth_handler.router,
    handlers.bid_router,
    handlers.rate_router,
    handlers.bids_it_router,
    handlers.tech_request_router,
    handlers.personal_cabinet_router,
    handlers.monitoring_router,
)
