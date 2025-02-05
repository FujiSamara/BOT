from aiogram import Router

from app.adapters.bot.handlers.tech_request import (
    worker,
    repairman,
    appraiser,
    chief_technician,
    local_handlers,
)
from services.core.app.adapters.bot.handlers.tech_request import extensive_director

router = Router(name="technical_request_main")

router.include_routers(
    worker.router,
    repairman.router,
    chief_technician.router,
    appraiser.router,
    local_handlers.router,
    extensive_director.router,
)
