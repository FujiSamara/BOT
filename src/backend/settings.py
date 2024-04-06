from pydantic_settings import BaseSettings
from functools import lru_cache
import logging

class Settings(BaseSettings):
    pass

@lru_cache
def get_settings() -> Settings:
    '''Returns settings of app.

    Settings will be generate only for first call.
    '''
    try:
        settings = Settings()
        return settings
    except Exception as e:
        logging.critical(f"Settings generated with error: {e}")