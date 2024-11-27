from aiogram import Router

from app.bot.handlers.tech_request import (
    worker,
    repairman,
    territorial_manager,
    chief_technician,
    department_director,
    local_handlers,
)

router = Router(name="technical_request_main")

router.include_routers(
    worker.router,
    repairman.router,
    chief_technician.router,
    territorial_manager.router,
    local_handlers.router,
    department_director.router,
)
