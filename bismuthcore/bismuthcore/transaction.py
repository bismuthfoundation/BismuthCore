"""
Bismuth core transaction structure
"""

import json
from decimal import Decimal, getcontext, ROUND_HALF_EVEN
from base64 import b64decode, b64encode
from sqlite3 import Binary
from Cryptodome.Hash import SHA

__version__ = '0.0.6'

# Multiplier to convert floats to int
DECIMAL_1E8 = Decimal(100000000)

# Keys of the Json object
TRANSACTION_KEYS = ('block_height', 'timestamp', 'address', 'recipient', 'amount', 'signature', 'public_key',
                    'block_hash', 'fee', 'reward', 'operation', 'openfield',
                    'format')

getcontext().rounding = ROUND_HALF_EVEN


"""
Transaction
"""


class Transaction:
    """A generic Bismuth Transaction"""

    # Inner storage is compact, binary form

    __slots__ = ('block_height', 'timestamp', 'address', 'recipient', 'amount', 'signature', 'public_key',
                 'block_hash', 'fee', 'reward', 'operation', 'openfield')

    def __init__(self, block_height: int=0, timestamp: float=0, address: str='', recipient: str='',
                 amount: int=0, signature: bytes=b'', public_key: bytes=b'', block_hash: bytes=b'', fee: int=0,
                 reward: int=0, operation: str='', openfield: str=''):
        """Default constructor with binary, non verbose, parameters"""
        self.block_height = block_height
        self.timestamp = timestamp
        self.address = address
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
        # public_key is double b64 encoded in legacy format.
        # Could win even more storing the public_key decoded once more, but may generate more overhead at decode
        # Postponed, since pubkeys do not need to be stored for every address every time
        bin_public_key = b64decode(public_key)
        # signature is b64 encoded in legacy format.
        bin_signature = b64decode(signature)
        # whereas block hash only is hex encoded.
        bin_block_hash = bytes.fromhex(block_hash)
        return cls(block_height, timestamp, sender, recipient, int_amount, bin_signature, bin_public_key,
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
        bin_public_key = b64decode(public_key)
        bin_signature = b64decode(signature)
        bin_block_hash = bytes.fromhex(block_hash)
        return cls(block_height, timestamp, sender, recipient, int_amount, bin_signature, bin_public_key,
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

        json can either contain public_key as double encoded b64 or not.
        In either case, amount will be as string, 0.8f
        block_hash, sender and recipient are to be hex encoded, for readability reasons, and because json does not support byte streams.

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

        # addresses are hex encoded, convert to bin inplace
        payload['address'] = bytes.fromhex(payload['address'])
        payload['recipient'] = bytes.fromhex(payload['recipient'])

        bin_signature = b64decode(payload['signature'])
        bin_block_hash = bytes.fromhex(payload['block_hash'])

        if payload['public_key'].beginsWith('-----BEGIN PUBLIC KEY-----'):
            return cls(payload['block_height'], payload['timestamp'], payload['address'], payload['recipient'],
                       int_amount, bin_signature, payload['public_key'], bin_block_hash,
                       int_fee, int_reward, payload['operation'], payload['openfield'])
        else:
            # We got legacy encoded strings, convert to bin
            bin_public_key = b64decode(payload['public_key'])
            return cls(payload['block_height'], payload['timestamp'], payload['address'], payload['recipient'],
                       int_amount, bin_signature, bin_public_key, bin_block_hash, int_fee, int_reward,
                       payload['operation'], payload['openfield'])

    """
    Exporters
    """

    def to_dict(self, legacy: bool=False, decode_pubkey: bool=False):
        """
        The transaction object as a Python dict with keys
        'block_height', 'timestamp', 'address', 'recipient', 'amount', 'signature', 'public_key',
        'block_hash', 'fee', 'reward', 'operation', 'openfield'
        'format'

        format will be either 'Legacy' or 'Bin'
        decode_pubkey is used to keep compatibility with essentials.format_raw_tx, that was trying to decode pubkey
        Only checkled if legacy.
        """
        amount = Transaction.int_to_f8(self.amount)
        fee = Transaction.int_to_f8(self.fee)
        reward = Transaction.int_to_f8(self.reward)
        if legacy:
            public_key = b64encode(self.public_key).decode('utf-8')
            if decode_pubkey:
                try:
                    public_key = b64decode(public_key).decode('utf-8')
                except:
                    pass  # support new pubkey schemes
            signature = b64encode(self.signature).decode('utf-8')
            block_hash = self.block_hash.hex()
            return dict(zip(TRANSACTION_KEYS, (self.block_height, self.timestamp, self.address, self.recipient, amount,
                                               signature, public_key, block_hash, fee, reward,
                                               self.operation, self.openfield, 'Legacy')))

        return dict(zip(TRANSACTION_KEYS, (self.block_height, self.timestamp, self.address, self.recipient, amount,
                                           self.signature, self.public_key, self.block_hash, fee, reward,
                                           self.operation, self.openfield, 'Bin')))

    def to_json(self):
        """
        The transaction object as a json string
        """
        return json.dumps(self.to_dict(True))

    def to_tuple(self):
        """
        The transaction object as a legacy tuple in the following order:
        'block_height', 'timestamp', 'address', 'recipient', 'amount', 'signature', 'public_key', 'block_hash',
        'fee', 'reward', 'operation', 'openfield'

        Legacy format means amounts will be string, 0.8f, and all bin content hex or b64 encoded.
        """
        amount = Transaction.int_to_f8(self.amount)
        fee = Transaction.int_to_f8(self.fee)
        reward = Transaction.int_to_f8(self.reward)
        public_key = b64encode(self.public_key).decode('utf-8')
        signature = b64encode(self.signature).decode('utf-8')
        block_hash = self.block_hash.hex()
        return (self.block_height, self.timestamp, self.address, self.recipient, amount, signature, public_key, block_hash,
                fee, reward, self.operation, self.openfield)

    def to_bin_tuple(self, sqlite_encode=False):
        """
        The transaction object as a bin tuple in the following order:
        'block_height', 'timestamp', 'address', 'recipient', 'amount', 'signature', 'public_key', 'block_hash',
        'fee', 'reward', 'operation', 'openfield'

        Bin format means amounts will be integers, and all content unencoded.
        """
        if sqlite_encode:
            # sqlite needs .binary() to encode blobs
            return (self.block_height, self.timestamp, self.address, self.recipient, self.amount, Binary(self.signature),
                    Binary(self.public_key), Binary(self.block_hash), self.fee, self.reward, self.operation, self.openfield)

        return (self.block_height, self.timestamp, self.address, self.recipient, self.amount, self.signature,
                self.public_key, self.block_hash, self.fee, self.reward, self.operation, self.openfield)

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
        """Is this a coinbase transaction ?"""
        return self.reward > 0 and not self.amount

    @property
    def checksum(self):
        """A hash of all the inner properties, used for test purposes atm"""
        check = SHA.new(bytes(self.block_height))
        check.update(str(self.timestamp).encode('utf-8'))
        check.update(self.address.encode('utf-8'))
        check.update(self.recipient.encode('utf-8'))
        check.update(bytes(self.amount))
        check.update(self.signature)
        check.update(self.public_key)
        check.update(self.block_hash)
        check.update(bytes(self.fee))
        check.update(bytes(self.reward))
        check.update(self.operation.encode('utf-8'))
        check.update(self.openfield.encode('utf-8'))
        return check.digest()

