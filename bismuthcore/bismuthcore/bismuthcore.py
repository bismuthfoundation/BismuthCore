# -*- coding: utf-8 -*-

"""Main module."""


import asyncio
import importlib
from time import time

import aioprocessing
from bismuthcore.clientcommands import ClientCommands
from bismuthcore.helpers import BismuthBase
from tornado.ioloop import IOLoop

# from sys import exit

__version__ = '0.0.6'

CORE_COMMANDS =('version', 'getversion', 'hello', 'mempool')


class BismuthNode(BismuthBase):
    """Main Bismuth node class. Should probably be a network backend agnostic class"""

    __slots__ = ('stop_event', '_com_backend', 'connecting', 'startup_time', '_client_commands')

    def __init__(self, app_log=None, config=None, verbose: bool=False,
                 com_backend_class_name: str='TornadoBackend'):
        """Init the node components"""
        super().__init__(app_log, config, verbose)
        self.startup_time = time()
        self.connecting = False  # If true, manager tries to initiate outgoing connections to peers
        self.stop_event = aioprocessing.AioEvent()
        # load the backend class from the provided name
        backend_class = getattr(importlib.import_module(f"bismuthcore.{com_backend_class_name.lower()}"), com_backend_class_name)
        self._com_backend = backend_class(self, app_log=app_log, config=config, verbose=verbose)
        self._client_commands = ClientCommands(self)
        self._check()

    def _check(self) -> bool:
        """Initial check of all config, data and db"""
        if self.verbose:
            self.app_log.info("Node: Initial Check...")
        # TODO
        return True

    def run(self) -> None:
        """Begins to listen to the net"""
        if self.verbose:
            self.app_log.info("Node: Run")

        self._com_backend.serve()
        # TODO: start() the IOLoop from here, so we can start several servers (json-rpc, wallet server) in the loop.
        # Or create a new process per server? More sync issues or can play well?
        loop = IOLoop.current()
        try:
            loop.start()
        except KeyboardInterrupt:
            self.app_log.info("BismuthNode: got quit signal")
            self.stop_event.set()
            self._com_backend.stop()
            """
            # TODO: local cleanup if needed
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.mempool.async_close())
            except:
                pass
            """
            self.app_log.info("BismuthNode: exited cleanly")

    async def manager(self) -> None:
        """Background main co-routine"""
        self.app_log.info("Manager starting...")
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
            await self._async_wait(self.config.node_pause)

        self.app_log.info("Manager stopped...")

    async def process_legacy_command(self, command) -> None:
        """
        Dispatch command to the right handler. Called by the communication backend.

        TODO: make command an object
        """
        try:
            self.app_log.info(f"Got Legacy command {command['command']} from {command['connector'].ip}.")
            if command['command'] in ClientCommands.commands:
                await self._client_commands.process_legacy(command)
                return
            elif command['command'] not in CORE_COMMANDS:
                self.app_log.warning(f"Got unknown command '{command['command']}''")
            # TODO: process core commands hereafter

        except Exception as e:
            self.app_log.warning(f"Error {e} in process_legacy_command")

    def connect(self, connect: bool=True) -> None:
        """If connect is True, manager will try to connect to peers."""
        self.connecting = connect

    def thread_count(self) -> int:
        """Returns total count threads and/or clients + server coroutines running"""
        # TODO: add other servers count, too
        return self._com_backend.thread_count()

    async def _async_wait(self, seconds: int) -> None:
        for i in range(seconds):
            if not self.stop_event.is_set():
                await asyncio.sleep(1)

    def _finalize(self) -> None:
        """Maintenance method to be called when stopping"""
        self.com_backend.stop()  # May not be needed since the backend has access to our stop_event
        # TODO

    def stop(self) -> None:
        """Clean stop the node"""
        self.app_log.info("Node: Trying to close nicely...")
        self.stop_event.set()
        self._finalize()
        self.app_log.info("Bye!")
        # Emulate ctrl-c to have the backend loop stop
        raise KeyboardInterrupt
