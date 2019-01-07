# -*- coding: utf-8 -*-

"""Main module."""


import asyncio
import importlib
import logging

from time import time
import aioprocessing

# from sys import exit

__version__ = '0.0.5'

CLIENT_COMMANDS = ('statusjson', )

CORE_COMMANDS =('version', 'getversion', 'hello', 'mempool')


class BismuthNode:
    """Main Bismuth node class. Should probably be a network backend agnostic class"""

    __slots__ = ('app_log', 'verbose', 'config', 'stop_event', 'com_backend', 'connecting', 'startup_time')

    def __init__(self, app_log=None, config=None, verbose: bool=False,
                 com_backend_class_name: str='TornadoBackend'):
        """Init the node components"""
        self.startup_time = time()
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
        self.com_backend.serve()
        """        
        loop = asyncio.get_event_loop()
        while not self.stop_event.is_set():
            # This was to simulate some server
            loop.create_task(asyncio.sleep(1))
        """

    async def manager(self):
        """Background main coroutine"""
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
            for i in range(self.config.node_pause):
                if not self.stop_event.is_set():
                    await asyncio.sleep(1)
            # print('.')

        self.app_log.info("Manager stopped...")

    async def process_legacy_command(self, command):
        """Dispatch command to the right handler"""
        # print(command)  # {'command': 'statusjson', 'params': [], 'ip', 'connector'}
        try:
            self.app_log.info(f"Got Legacy command {command['command']} from {command['connector'].ip}.")
            if command['command'] in CLIENT_COMMANDS:
                await self.process_legacy_client_command(command)
                return
            elif command['command'] not in CORE_COMMANDS:
                self.app_log.warning(f"Got unknown command '{command['command']}''")
            # TODO: process core commands

        except Exception as e:
            self.app_log.warning(f"Error {e} in process_legacy_command")

    async def process_legacy_client_command(self, command):
        try:
            """Usual Client command - TODO: To be moved in a module of its own"""
            if command['command'] == 'statusjson':
                if True:  # peers.is_allowed(peer_ip, data):
                    uptime = int(time() - self.startup_time)
                    diff, _ = [-1, -1]  # TODO self.chain.difficulty(c)
                    last_block = 0  # TODO
                    # TODO: depends on async or not.
                    threads = 1  # threading.active_count()

                    if self.config.peers_reveal_address:
                        revealed_address = 'TODO'  # TODO self.wallet.address
                    else:
                        revealed_address = "private"

                    status = {"protocolversion": self.config.node_version,
                              "address": revealed_address,
                              "walletversion": __version__,
                              "testnet": self.config.node_testnet,
                              "blocks": last_block, "timeoffset": 0,
                              "connections": -1,  # self.peers.consensus_size,
                              "connections_list": [],  # self.peers.peer_ip_list,
                              "difficulty": diff,  # live status, bitcoind format
                              "threads": threads,
                              "uptime": uptime, "consensus": [],  # peers.consensus,
                              "consensus_percent": 50,  # peers.consensus_percentage,
                              "server_timestamp": f'{time():.2f}'}  # extra data
                    if self.config.node_regnet:
                        status['regnet'] = True
                    await command['connector'].send_legacy(status)
                else:
                    app_log.warning(f"{command['ip']} not whitelisted for statusjson command")
        except Exception as e:
            self.app_log.warning(f"Error {e} in process_legacy_client_command")

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
