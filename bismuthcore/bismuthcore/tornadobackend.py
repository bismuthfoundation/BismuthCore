# -*- coding: utf-8 -*-

"""Main module."""

import asyncio
import json
import socket

from bismuthcore.combackend import ComBackend, ComClient, Connector
from bismuthcore.messages.basemessages import Message
from tornado.ioloop import IOLoop
# from tornado.options import define, options
# from tornado import gen
from tornado.iostream import IOStream
from tornado.tcpclient import TCPClient
from tornado.tcpserver import TCPServer

__version__ = '0.0.4'

# Some systems do not support reuse_port
REUSE_PORT = hasattr(socket, "SO_REUSEPORT")


class TornadoComClient(ComClient):
    """An async TCP client"""

    def __init__(self, config, host:str='', port: int=0, app_log=None):
        super().__init__(config, host, port, app_log)
        self.stream_handler = None

    async def connect(self, host:str='', port: int=0):
        """Tries to connect and returns connected status"""
        if host:
            self.host = host
        if port:
            self.port = port
        self.app_log.info(f"TornadoComClient: connect to '{self.host}:{self.port}'.")
        try:
            stream = await TCPClient().connect(self.host, self.port)
            if stream:
                self.app_log.info(f"Connected to {self.host}:{self.port}")
                self.stream_handler = LegacyStreamHandler(stream, self.app_log, self.host, self.port,
                                                          timeout=self.config.node_timeout)
        except Exception as e:
            self.app_log.warning(f"Could not connect to {self.host}:{self.port} ({e})")
            self.stream_handler = None

    def close(self):
        """Be sure to call this one, or the thread count won't be correct."""
        try:
            self.stream_handler.close()
        except:
            pass

    @property
    def connected(self) -> bool:
        if not self.stream_handler:
            return False
        if not self.stream_handler.stream:
            return False
        return True

    async def command(self, message: Message) -> bool:
        if not self.stream_handler:
            return None
        data = message.legacy_command
        param = message.to_legacy()
        # return await self.stream_handler._command(data, param)
        message.set_legacy_answer(await self.stream_handler._command(data, param))
        return True



class TornadoBackend(ComBackend):
    """Try at a tornado powered backend"""

    __slots__ = ('app_log', 'verbose', 'config', 'address', 'port', 'address', 'stop_event', 'node', 'async',
                 'threads')

    def __init__(self, node, app_log=None, config=None, verbose: bool=False):
        super().__init__(node, app_log, config, verbose)

        self.async = True  # Tells whether this backend is async or not (else it would be threaded).
        self.threads = 0  # Improper, these are co-routines.
        self.app_log.info(f"Tornado: Init port {self.port} on address '{self.address}'.")

    def serve(self) -> None:
        """Begins to listen to the net"""
        self.app_log.info("Tornado: Serve")
        loop = IOLoop.current()
        if self.config.log_debug:
            loop.set_debug(True)
        try:
            server = TornadoComServer(self, self.app_log, self.config, self.verbose)
            # server.listen(port)
            server.bind(self.port, backlog=128, address=self.address, reuse_port=REUSE_PORT)
            server.start(1)  # Forks multiple sub-processes

            self.app_log.info(f"Starting Tornado Server on tcp://{self.address}:{self.port}, reuse_port={REUSE_PORT}")

            # Local init
            loop.spawn_callback(self.node.manager)
            self.node.connect()

        except Exception as e:
            self.app_log.error(f"TornadoBackend Serve error: {e}")

    def stop(self) -> None:
        pass
        self.app_log.info("Tornado: Stop required")
        # TODO - local cleanup

    def thread_count(self) -> int:
        return self.threads

    async def get_client(self, host: str, port: int) -> TornadoComClient:
        """ASYNC. Returns a connected ComClient instance, or None if connection wasn't possible"""
        self.threads += 1
        client = TornadoComClient(self.config, host, port, app_log=self.app_log)
        await client.connect()
        return client

    def close_client(self, client: TornadoComClient) -> None:
        """Be sure to call this one, or the thread count won't be correct."""
        try:
            client.close()
            self.threads -= 1
        except:
            pass


class TornadoComServer(TCPServer):
    """Tornado asynchronous TCP server."""

    def __init__(self, backend, app_log, config, verbose: bool=False):
        self.backend = backend
        self.app_log = app_log
        self.config = config
        self.verbose = verbose
        super().__init__()

    async def handle_stream(self, stream, address):
        """Async. Handles the lifespan of a client, from connection to end of stream"""
        peer_ip, fileno = address
        self.app_log.info(f"TornadoComServer: Incoming connection from {peer_ip}")
        self.backend.threads += 1
        try:
            stream_handler = LegacyStreamHandler(stream, self.app_log, peer_ip, timeout=self.config.node_timeout)
            # Get first message, we expect an hello with version number and address
            # msg = await async_receive(stream, peer_ip)
            # msg = stream_handler.receive()
            msg = await stream_handler._receive()
            # print('TornadoComServer: got', msg)
            connector = TornadoConnector(self.app_log, stream, peer_ip)
            # TODO: depending on the command, wait for more packets
            command = {'command': msg, 'params': [], 'connector': connector}
            # TODO: use a core structure with from/to to convert ?
            # Convert here or in bismuthcore? or just use different classes like for the backend?
            await self.backend.node.process_legacy_command(command)
        except:
            pass
        finally:
            self.backend.threads -= 1


class LegacyStreamHandler:
    """A helper to process legacy low level protocol on top of async streams"""

    __slots__ = ('stream', 'app_log', 'loop', 'connected', 'ip', 'port', 'timeout')

    def __init__(self, stream: IOStream, app_log, ip: str='', port: int=0, loop: IOLoop=None, timeout=45):
        self.stream = stream
        self.app_log = app_log
        self.loop = loop if loop else IOLoop.current()
        """
        print(loop)
        print(asyncio.get_event_loop())
        print(IOLoop.instance())
        """
        self.connected = False
        self.ip = ip
        self.port = port
        self.timeout = timeout

    def close(self):
        if self.stream:
            self.stream.close()
            self.stream = None

    async def _receive(self):
        """Async. Get a command"""
        if self.stream:
            header = await self.stream.read_bytes(10)
            data_len = int(header)
            data = await self.stream.read_bytes(data_len)
            data = json.loads(data.decode("utf-8"))
            return data
        else:
            self.app_log.warning('receive: not connected')

    def receive(self, timeout=None):
        future = asyncio.run_coroutine_threadsafe(self._receive(), self.loop)
        return future.result(timeout)

    def send(self, data, timeout=None):
        future = asyncio.run_coroutine_threadsafe(self._send(data), self.loop)
        return future.result(timeout)

    def command(self, data, param=None, timeout=None):
        future = asyncio.run_coroutine_threadsafe(self._command(data, param), self.loop)
        return future.result(timeout)

    async def _send(self, data):
        """"sends an object to the stream, async."""
        if self.stream:
            try:
                data = str(json.dumps(data))
                header = str(len(data)).encode("utf-8").zfill(10)
                full = header + data.encode('utf-8')
                await self.stream.write(full)
            except Exception as e:
                self.app_log.error(f"send_to_stream {e} for ip {self.ip}:{self.port}")
                self.stream = None
                raise
        else:
            self.app_log.warning('send: not connected')

    async def _command(self, data, param=None):
        if self.stream:
            await self._send(data)
            if param:
                await self._send(param)
            return await self._receive()
        else:
            self.app_log.warning('command: not connected')
            return None


class TornadoConnector(Connector):

    __slots__ = ('stream', )

    def __init__(self, app_log, stream: IOStream, ip: str=''):
        super().__init__(app_log, ip)
        self.stream = stream

    async def send_legacy(self, data):
        if self.stream:
            try:
                data = str(json.dumps(data))
                header = str(len(data)).encode("utf-8").zfill(10)
                full = header + data.encode('utf-8')
                await self.stream.write(full)
            except Exception as e:
                self.app_log.error(f"send_to_stream {e} for ip {self.ip}:{self.port}")
                self.stream = None
                raise
        pass
