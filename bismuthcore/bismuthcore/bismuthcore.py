# -*- coding: utf-8 -*-

"""Main module."""


"""
A all in one Bismuth node
"""

import logging


__version__ = '0.0.1'


class BismuthNode():
    """Main Bismuth node class"""

    __slots__ = ('app_log', 'verbose', 'config')

    def __init__(self, app_log=None, config=None, verbose: bool=False):
        """Init the node components"""
        self.verbose = verbose
        self.config = config
        if app_log:
            self.app_log = app_log
        elif logging.getLogger("tornado.application"):
            self.app_log = logging.getLogger("tornado.application")
        else:
            self.app_log = logging

    def check(self):
        """Initial check of all config, data and db"""

    def run(self):
        """Begins to listen to the net"""
