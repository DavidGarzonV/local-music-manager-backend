import logging
import datetime as dt
import os
from app.common.environments import IS_DEVELOPMENT
from app.common.utils import create_folder_if_not_exists

create_folder_if_not_exists("logs")

current_date = dt.date.today()

# create logger
logger_level = logging.ERROR
if IS_DEVELOPMENT:
    logger_level = logging.DEBUG

filename = os.path.join(
    os.path.dirname(__file__), "../logs/" + current_date.strftime("%d%m%Y") + ".log"
)
logging.basicConfig(filename=filename, encoding="utf-8", level=logger_level)
APP_LOGGER = logging.getLogger("local-music-manager")
APP_LOGGER.setLevel(logger_level)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logger_level)

# add ch to logger
APP_LOGGER.addHandler(ch)
