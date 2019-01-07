# -*- coding: utf-8 -*-

"""Main module."""


import asyncio
import importlib
import logging

import aioprocessing

# from sys import exit

__version__ = '0.0.4'


class BismuthNode:
    """Main Bismuth node class. Should probably be a network backend agnostic class"""

    __slots__ = ('app_log', 'verbose', 'config', 'stop_event', 'com_backend', 'connecting')

    def __init__(self, app_log=None, config=None, verbose: bool=False,
                 com_backend_class_name: str='TornadoBackend'):
        """Init the node components"""
        self.verbose = verbose
        self.config = config
        self.connecting = False  # If true, manager tries to connect to peers
        if app_log:
            self.app_log = app_log
        elif logging.getLogger("tornado.application"):
            self.app_log = logging.getLogger("tornado.application")
        else:
            self.app_log = logging
        self.stop_event = aioprocessing.AioEvent()
        backend_class = getattr(importlib.import_module(f"bismuthcore.{com_backend_class_name.lower()}"), com_backend_class_name)
        self.com_backend = backend_class(self, app_log=app_log, config=config, verbose=verbose)
        self._check()

    def _check(self):
        """Initial check of all config, data and db"""
        if self.verbose:
            self.app_log.info("Node: Initial Check...")
        # TODO

    def run(self):
        """Begins to listen to the net"""
        if self.verbose:
            self.app_log.info("Node: Run")
        loop = asyncio.get_event_loop()
        self.com_backend.serve()
        """        
        while not self.stop_event.is_set():
            # This was to simulate some server
            loop.create_task(asyncio.sleep(1))
        """

    async def manager(self):
        """Background main coroutine"""
        self.app_log.info("Manager starting...")
        loop = asyncio.get_event_loop()
        while not self.stop_event.is_set():
            # TODO...
            """
            self.peers.manager_loop(target=worker)

            app_log.warning("Status: Threads at {} / {}".format(threading.active_count(), thread_limit_conf))
            app_log.info("Status: Syncing nodes: {}".format(syncing))
            app_log.info("Status: Syncing nodes: {}/3".format(len(syncing)))

            # Status display for Peers related info
            peers.status_log()
            """
            for i in range(self.config.node_pause):
                if not self.stop_event.is_set():
                    await asyncio.sleep(1)

        self.app_log.info("Manager stopped...")

    def connect(self, connect=True):
        self.connecting = connect

    def _finalize(self):
        """Maintenance method to be called when stopping"""
        self.com_backend.stop()  # May not be needed since the backend has access to our stop_event
        # TODO

    def stop(self):
        """Clean stop the node"""
        self.app_log.info("Node: Trying to close nicely...")
        self.stop_event.set()
        self._finalize()
        self.app_log.info("Bye!")
        # Emulate ctrl-c to have the backend loop stop
        raise KeyboardInterrupt
