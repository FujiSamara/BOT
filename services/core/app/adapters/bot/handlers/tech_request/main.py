from aiogram import Router

from app.adapters.bot.handlers.tech_request import (
    worker,
    repairman,
    appraiser,
    chief_technician,
    department_director,
    local_handlers,
)

router = Router(name="technical_request_main")

router.include_routers(
    worker.router,
    repairman.router,
    chief_technician.router,
    appraiser.router,
    local_handlers.router,
    department_director.router,
)
