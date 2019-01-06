# -*- coding: utf-8 -*-

"""Main module."""


import logging


__version__ = '0.0.2'


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

        self.check()

    def check(self):
        """Initial check of all config, data and db"""
        if self.verbose:
            self.app_log.info("Node: Initial Check...")

    def run(self):
        """Begins to listen to the net"""
        if self.verbose:
            self.app_log.info("Node: Run")
