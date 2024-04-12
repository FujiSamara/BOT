from functools import lru_cache
from fastapi import FastAPI, Header
from typing import Annotated
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from contextlib import asynccontextmanager
from aiogram.types import Update, WebhookInfo
import logging
from settings import get_settings

def configure(bot_api: FastAPI):
    '''Configures fast api admin app.
    '''
    bot_api.add_api_route(path="/webhook", endpoint=_bot_webhook, methods=["POST"])
    _configure_dispatcher(get_dispatcher())

@asynccontextmanager
async def lifespan(_: FastAPI):
    await get_bot().set_webhook(
        url=get_settings().bot_webhook_url,
        secret_token=get_settings().telegram_token,
        allowed_updates=get_dispatcher().resolve_used_update_types(),
        drop_pending_updates=True
    )
    get_bot_logger().info(await _check_webhook())
    yield
    await get_bot().delete_webhook(drop_pending_updates=True)

@lru_cache
def get_dispatcher() -> Dispatcher:
    return Dispatcher()

@lru_cache
def get_bot() -> Bot:
    return Bot(token=get_settings().bot_token, parse_mode=ParseMode.HTML)

@lru_cache
def get_bot_logger() -> logging.Logger:
    return logging.getLogger("bot") 


async def _check_webhook() -> WebhookInfo | None:
    try:
        webhook_info = await get_bot().get_webhook_info()
        return webhook_info
    except Exception as e:
        raise

def _configure_dispatcher(dp: Dispatcher):
    '''Configures telegram dispatcher
    '''
    from bot.handlers import router
    dp.include_router(router)

async def _bot_webhook(update: dict,
                    x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None):
    '''Registers webhook endpoint for telegram bot'''
    if x_telegram_bot_api_secret_token != get_settings().telegram_token:
        get_bot_logger().error("Wrong secret token !")
        return {"status": "error", "message": "Wrong secret token !"}
    return await get_dispatcher().feed_update(bot=get_bot(), update=Update(**update))