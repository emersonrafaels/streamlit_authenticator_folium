import sys
from pathlib import Path

from loguru import logger

def configure_logging(APP_NAME="APPNAME", LOG_LEVEL="INFO"):

    logger.add(APP_NAME,
               colorize=True,
               format="{time:DD/MM/YYYY HH:mm:ss} - {level} - [{file}] - {message}",
               level=LOG_LEVEL)

    return logger