import logging
import os
from swap.config import Config


def get_path(file):
    # Get log path
    path = os.path.dirname(os.path.abspath(file))
    path = os.path.join(path, '../logs')
    path = os.path.abspath(path)

    # Ensure log path exists
    if not os.path.exists(path):
        os.makedirs(path)

    return path


def init(name, path):
    path = get_path(path)
    logger = logging.getLogger(name)

    # pylint: disable=E1101
    c = Config()
    level = c.logging.level
    fname = c.logging.filename
    f_format = c.logging.file_format
    c_format = c.logging.console_format
    date_format = c.logging.date_format
    # pylint: enable=E1101

    # Set log level
    for i in range(0, 51, 10):
        if logging.getLevelName(i) == level:
            logger.setLevel(i)
            break

    # Create file handler
    fname = os.path.join(path, fname)
    handler = logging.FileHandler(fname)

    formatter = logging.Formatter(f_format, date_format)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(c_format, date_format)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    logger.info('Initialized logging')
