import logging
import sys
from db.orm import create_tables


def configure():
    '''Configures all backend part of app.
    '''
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s:     [%(asctime)s] %(message)s',
                        datefmt="%d-%m-%Y %H:%M:%S")
    try:
        create_tables()
    except Exception as e:
        logging.critical(f"Error was occured during creating table: {e}")
        sys.exit()
