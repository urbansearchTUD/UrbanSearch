"""
Provide utils to enable logging. Example use:

LOGGER = logutils.getLogger(__name__)
logutils.add_handlers(LOGGER)
logutils.set_loglevel(LOGGER, logutils.logging.DEBUG)

def function_example:
    Logger.debug("Debug statement..")


"""

import os
import logging
import logging.handlers

# TODO Move to config? And absolute/relative choice
directory = './log/'

# Format of the lines in the log
log_formatter = logging.Formatter(
    fmt="[%(levelname)s] %(asctime)s || %(message)s"
)

# Rotating log with 5 backups
file_handler = logging.handlers.RotatingFileHandler(
    '%surbansearch.log' % directory, mode='w', maxBytes=10000000, backupCount=5
)
file_handler.setFormatter(log_formatter)

# Enable log output on console
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

try:
    # Create log directory if non-existent
    if not os.path.exists(PATH):
        os.makedirs(PATH)
except OSError:
    raise FileNotFoundError('Could not create log directory')


def add_handlers(logger):
    """
    Add all available handlers to the logger.

    :param logger: logging.Logger instance where handlers will be added to.
    """
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def add_file_handler(logger):
    """
    Add file handler to logger, will log into urbansearch.log files.

    :param logger: logging.Logger instance where handlers will be added to.
    """
    logger.addHandler(file_handler)


def add_console_handler(logger):
    """
    Add console handler to logger, will log output to console.

    :param logger: logging.Logger instance where handlers will be added to.
    """
    logger.addHandler(console_handler)


def getLogger(name):
    """
    Create and return a logging.Logger with given name

    :param name: Name of logger to be created
    :return: logging.Logger with name

    """
    logger = logging.getLogger(name)
    return logger


def set_loglevel(logger, level):
    """
    Change loglevel of logger to level. Standard levels available are:

    CRITICAL    50
    ERROR       40
    WARNING     30
    INFO        20
    DEBUG       10
    NOTSET      0

    :param logger: logging.Logger instance
    :param level: Loglevel
    """
    logger.setLevel(level)
    print("Loglevel of %s changed to: %s", (logger,
                                            logging.getLevelName(level))
