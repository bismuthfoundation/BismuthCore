"""
BismuthConfig class, derived from legacy config.py
"""

import logging
from os import path
from pprint import pprint
from sys import exc_info

from bismuthcore.helpers import BismuthBase

__version__ = '0.0.4'


class BismuthConfig(BismuthBase):

    # "param_name": ["type", default_value]
    _vars={
        # Node items
        "node_port": ["int", 2829],
        # Should the node open it's listening interface? If not it won't accept incoming connections
        "node_listen": ["bool", True],
        # If not, won't do anything to the chain, won't try to connect, won't accept connections
        # Could be used to run a wallet or json-rpc server in a different process
        "node_active": ["bool", True],
        "node_timeout": ["int", 45],
        "node_address": ["str", ''],
        # "node_version": ["str", "mainnet0018"],
        # "node_version_allow": ["list", ['mainnet0017', 'mainnet0018', 'mainnet0019']],
        # "node_testnet": ["bool", False],
        "node_version": ["str", "testnet"],
        "node_version_allow": ["list", ['testnet']],
        "node_testnet": ["bool", True],
        # 51.15.97.143

        "node_regnet": ["bool", False],
        "node_thread_limit": ["int", 24], # Maximum number of connections to keep/allow
        "node_out_limit": ["int", 10],  # Number of active outgoing connections to start
        "node_pause": ["int", 5],
        "node_tor": ["bool", False],
        # "node_diff_recalc": ["int", 50000],
        # integrated json-rpc - planned only, see https://github.com/EggPool/BismuthRPC/tree/master/RPCServer
        "jsonrpc_port": ["int", 8115],
        "jsonrpc_listen": ["bool", True],  # Should the node open it's json-rpc listening interface?
        # integrated wallet server
        "walletserver_port": ["int", 8150],
        "walletserver_listen": ["bool", True],  # Should the node open it's wallet server listening interface?

        # Log related
        "log_debug": ["bool", False],
        "log_level": ["str", 'WARNING'],
        "log_components": ["list", ["connections", "peers", "mempool", "blocks"]],
        # db_prefixed items are low level objects for chain object only.
        "db_verify": ["bool", False],
        "db_rebuild": ["bool", True],
        "db_path": ["str", 'static/'],  # TODO: move to user owned directory
        "db_hyper_recompress": ["bool", True],
        "db_full_ledger": ["bool", True],
        # peers items
        "peers_purge": ["bool", True],
        "peers_ban_threshold": ["int", 30],
        "peers_allowed": ["str", '127.0.0.1,any'],
        "peers_reveal_address": ["bool", True],
        "peers_accept_peers": ["bool", True],
        "peers_banlist": ["list", []],
        "peers_whitelist": ["list", ['127.0.0.1']],
        "peers_ban_reset": ["int", 5],
        # mempool items
        "mempool_allowed": ["list", ['edf2d63cdf0b6275ead22c9e6d66aa8ea31dc0ccb367fad2e7c08a25', '4edadac9093d9326ee4b17f869b14f1a2534f96f9c5d7b48dc9acaed']],
        "mempool_ram_conf": ["bool", True],
        }

    def __init__(self, config_filename: str='', app_log=None, verbose: bool=False):
        """Fill config in, and use info from local config files if they exist."""
        super().__init__(app_log, verbose=verbose)
        # Default genesis to keep compatibility - Hardcoded, can't be changed by config.
        self.genesis = '4edadac9093d9326ee4b17f869b14f1a2534f96f9c5d7b48dc9acaed'

        # Load from default config so we have all needed params with default values
        for key, default in self._vars.items():
            if key not in self.__dict__:
                setattr(self, key, default[1])
            else:
                self.app_log.warning(f"Config: Trying to redefine protected key '{key}'.")

        # Load from local config
        # TODO: move to user owned directory
        if not config_filename:
            config_filename = 'config.txt'
        self._load_file(config_filename)
        # then override with optional custom config (won't be needed with user dir)
        # self._load_file("config_custom.txt")
        if self.verbose:
            pprint(self.__dict__)

    def get(self, key: str):
        """Safe getter, helper for config params"""
        if key not in self._vars:
            self.app_log.error(f"Config: Error '{key}' is an unknown config key.")
            if self.log_debug:
                # Then provide some back trace
                exc_type, exc_obj, exc_tb = exc_info()
                fname = path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                self.app_log.debug(f"Config: Type '{exc_type}' fname '{fname}' line {exc_tb.tb_lineno}.")
            return
        return self.__dict__.get(key, None)

    def _load_file(self, filename: str):
        """Load provided config file and append to current config"""
        if not path.exists(filename):
            return
        try:
            for line in open(filename):
                if '=' in line:
                    left, right = map(str.strip,line.rstrip("\n").split("="))
                    if left not in self._vars:
                        # Warn for unknown param?
                        continue
                    params = self._vars[left]
                    if params[0] == "int":
                        right = int(right)
                    elif params[0] == "list":
                        right = [item.strip() for item in right.split(",")]
                    elif params[0] == "bool":
                        if right.lower() in ["false", "0", "", "no"]:
                            right = False
                        else:
                            right = True
                    else:
                        # treat as "str"
                        pass
                    setattr(self,left,right)
        except Exception as e:
            self.app_log.error(f"Config: Error '{e}' reading '{filename}' config file.")
