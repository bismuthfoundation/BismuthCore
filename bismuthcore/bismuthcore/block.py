
"""
Bismuth core Block Class
"""

from bismuthcore.transaction import Transaction
from bismuthcore.transactionslist import TransactionsList
from typing import List

__version__ = "0.0.2"


class Block(TransactionsList):
    """A generic Bismuth Block with its transactions.
    Holds a single block only, and can provide extra info about the block"""

    # Inner storage is compact, binary form
    __slots__ = ('computed', 'tokens_operation_present')

    def __init__(self, transactions: List[Transaction], compute=False, check_txs=False, last_block_timestamp=0):
        """Default constructor with list of binary, non verbose,
        Transactions instances, mining transaction at the end."""
        super().__init__(transactions)
        self.tokens_operation_present = False
        self.computed = False
        if compute:
            self._compute()
        if check_txs:
            # TODO
            pass

    def _compute(self):
        # TODO: Update tokens_operation_present
        for transaction in self.transactions:
            # if transaction.operation in ["token:issue", "token:transfer"]:
            if transaction.operation.startswith("token"):
                    self.tokens_operation_present = True

        self.computed = True

