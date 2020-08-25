"""
Bismuth core Blocks Class
"""

from bismuthcore.transaction import Transaction
from bismuthcore.block import Block
from typing import List
import sys

__version__ = "0.0.1"


class Blocks():
    """A generic List of Bismuth Blocks.
    """
    __slots__ = ("blocks", "_tx_count")

    def __init__(self, blocks: List[Block], first_level_checks: bool=False):
        """Default constructor with list of Block objects,
        """
        self.blocks = blocks
        self._tx_count = None
        if first_level_checks:
            self._check_txs()

    def _check_txs(self):
        """First level of sanity checks"""
        # TODO
        pass

    @property
    def tx_count(self):
        if self._tx_count is None:
            self._tx_count = 0
            for block in self.blocks:
                self._tx_count += len(block.transactions)
        return self._tx_count

    @classmethod
    def from_legacy_block_data(cls, block_data: List[list], first_level_checks: bool=False, last_block_timestamp=0):
        blocks = []
        for legacy_block in block_data:
            tx_list = [Transaction.from_legacy_params(timestamp=tx[0], address=tx[1], recipient=tx[2], amount=tx[3],
                                                      signature=tx[4], public_key=tx[5], operation=tx[6],
                                                      openfield=tx[7]) for tx in legacy_block]
            block = Block(tx_list, check_txs=first_level_checks, last_block_timestamp=last_block_timestamp)
            blocks.append(block)
        return cls(blocks, first_level_checks=first_level_checks)




