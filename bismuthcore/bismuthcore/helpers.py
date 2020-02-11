"""
Helper Class and functions
"""

import logging
from abc import ABC, abstractmethod
from decimal import Decimal, getcontext, ROUND_HALF_EVEN
from sqlite3 import Binary
from base64 import b64decode, b64encode

__version__ = '0.0.3'


def base_app_log(app_log=None):
    """Returns the best possible log handler if none is provided"""
    if app_log:
        return app_log
    elif logging.getLogger("tornado.application"):
        return logging.getLogger("tornado.application")
    else:
        return logging


class BismuthBase:
    """Base class for every core object needing app_log and config."""

    __slots__ = ('app_log', 'verbose', 'config')

    def __init__(self, app_log=None, config=None, verbose: bool=False):
        """Init and set defaults with fallback"""
        self.app_log = base_app_log(app_log)
        self.verbose = verbose
        self.config = config


class Commands(ABC):

    commands = None

    def __init__(self, node):
        self.node = node
        self.app_log = node.app_log
        self.verbose = node.verbose
        self.config = node.config

    @abstractmethod
    def process_legacy(self, command):
        pass


"""
Temporary benchmarking helpers - Potential dup code
"""

getcontext().rounding = ROUND_HALF_EVEN
# Multiplier to convert floats to int
DECIMAL_1E8 = Decimal(100000000)


def int_to_f8(an_int: int):
    """Helper function to convert an int amount - inner format - to legacy string 0.8f """
    return str('{:.8f}'.format(Decimal(an_int) / DECIMAL_1E8))


def f8_to_int(a_str: str):
    """Helper function to convert a legacy string 0.8f to compact int format"""
    return int(Decimal(a_str) * DECIMAL_1E8)


def native_tx_to_bin_sqlite(tx):
    """
    Converts a native tuple tx into a bin tuple for sqlite
    :param tx:
    :return:
    """
    return (tx[0], tx[1], tx[2], tx[3], f8_to_int(tx[4]), Binary(b64decode(tx[5])),
            Binary(b64decode(tx[6])), Binary(b64decode(tx[7])), f8_to_int(tx[8]), f8_to_int(tx[9]), tx[10], tx[11])


class TxConverter():

    @staticmethod
    def native_tx_to_bin_sqlite(tx):
        """
        Converts a native tuple tx into a bin tuple for sqlite
        :param tx:
        :return:
        """
        return (tx[0], tx[1], tx[2], tx[3], f8_to_int(tx[4]), Binary(b64decode(tx[5])),
                Binary(b64decode(tx[6])), Binary(b64decode(tx[7])), f8_to_int(tx[8]), f8_to_int(tx[9]), tx[10], tx[11])
