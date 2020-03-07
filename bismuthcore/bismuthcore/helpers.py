"""
Helper Class and functions
"""

import logging
import requests
from abc import ABC, abstractmethod
from decimal import Decimal, getcontext, ROUND_HALF_EVEN
from sqlite3 import Binary
from base64 import b64decode, b64encode
from bismuthcore.compat import quantize_eight

__version__ = '0.0.4'


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
Migrated from essentials
"""


def fee_calculate(openfield: str, operation: str='', block: int=0) -> Decimal:
    # block var is no more needed, kept for interface retro compatibility
    fee = Decimal("0.01") + (Decimal(len(openfield)) / Decimal("100000"))  # 0.01 dust
    if operation == "token:issue":
        fee = Decimal(fee) + Decimal("10")
    if openfield.startswith("alias="):
        fee = Decimal(fee) + Decimal("1")
    if operation == "alias:register":  # Take fee into account even if the protocol is not live yet.
        fee = Decimal(fee) + Decimal("1")
    return quantize_eight(fee)


def just_int_from(s):
    return int(''.join(i for i in s if i.isdigit()))


def download_file(url: str, filename: str) -> None:
    """Download a file from URL to filename

    :param url: URL to download file from
    :param filename: Filename to save downloaded data as

    returns `filename`
    """
    try:
        r = requests.get(url, stream=True)
        total_size = int(r.headers.get('content-length')) / 1024

        with open(filename, 'wb') as fp:
            chunkno = 0
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    chunkno = chunkno + 1
                    if chunkno % 10000 == 0:  # every x chunks
                        print(f"Downloaded {int(100 * (chunkno / total_size))} %")

                    fp.write(chunk)
                    fp.flush()
            print("Downloaded 100 %")
    except:
        raise


"""
User input sanitization
"""


def sanitize_address(address: str) -> str:
    # Could use polysign to further check if it's valid. not sure it(s worth it at this stage.
    # There, it's to avoid easy exploits, not fully validate.
    return str(address)[:56]


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
