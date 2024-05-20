from functools import lru_cache
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
from aiogram.types import Update, WebhookInfo
from settings import get_settings
from typing import Annotated
from fastapi import Header
import logging


@lru_cache
def get_dispatcher() -> Dispatcher:
    return Dispatcher()


@lru_cache
def get_bot() -> Bot:
    return Bot(token=get_settings().bot_token, parse_mode=ParseMode.HTML)


async def _bot_webhook(
    update: dict,
    x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None,
):
    """Registers webhook endpoint for telegram bot"""
    if x_telegram_bot_api_secret_token != get_settings().telegram_token:
        logging.getLogger("uvicorn.error").error("Wrong secret token !")
        return {"status": "error", "message": "Wrong secret token !"}
    try:
        answer = await get_dispatcher().feed_update(
            bot=get_bot(), update=Update(**update)
        )
        return answer
    except Exception as e:
        logging.getLogger("uvicorn.error").error(f"Bot hook error: {e}")
        return


async def _check_webhook() -> WebhookInfo | None:
    webhook_info = await get_bot().get_webhook_info()
    return webhook_info
