from aiogram import Router

from app.adapters.bot.handlers.department_request import (
    worker,
    appraiser,
    local_handlers,
    executors,
)
from app.adapters.bot.handlers.department_request.technician import (
    chief_technician,
    territorial_director,
)
from services.core.app.adapters.bot.handlers.department_request.technician import department_director

router = Router(name="department_request_main")

executors.build_coordinations()
appraiser.build_coordinations()

router.include_routers(
    worker.router,
    executors.router,
    chief_technician.router,
    appraiser.router,
    local_handlers.router,
    department_director.router,
    territorial_director.router,
)
