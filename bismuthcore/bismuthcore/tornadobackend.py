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
from bismuthcore.combackend import ComBackend, ComClient

__version__ = '0.0.1'

# Some systems do not support reuse_port
REUSE_PORT = hasattr(socket, "SO_REUSEPORT")


class TornadoBackend(ComBackend):
    """Try at a tornado powered backend"""

    __slots__ = ('app_log', 'verbose', 'config', 'address', 'port', 'address', 'stop_event', 'node', 'async')

    def __init__(self, node, app_log=None, config=None, verbose: bool=False):
        super().__init__(node, app_log, config, verbose)
        self.async = True  # Tells whether this backend is async or not (else it would be threaded).
        self.app_log.info(f"Tornado: Init port {self.port} on address '{self.address}'.")

    def serve(self):
        """Begins to listen to the net"""
        self.app_log.info("Tornado: Serve")
        loop = asyncio.get_event_loop()
        if self.config.log_debug:
            loop.set_debug(True)
        try:
            server = TornadoComServer()
            server.verbose = self.verbose
            server.backend = self
            # server.listen(port)
            server.bind(self.port, backlog=128, address=self.address, reuse_port=REUSE_PORT)
            server.start(1)  # Forks multiple sub-processes
            self.app_log.info(f"Starting server on tcp://{self.address}:{self.port}, reuse_port={REUSE_PORT}")
            io_loop = IOLoop.instance()
            # io_loop.spawn_callback(self.node.manager)
            # self.node.connect()
            try:
                io_loop.start()
            except KeyboardInterrupt:
                self.node.stop_event.set()
                loop = asyncio.get_event_loop()
                # loop.run_until_complete(self.mempool.async_close())
                io_loop.stop()
                self.app_log.info("TornadoBackend: exited cleanly")
        except Exception as e:
            self.app_log.error(f"TornadoBackend Serve error: {e}")

    def stop(self):
        pass
        self.app_log.info("Tornado: Stop required")
        # TODO

    async def get_client(self, host, port):
        """ASYNC. Returns a connected ComClient instance, or None if connection wasn't possible"""
        pass
        # TODO - have the caller use await or not, or get the ioloop from here and call sync'd?


class TornadoComClient(ComClient):

    def __init__(self, host:str='', port: int=0, app_log=None):
        super().__init__(host, port, app_log)

    async def connect(self, host:str='', port: int=0):
        """Tries to connect and returns connected status"""
        if host:
            self.host = host
        if port:
            self.port = port
        self.app_log.info(f"TornadoComClient: connect to '{self.host}:{self.port}'.")


class TornadoComServer(TCPServer):
    """Tornado asynchronous TCP server."""

    def __init__(self):
        self.verbose = False
        self.backend = None
        self.app_log = None
        super().__init__()

    async def handle_stream(self, stream, address):
        """Async. Handles the lifespan of a client, from connection to end of stream"""
        peer_ip, fileno = address
        self.app_log.info(f"TornadoComServer: Incoming connection from {peer_ip}")
        try:
            # Get first message, we expect an hello with version number and address
            # msg = await async_receive(stream, peer_ip)
            pass
        except:
            pass
