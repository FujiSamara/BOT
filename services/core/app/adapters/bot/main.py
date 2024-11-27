from fastapi import FastAPI
import sys

from app.infra.logging import logger

from app.adapters.bot.configure import configure


def create(app: FastAPI) -> FastAPI:
    bot = FastAPI(docs_url=None, redoc_url=None)
    try:
        configure(bot)
    except Exception as e:
        logger.critical(f"Bot configuring is failed: {e}")
        sys.exit()
    logger.info("Bot created")
    app.mount(path="/bot", app=bot)
    return bot
