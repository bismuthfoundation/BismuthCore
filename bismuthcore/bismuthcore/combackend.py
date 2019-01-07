"""
Communication classes ancestors.
"""

import logging
from abc import ABC, abstractmethod

__version__ = '0.0.2'


class ComBackend(ABC):
    """Abstract ancestor for Communication backends"""

    def __init__(self, node, app_log=None, config=None, verbose: bool = False):
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

    @abstractmethod
    def serve(self):
        pass

    @abstractmethod
    def stop(self):
        pass


class ComClient(ABC):
    """Abstract Ancestor for Communication clients"""

    def __init__(self, config, host: str = '', port: int = 0, app_log=None):
        self.async = True  # Tells whether this backend is async or not (else it would be threaded).
        self.config = config
        self.port = port
        self.host = host
        # TODO: factorize this app_log thing into a helper class
        if app_log:
            self.app_log = app_log
        elif logging.getLogger("tornado.application"):
            self.app_log = logging.getLogger("tornado.application")
        else:
            self.app_log = logging

    @abstractmethod
    def connect(self, host: str = '', port: int = 0):
        pass


class Connector(ABC):

    __slots__ = ('ip', 'app_log')

    def __init__(self, app_log, ip: str=''):
        self.app_log = app_log
        self.ip = ip

    @abstractmethod
    async def send_legacy(self, data):
        pass
