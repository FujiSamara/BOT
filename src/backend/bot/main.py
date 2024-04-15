from fastapi import FastAPI
from bot.configure import configure
from bot.bot import get_bot_logger
import sys

def create(app: FastAPI) -> FastAPI:
    bot = FastAPI()
    try:
        configure(bot)
    except Exception as e:
        get_bot_logger().critical(f"Bot configuring is failed: {e}")
        sys.exit()
    get_bot_logger().info("Bot created")
    app.mount(path='/bot', app=bot)
    return bot

