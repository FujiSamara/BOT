from aiogram import Router
from app.adapters.bot.handlers.extra import restaurant_menu


router = Router()
router.include_routers(restaurant_menu.router)
