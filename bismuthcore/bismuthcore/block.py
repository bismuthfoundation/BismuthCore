
"""
Bismuth core Block Class
"""

from bismuthcore.transaction import Transaction
from bismuthcore.transactionslist import TransactionsList
from typing import List
from bismuthcore.helpers import address_validate, address_is_rsa
from time import time as ttime
from polysign.signerfactory import SignerFactory
from base64 import b64decode, b64encode

__version__ = "0.0.2"


class Block(TransactionsList):
    """A generic Bismuth Block with its transactions.
    Holds a single block only, and can provide extra info about the block"""

    # Inner storage is compact, binary form
    __slots__ = ('computed', '_tokens_operation_present', '_last_block_timestamp', 'mining_reward')

    def __init__(self, transactions: List[Transaction], compute: bool=False, check_txs: bool=False, last_block_timestamp=0, mining_reward: int=0):
        """Default constructor with list of binary, non verbose,
        Transactions instances, mining transaction at the end."""
        super().__init__(transactions)
        self._last_block_timestamp = last_block_timestamp
        self._tokens_operation_present = None
        self.computed = False
        self.mining_reward = mining_reward
        if compute:
            self._compute()
        if check_txs:
            self._check_txs_fast()
            pass

    def _compute(self):
        # Update tokens_operation_present, without tx checks.
        self._tokens_operation_present = False
        for transaction in self.transactions:
            # if transaction.operation in ["token:issue", "token:transfer"]:
            if transaction.operation.startswith("token"):
                    self._tokens_operation_present = True

        self.computed = True

    def _check_txs_fast(self):
        """Fast checks - only light ones."""
        start_time = ttime()
        self._tokens_operation_present = False
        if self.miner_tx.amount != 0:
            raise ValueError("Coinbase (Mining) transaction must have zero amount")
        if not address_is_rsa(self.miner_tx.address):
            # Compare address rather than sig, as sig could be made up
            raise ValueError("Coinbase (Mining) transaction only supports legacy RSA Bismuth addresses")
        # str / float with regnet v2
        # print("TEMP TS TYPE", type(self.miner_tx.timestamp), type(self._last_block_timestamp))
        if self.miner_tx.timestamp <= self._last_block_timestamp:
            raise ValueError(f"!Block is older {self.miner_tx.timestamp} "
                             f"than the previous one {self._last_block_timestamp} , will be rejected")
        signature_list = set()
        for transaction in self.transactions:
            # if transaction.operation in ["token:issue", "token:transfer"]:
            if not transaction.signature:
                raise ValueError("Missing signature")
            signature_list.add(transaction.signature)
            if transaction.operation.startswith("token"):
                    self._tokens_operation_present = True
            if transaction.timestamp > start_time:
                raise ValueError(f"Future transaction not allowed, timestamp "
                                 f"{((transaction.timestamp - start_time) / 60):0.2f} minutes in the future")
            if self._last_block_timestamp - 86400 > transaction.timestamp:
                raise ValueError("Transaction older than 24h not allowed.")
        if len(self.transactions) != len(signature_list):
            raise ValueError("There are duplicate signatures in this block, rejected")

    def validate_mid(self):
        """More intensive checks"""
        # still easy ones
        for transaction in self.transactions:
            # Addresses validity
            if not address_validate(transaction.address):
                raise ValueError("Not a valid sender address")
            if not address_validate(transaction.recipient):
                raise ValueError("Not a valid recipient address")

    def validate_heavy(self):
        """More intensive checks - sigs checks"""
        for transaction in self.transactions:
            # EGG_EVO: Temp coherence control for db V2. TODO: Remove after more tests
            buffer2 = transaction.to_buffer_for_signing()
            if transaction.legacy_buffer != buffer2:
                print(f"Amount '{transaction.temp_amount}' Int {transaction.amount}")
                print("Legacy ", transaction.legacy_buffer)
                print("Buffer2", buffer2)

                raise ValueError("Buffer mismatch DB V2")
            # Will raise if error - also includes reconstruction of address from pubkey to make sure it matches
            # TODO: add a "raw" method in polysign so we avoid encode/recode
            """
            SignerFactory.verify_bis_signature(b64encode(transaction.signature).decode('utf-8'),
                                               b64encode(transaction.public_key).decode('utf-8'),
                                               buffer2, transaction.address)
            """
            SignerFactory.verify_bis_signature_raw(transaction.signature,
                                               transaction.public_key,
                                               buffer2, transaction.address)
            # TODO: node log
            # print(f"Valid signature from {transaction.address} to {transaction.recipient} amount {Transaction.int_to_f8(transaction.amount)}")
            """
            node.logger.digest_log.debug(f"Valid signature from {tx.received_address} "
                                         f"to {tx.received_recipient} amount {tx.received_amount}")
            """

    def tx_list_for_hash(self):
        """Returns the list of transactions of the block as legacy tuple format for block hash."""
        res = []
        for transaction in self.transactions:
            res.append(transaction.to_tuple_for_block_hash())
        return res

    @property
    def tokens_operation_present(self) -> bool:
        if self._tokens_operation_present is None:
            self._compute()
        return self._tokens_operation_present

    @property
    def miner_tx(self) -> Transaction:
        # Miner tx is the last one.
        return self.transactions[-1]

    @property
    def height(self)-> int:
        return self.transactions[-1].block_height

    def set_height(self, height: int) -> None:
        for transaction in self.transactions:
            transaction.block_height = height

    """
    def set_fee(self, fee: int) -> None:
        self.transactions[-1].fee = fee
    """

    def set_reward(self, reward: int) -> None:
        self.transactions[-1].reward = reward

    def set_hash(self, block_hash: bytes) -> None:
        for transaction in self.transactions:
            transaction.block_hash = block_hash
