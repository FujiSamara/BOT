from fastapi import FastAPI
from bot.configure import configure, get_bot_logger
import asyncio
import sys

def create_bot(app: FastAPI) -> FastAPI:
    bot = FastAPI()
    try:
        asyncio.run(configure(bot))
    except Exception as e:
        get_bot_logger().critical(f"Bot configuring is failed: {e}")
        sys.exit()
    get_bot_logger().info("Bot created")
    app.mount(path='/bot', app=bot)
    return bot

