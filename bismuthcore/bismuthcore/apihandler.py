"""
API Command handler module for Bismuth nodes
@EggPoolNet
Needed for Json-RPC server or other third party interaction
"""

import threading

__version__ = "0.0.0"


"""
TODO: This is a scaffold from the legacy node.
Will need rework to be used with higher level abstraction, and no access to the db itself.
"""


class ApiHandler:
    """
    The API commands manager. Extra commands, not needed for node communication, but for third party tools.
    Handles all commands prefixed by "api_".
    It's called from client threads, so it has to be thread safe.
    """

    __slots__ = ('app_log', 'config', 'callback_lock', 'callbacks')

    def __init__(self, app_log, config=None):
        self.app_log = app_log
        self.config = config
        # Avoid mixing answers to commands with callbacks
        self.callback_lock = threading.Lock()
        # list of sockets that asked for a callback (new block notification)
        # Not used yet.
        self.callbacks = []

    def dispatch(self, method, socket_handler, ledger_db, peers):
        """
        Routes the call to the right method
        :return:
        """
        # Easier to ask forgiveness than ask permission
        try:
            """
            All API methods share the same interface. Not storing in properties since it has to be thread safe.
            This is not pretty, this will evolve with more modular code.
            Primary goal is to limit the changes in node.py code and allow more flexibility in this class, like some plugin.
            """
            result = getattr(self, method)(socket_handler, ledger_db, peers)
            return result
        except AttributeError:
            self.app_log.warning("API Method <{}> does not exist.".format(method))
            return False

