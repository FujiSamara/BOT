from fastapi import FastAPI
from app.adapters.bot.configure import configure
import sys
import logging


def create(app: FastAPI) -> FastAPI:
    bot = FastAPI(docs_url=None, redoc_url=None)
    try:
        configure(bot)
    except Exception as e:
        logging.critical(f"Bot configuring is failed: {e}")
        sys.exit()
    logging.info("Bot created")
    app.mount(path="/bot", app=bot)
    return bot
