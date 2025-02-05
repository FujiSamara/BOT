from aiogram import Router

from app.adapters.bot.handlers.tech_request import (
    worker,
    repairman,
    appraiser,
    chief_technician,
    local_handlers,
    extensive_director,
    territorial_director,
)

router = Router(name="technical_request_main")

router.include_routers(
    worker.router,
    repairman.router,
    chief_technician.router,
    appraiser.router,
    local_handlers.router,
    extensive_director.router,
    territorial_director.router,
)
