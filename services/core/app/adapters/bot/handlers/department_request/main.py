from aiogram import Router

from app.adapters.bot.handlers.department_request import (
    worker,
    territorial_manager,
    local_handlers,
    executors,
)
from app.adapters.bot.handlers.department_request.technician import (
    chief_technician,
    department_director,
)

router = Router(name="department_request_main")

executors.build_coordinations()
territorial_manager.build_coordinations()

router.include_routers(
    worker.router,
    executors.router,
    chief_technician.router,
    territorial_manager.router,
    local_handlers.router,
    department_director.router,
)
