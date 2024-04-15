from fastapi import FastAPI
from typing import AsyncGenerator
from aiogram import Dispatcher
from bot.router import router
from settings import get_settings
from bot.bot import get_bot, get_dispatcher, _bot_webhook, _check_webhook
import logging 
from aiogram.loggers import dispatcher, event, middlewares, scene, webhook

def configure(bot_api: FastAPI):
    '''Configures fast api admin app.
    '''
    bot_api.add_api_route(path="/webhook", endpoint=_bot_webhook, methods=["POST"])
    _configure_dispatcher(get_dispatcher())

    # Disables aiogram loggers
    dispatcher.propagate = False
    event.propagate = False
    middlewares.propagate = False
    scene.propagate = False
    webhook.propagate = False
    

async def lifespan(_: FastAPI) -> AsyncGenerator:
    await get_bot().delete_webhook(drop_pending_updates=True)
    await get_bot().set_webhook(
        url=get_settings().bot_webhook_url,
        secret_token=get_settings().telegram_token,
        allowed_updates=get_dispatcher().resolve_used_update_types(),
        drop_pending_updates=True
    )
    logging.getLogger("uvicorn.error").info("Webhook info: " + str(await _check_webhook()))
    yield
    await get_bot().delete_webhook(drop_pending_updates=True)
    yield

def _configure_dispatcher(dp: Dispatcher):
    '''Configures telegram dispatcher
    '''
    dp.include_router(router)
