"""
Bismuth core structures
"""

import json
from decimal import Decimal, getcontext, ROUND_HALF_EVEN
from base64 import b64decode, b64encode

__version__ = '0.0.1'

# Multiplier to convert floats to int
DECIMAL_1E8 = Decimal(100000000)

# Keys of the Json object
TRANSACTION_KEYS = ('block_height', 'timestamp', 'sender', 'recipient', 'amount', 'signature', 'public_key',
                    'block_hash', 'fee', 'reward', 'operation', 'openfield'
                    'format')

getcontext().rounding = ROUND_HALF_EVEN


"""
Transaction
"""


class Transaction:
    """A generic Bismuth Transaction"""

    # Inner storage is compact, binary form
    __slots__ = ('block_height', 'timestamp', 'sender', 'recipient', 'amount', 'signature', 'public_key',
                 'block_hash', 'fee', 'reward', 'operation', 'openfield')

    def __init__(self, block_height: int=0, timestamp: float=0, sender: bytes=b'', recipient: bytes=b'',
                 amount: int=0, signature: bytes=b'', public_key: bytes=b'', block_hash: bytes=b'', fee: int=0,
                 reward: int=0, operation: str='', openfield: str=''):
        """Default constructor with binary, non verbose, parameters"""
        self.block_height = block_height
        self.timestamp = timestamp
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature
        self.public_key = public_key
        self.block_hash = block_hash
        self.fee = fee
        self.reward = reward
        self.operation = operation
        self.openfield = openfield

    @staticmethod
    def int_to_f8(an_int: int):
        """Helper function to convert an int amount - inner format - to legacy string 0.8f """
        return str('{:.8f}'.format(Decimal(an_int) / DECIMAL_1E8))

    @staticmethod
    def f8_to_int(a_str: str):
        """Helper function to convert a legacy string 0.8f to compact int format"""
        return int(Decimal(a_str) * DECIMAL_1E8)

    """
    Alternate constructors
    """

    @classmethod
    def from_legacy_params(cls, block_height: int=0, timestamp: float=0, sender: str='', recipient: str='',
                           amount: str='0', signature: str = '', public_key: str='', block_hash: str='',
                           fee: str='0', reward: str='0', operation: str='', openfield: str='',):
        """
        Create from legacy - verbose - parameters.
        Call as tx = Transaction.from_legacy_params(0, '', 0 ...)
        """
        int_amount = Transaction.f8_to_int(amount)
        int_fee = Transaction.f8_to_int(fee)
        int_reward = Transaction.f8_to_int(reward)
        # public_key and signature are hex encoded then b64 encoded in legacy format.
        bin_public_key = bytes.fromhex(b64decode(public_key))
        bin_signature = bytes.fromhex(b64decode(signature))
        # whereas block hash only is hex encoded.
        bin_block_hash = bytes.fromhex(block_hash)
        # As well as sender and recipient
        bin_sender = bytes.fromhex(sender)
        bin_recipient = bytes.fromhex(recipient)
        return cls(block_height, timestamp, bin_sender, bin_recipient, int_amount, bin_signature, bin_public_key,
                   bin_block_hash, int_fee, int_reward, operation, openfield)

    @classmethod
    def from_legacy(cls, tx: list):
        """
        Create from legacy - verbose - parameters.
        Call as tx = Transaction.from_legacy(tx_list)
        """
        if len(tx) == 11:
            # legacy tx list can omit the blockheight (like for mempool)
            tx.insert(0, 0)
        block_height, timestamp, sender, recipient, amount, signature, \
            public_key, block_hash, fee, reward, operation, openfield = tx
        int_amount = Transaction.f8_to_int(amount)
        int_fee = Transaction.f8_to_int(fee)
        int_reward = Transaction.f8_to_int(reward)
        bin_public_key = bytes.fromhex(b64decode(public_key))
        bin_signature = bytes.fromhex(b64decode(signature))
        bin_block_hash = bytes.fromhex(block_hash)
        bin_sender = bytes.fromhex(sender)
        bin_recipient = bytes.fromhex(recipient)
        return cls(block_height, timestamp, bin_sender, bin_recipient, int_amount, bin_signature, bin_public_key,
                   bin_block_hash, int_fee, int_reward, operation, openfield)

    @classmethod
    def from_protobuf(cls, protobuf):
        """
        Create from a protobuf buffer.
        Call as tx = Transaction.from_protobuf(buffer)
        """
        raise AssertionError("TODO")
        # TODO
        return cls()

    @classmethod
    def from_json(cls, json_payload: str):
        """
        Create from json object.
        Call as tx = Transaction.from_json(json_string)

        json can either contain public_key and sign as legacy str (b64 encoded hex) or as bytes.
        In either case, amount will be as string, 0.8f

        This method tries to be as forgiveable as possible at import. However it *can't* import with amounts as int.
        """
        payload = json.loads(json_payload)
        if isinstance(payload['amount'], Decimal):
            # amounts are as Decimal, convert to int
            int_amount = int(payload['amount'] * DECIMAL_1E8)
            int_fee = int(payload['fee'] * DECIMAL_1E8)
            int_reward = int(payload['reward'] * DECIMAL_1E8)
        elif isinstance(payload['amount'], float):
            # amounts are as float, convert to int
            int_amount = int(payload['amount'] * DECIMAL_1E8)
            int_fee = int(payload['fee'] * DECIMAL_1E8)
            int_reward = int(payload['reward'] * DECIMAL_1E8)
        else:
            int_amount = Transaction.f8_to_int(payload['amount'])
            int_fee = Transaction.f8_to_int(payload['fee'])
            int_reward = Transaction.f8_to_int(payload['reward'])

        if isinstance(payload['sender'], str):
            # addresses are hex encoded, convert to bin inplace
            payload['sender'] = bytes.fromhex(payload['sender'])
            payload['recipient'] = bytes.fromhex(payload['recipient'])
        if isinstance(payload['public_key'], str):
            # We got legacy encoded strings, convert to bin
            bin_public_key = bytes.fromhex(b64decode(payload['public_key']))
            bin_signature = bytes.fromhex(b64decode(payload['signature']))
            bin_block_hash = bytes.fromhex(payload['block_hash'])
            return cls(payload['block_height'], payload['timestamp'], payload['sender'], payload['recipient'],
                       int_amount, bin_signature, bin_public_key, bin_block_hash, int_fee, int_reward,
                       payload['operation'], payload['openfield'])
        else:
            return cls(payload['block_height'], payload['timestamp'], payload['sender'], payload['recipient'],
                       int_amount, payload['signature'], payload['public_key'], payload['block_hash'],
                       int_fee, int_reward, payload['operation'], payload['openfield'])

    """
    Exporters
    """

    def to_dict(self, legacy=False):
        """
        The transaction object as a Python dict with keys
        'block_height', 'timestamp', 'sender', 'recipient', 'amount', 'signature', 'public_key',
        'block_hash', 'fee', 'reward', 'operation', 'openfield'
        'format'

        format will be either 'Legacy' or 'Bin'
        """
        amount = Transaction.int_to_f8(self.amount)
        fee = Transaction.int_to_f8(self.fee)
        reward = Transaction.int_to_f8(self.reward)
        if legacy:
            public_key = b64encode(self.public_key.hex())
            signature = b64encode(self.signature.hex())
            block_hash = self.block_hash.hex()
            sender = self.sender.hex()
            recipient = self.recipient.hex()
            return dict(zip(TRANSACTION_KEYS, (self.block_height, self.timestamp, sender, recipient, amount,
                                               signature, public_key, block_hash, fee, reward,
                                               self.operation, self.openfield, 'Legacy')))

        return dict(zip(TRANSACTION_KEYS, (self.block_height, self.timestamp, self.sender, self.recipient, amount,
                                           self.signature, self.public_key, self.block_hash, fee, reward,
                                           self.operation, self.openfield, 'Bin')))

    def to_json(self, legacy=False):
        """
        The transaction object as a json string
        """
        return json.dumps(self.to_dict(legacy))

    def to_tuple(self):
        """
        The transaction object as a legacy tuple in the following order:
        'block_height', 'timestamp', 'sender', 'recipient', 'amount', 'signature', 'public_key', 'block_hash',
        'fee', 'reward', 'operation', 'openfield'

        Legacy format means amounts will be string, 0.8f, and all bin content hex or hex+b64 encoded.
        """
        amount = Transaction.int_to_f8(self.amount)
        fee = Transaction.int_to_f8(self.fee)
        reward = Transaction.int_to_f8(self.reward)
        public_key = b64encode(self.public_key.hex())
        signature = b64encode(self.signature.hex())
        block_hash = self.block_hash.hex()
        sender = self.sender.hex()
        recipient = self.recipient.hex()
        return (self.block_height, self.timestamp, sender, recipient, amount, signature, public_key, block_hash,
                fee, reward, self.operation, self.openfield)

    def to_protobuf(self, buffer=None):
        """Exports to protobuf
        """
        raise AssertionError("TODO")
        # TODO

    """
    Properties
    """

    @property
    def is_mining(self):
        return self.reward > 0 and not self.amount


"""
Block
"""


class Block:
    """A generic Bismuth Block with its transactions"""

    # Inner storage is compact, binary form
    __slots__ = ('transactions', )

    def __init__(self, transactions):
        """Default constructor with list of binary, non verbose, transactions, mining transaction at the end."""
        self.transactions = transactions


