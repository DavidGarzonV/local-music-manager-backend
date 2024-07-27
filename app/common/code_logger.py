import logging
import datetime as dt
import os

from app.config import IS_DEVELOPMENT


folder = os.path.join(os.path.dirname(__file__), "../logs/")
if not os.path.exists(folder):
    os.makedirs(folder)

current_date = dt.date.today()

# create logger
filename = os.path.join(
    os.path.dirname(__file__), "../logs/" + current_date.strftime("%w%m%Y") + ".log"
)

logger_level = logging.ERROR
if IS_DEVELOPMENT:
    logger_level = logging.DEBUG
else:
    logging.basicConfig(filename=filename, encoding="utf-8", level=logger_level)

APP_LOGGER = logging.getLogger("local-music-manager")
APP_LOGGER.setLevel(logger_level)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logger_level)

# add ch to logger
APP_LOGGER.addHandler(ch)
