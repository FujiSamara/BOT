from app.adapters.bot.handlers.bids.main import router as bid_router
from app.adapters.bot.handlers.bids_it.main import router as bids_it_router
from app.adapters.bot.handlers.monitoring.main import router as monitoring_router
from app.adapters.bot.handlers.perconal_cab.main import (
    router as personal_cabinet_router,
)
from app.adapters.bot.handlers.rate.main import router as rate_router
from app.adapters.bot.handlers.tech_request.main import router as tech_request_router

__all__ = [
    "bid_router",
    "bids_it_router",
    "monitoring_router",
    "personal_cabinet_router",
    "rate_router",
    "tech_request_router",
]
