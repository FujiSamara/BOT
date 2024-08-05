from aiogram import Router
from bot.handlers.tech_req import tr_worker

router = Router(name="technical_request_main")

router.include_routers(tr_worker.router)