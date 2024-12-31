from app.adapters.bot.handlers.bids.main import router as bid_router
from app.adapters.bot.handlers.bids_it.main import router as bids_it_router
from app.adapters.bot.handlers.monitoring.main import router as monitoring_router
from app.adapters.bot.handlers.personal_cab.main import (
    router as personal_cabinet_router,
)
from app.adapters.bot.handlers.rate.main import router as rate_router
from app.adapters.bot.handlers.department_request.main import (
    router as department_request_router,  # Technical and Cleaning requests
)
from app.adapters.bot.handlers.worker_bids.main import router as worker_bid_router

__all__ = [
    "bid_router",
    "bids_it_router",
    "monitoring_router",
    "personal_cabinet_router",
    "rate_router",
    "department_request_router",
    "worker_bid_router",
]
