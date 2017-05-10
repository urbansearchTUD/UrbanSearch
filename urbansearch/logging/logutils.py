import os
import logging
import logging.handlers

directory = './log/'


def _create_directory(dir_path):
    try:
        os.makedirs(dir_path, exist_ok=True)
    except OSError:
        # TODO do something useful?
        raise

_create_directory(directory)


log_formatter = logging.Formatter(
    fmt="[%(levelname)s] %(asctime)s || %(message)s"
)


file_handler = logging.handlers.RotatingFileHandler(
    '%surbansearch.log' % directory, mode='w', maxBytes=10000000, backupCount=5
)
file_handler.setFormatter(log_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)


def add_handlers(logger):
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def getLogger(name):
    logger = logging.getLogger(name)
    return logger

