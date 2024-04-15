from fastapi import FastAPI
from bot.configure import configure
import sys
import logging

def create(app: FastAPI) -> FastAPI:
    bot = FastAPI()
    try:
        configure(bot)
    except Exception as e:
        logging.critical(f"Bot configuring is failed: {e}")
        sys.exit()
    logging.info("Bot created")
    app.mount(path='/bot', app=bot)
    return bot

