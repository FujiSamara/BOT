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
    extensive_director,
)

router = Router(name="department_request_main")

executors.build_coordinations()
appraiser.build_coordinations()
chief_technician.include_extensions_callback_query()
territorial_director.include_extensions_callback_query()
extensive_director.include_extensions_callback_query()


router.include_routers(
    worker.router,
    executors.router,
    chief_technician.router,
    appraiser.router,
    local_handlers.router,
    extensive_director.router,
    territorial_director.router,
)
