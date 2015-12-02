# coding=utf-8

import logging
from logging.handlers import RotatingFileHandler

# Global variable definition
TORTILLADEBUG = True
logger = None


def initialize_logger(redfish_logfile):
    """Return api version.

    :param redfish_logfile: redfish log
    :type str
    :returns:  True

    """
    global logger
    logger = logging.getLogger()
    
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s :: %(levelname)s :: %(message)s'
        )
    file_handler = RotatingFileHandler(redfish_logfile, 'a', 1000000, 1)

    # First logger to file
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Second logger to console
    steam_handler = logging.StreamHandler()
    steam_handler.setLevel(logging.DEBUG)
    logger.addHandler(steam_handler)
    return True