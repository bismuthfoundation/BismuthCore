"""
Communication classes ancestors.
"""

from abc import ABC, abstractmethod
from bismuthcore.helpers import base_app_log

__version__ = '0.0.2'


class ComBackend(ABC):
    """Abstract ancestor for Communication backends.
    A Communication Backend handles server as well as clients for a specific low level transport."""

    def __init__(self, node, app_log=None, config=None, verbose: bool = False):
        self.app_log = base_app_log(app_log)
        self.node = node
        self.verbose = verbose
        self.config = config
        self.port = config.get('node_port')
        self.address = config.get('node_address')

    @abstractmethod
    def serve(self):
        pass

    @abstractmethod
    def stop(self):
        pass


class ComClient(ABC):
    """Abstract Ancestor for Communication clients. Used for outgoing connections."""

    def __init__(self, config, host: str = '', port: int = 0, app_log=None):
        self.app_log = base_app_log(app_log)
        self.async = True  # Tells whether this backend is async or not (else it would be threaded).
        self.config = config
        self.port = port
        self.host = host

    @abstractmethod
    def connect(self, host: str = '', port: int = 0):
        pass


class Connector(ABC):
    """A Connector is a "channel" to send info back to the peer. It's backend agnostic."""

    __slots__ = ('ip', 'app_log')

    def __init__(self, app_log=None, ip: str=''):
        self.app_log = base_app_log(app_log)
        self.ip = ip

    @abstractmethod
    async def send_legacy(self, data):
        pass
