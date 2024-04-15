import logging
import sys
from db.orm import create_tables


def configure():
    '''Configures all backend part of app.
    '''
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    try:
        create_tables()
    except Exception as e:
        logging.critical(f"Error was occured during creating table: {e}")
        sys.exit()