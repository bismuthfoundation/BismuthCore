# -*- coding: utf-8 -*-

"""Main module."""


import asyncio
import importlib
from time import time

import aioprocessing
from bismuthcore.clientcommands import ClientCommands
from bismuthcore.messages.coremessages import VersionMessage
from bismuthcore.helpers import BismuthBase
from tornado.ioloop import IOLoop
from tornado.iostream import StreamClosedError
from sys import exc_info
from os import path

# from sys import exit

__version__ = '0.0.6'

CORE_COMMANDS =('version', 'getversion', 'hello', 'mempool')


class BismuthNode(BismuthBase):
    """Main Bismuth node class. Should probably be a network backend agnostic class"""

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
        self._clients = {}  # outgoing connections

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
            await self.reach_out()
            await self._async_wait()

        self.app_log.info("Manager stopped...")

    async def reach_out(self) -> None:
        """Tries to connect to distant peers until node_out_limit is reached"""
        if not self.connecting:
            return
        # Early exits allow to limit indentation levels and is more readable.
        if len(self._clients) >= self.config.node_out_limit:
            return
        for peer in [('35.227.90.114', 2829), ('51.15.97.143', 2829), ('163.172.163.4', 2829), ('94.113.207.67', 2829)]:
            # TODO: take from file ofc
            ip, port = peer
            if ip not in self._clients:
                io_loop = IOLoop.current()
                io_loop.spawn_callback(self.client_worker, ip, port)

    async def client_worker(self, ip:str, port:int) -> None:
        """Background co-routine handling outgoing connections to peers"""
        if ip in self._clients:
            return  # safety
        """
        dict_ip = {'ip': ip}
        self.plugin_manager.execute_filter_hook('peer_ip', dict_ip)
        if self.peers.is_banned(ip) or dict_ip['ip'] == 'banned':
            self.app_log.warning(f"IP {ip} is banned, won't connect")
            return
        """
        if 'connections' in self.config.log_components:
            self.app_log.info(f"Trying to reach out to {ip}:{port}.")
        try:
            self._clients[ip] = {'client': None}
            # TODO: possible to have a different backend depending on the port?
            client = await self._com_backend.get_client(ip, str(port))
            if not client.connected:
                return
            self._clients[ip] = {'client': client}
            self.app_log.debug(f"Status: Threads at {self.thread_count()}")
            # TODO: extend client object to store all what needed, use straight key => client
            # Communication starter
            message = VersionMessage(self.config.node_version)
            await client.command(message)
            self.app_log.debug(f"Sent version {self.config.node_version} to {ip}:{port}, got {message}")
            # if answer.valid:  # Make command and answer objects with no presupposed transport format
            if message.valid_answer():
                print('valid')
            else:
                print('invalid')
                return

            while client.connected:
                if 'connections' in self.config.log_components:
                    self.app_log.info(f"Still connected to {ip}:{port}.")
                await self._async_wait()

        except StreamClosedError as e:
            if 'connections' in self.config.log_components:
                self.app_log.warning(f"Lost connection to {ip}:{port} because '{e}'.")
                return
            # TODO: add to wait list not to try again too soon
        except Exception as e:
            # Here, we face a local code issue rather than network error.
            self.app_log.warning(f"Lost connection to {ip}:{port} because '{e}'.")
            # TODO: we may factorize that in an helper
            exc_type, exc_obj, exc_tb = exc_info()
            fname = path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.app_log.debug(f"client_worker: Unexpected '{exc_type}' fname '{fname}' line {exc_tb.tb_lineno}.")
            return
        finally:
            try:
                # We could keep it and set to inactive, but is it useful? could grow too much
                # use a timeout?
                self._com_backend.close_client(self._clients[ip]['client'])
                del self._clients[ip]
                self.app_log.debug("Status: Threads at {} / {}".format(self.thread_count()))
            except:
                pass

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

    async def _async_wait(self, seconds: int=0) -> None:
        if not seconds:
            seconds = self.config.node_pause
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
