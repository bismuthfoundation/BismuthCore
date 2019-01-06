# -*- coding: utf-8 -*-

"""Main module."""

import aioprocessing
import asyncio
import logging
import socket
from tornado.ioloop import IOLoop
# from tornado.options import define, options
# from tornado import gen
from tornado.iostream import StreamClosedError
from tornado.tcpclient import TCPClient
from tornado.tcpserver import TCPServer

__version__ = '0.0.1'

# Some systems do not support reuse_port
REUSE_PORT = hasattr(socket, "SO_REUSEPORT")


class TornadoBackend:
    """Try at a tornado powered backend"""

    __slots__ = ('app_log', 'verbose', 'config', 'address', 'port', 'address', 'stop_event', 'node')

    def __init__(self, node, app_log=None, config=None, verbose: bool=False):
        self.node = node
        self.verbose = verbose
        self.config = config
        self.port = int(config.get('node_port'))
        self.address = config.get('node_address')
        if app_log:
            self.app_log = app_log
        elif logging.getLogger("tornado.application"):
            self.app_log = logging.getLogger("tornado.application")
        else:
            self.app_log = logging

        self.app_log.info(f"Tornado: Init port {self.port} on address '{self.address}'.")

    def serve(self):
        """Begins to listen to the net"""
        self.app_log.info("Tornado: Serve")
        # TODO

    def stop(self):
        pass
