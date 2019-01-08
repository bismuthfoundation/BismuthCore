"""
Commands handler

These are the core commands used by the client and wallets, but not part of the core node protocol.
"""

from time import time
from bismuthcore.helpers import Commands

__version__ = '0.0.1'


class ClientCommands(Commands):

    commands = ('statusjson', )

    async def process_legacy(self, command):
        try:
            if command['command'] == 'statusjson':
                if True:  # peers.is_allowed(peer_ip, data):
                    uptime = int(time() - self.node.startup_time)
                    diff, _ = [-1, -1]  # TODO self.chain.difficulty(c)
                    last_block = 0  # TODO
                    # TODO: depends on async or not.
                    threads = self.node.thread_count()  # threading.active_count()

                    if self.config.peers_reveal_address:
                        revealed_address = 'TODO'  # TODO self.wallet.address
                    else:
                        revealed_address = "private"

                    status = {"protocolversion": self.config.node_version,
                              "address": revealed_address,
                              "walletversion": __version__,
                              "testnet": self.config.node_testnet,
                              "blocks": last_block, "timeoffset": 0,
                              "connections": -1,  # self.node.peers.consensus_size,
                              "connections_list": [],  # self.node.peers.peer_ip_list,
                              "difficulty": diff,  # live status, bitcoind format
                              "threads": threads,
                              "uptime": uptime, "consensus": [],  # self.node.peers.consensus,
                              "consensus_percent": 50,  # self.node.peers.consensus_percentage,
                              "server_timestamp": f'{time():.2f}'}  # extra data
                    if self.config.node_regnet:
                        status['regnet'] = True
                    await command['connector'].send_legacy(status)
                else:
                    self.app_log.warning(f"{command['ip']} not whitelisted for statusjson command")
        except Exception as e:
            self.app_log.warning(f"Error {e} in process_legacy_client_command")

