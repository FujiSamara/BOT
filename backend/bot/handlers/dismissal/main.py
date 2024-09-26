from aiogram import Router
from bot.handlers.dismissal import (
    employee,
    dismissal_coordination,
)

router = Router(name="dismissal_main")

dismissal_coordination.build_coordination()

router.include_routers(employee.router, dismissal_coordination.router)
