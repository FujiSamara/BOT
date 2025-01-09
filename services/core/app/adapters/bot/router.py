from aiogram import Router
import app.adapters.bot.handlers as handlers
from app.adapters.bot.handlers import (
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
    handlers.department_request_router,
    handlers.personal_cabinet_router,
    handlers.monitoring_router,
    handlers.worker_bid_router,
)
