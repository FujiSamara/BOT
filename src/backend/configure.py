import logging
import asyncio
from db.orm import create_tables


def configure():
    '''Configures all backend part of app.
    '''
    logging.basicConfig(level=logging.INFO, filename="server.log", filemode="w",
                        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    asyncio.run(create_tables())