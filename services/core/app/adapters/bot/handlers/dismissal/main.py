from aiogram import Router
from bot.handlers.dismissal import (
    worker,
    dismissal_coordination,
    chief,
)

router = Router(name="dismissal_main")

dismissal_coordination.build_coordination()

router.include_routers(worker.router, dismissal_coordination.router, chief.router)
