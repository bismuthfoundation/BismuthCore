"""
Helper Class and functions
"""

import logging


__version__ = '0.0.2'


def base_app_log(app_log=None):
    """Returns the best possible log handler if none is provided"""
    if app_log:
        return app_log
    elif logging.getLogger("tornado.application"):
        return logging.getLogger("tornado.application")
    else:
        return logging


class BismuthBase:
    """Base class for every core object needing app_log and config."""

    __slots__ = ('app_log', 'verbose', 'config')

    def __init__(self, app_log=None, config=None, verbose: bool=False):
        """Init and set defaults with fallback"""
        self.verbose = verbose
        self.config = config
        self.app_log = base_app_log(app_log)
