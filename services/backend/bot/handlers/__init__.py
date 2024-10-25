from bids.main import router as bid_router
from bids_it.main import router as bids_it_router
from monitoring.main import router as monitoring_router
from perconal_cab.main import router as personal_cabinet_router
from rate.main import router as rate_router
from tech_request.main import router as tech_request_router

__all__ = [
    "bid_router",
    "bids_it_router",
    "monitoring_router",
    "personal_cabinet_router",
    "rate_router",
    "tech_request_router",
]
