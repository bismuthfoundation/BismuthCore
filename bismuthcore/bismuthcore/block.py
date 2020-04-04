
"""
Bismuth core Block Class
"""

from bismuthcore.transaction import Transaction

__version__ = "0.0.2"


class Block:
    """A generic Bismuth Block with its transactions"""

    # Inner storage is compact, binary form
    __slots__ = ('transactions', )

    def __init__(self, transactions: list):
        """Default constructor with list of binary, non verbose,
        Transactions instances, mining transaction at the end."""
        self.transactions = transactions

    def to_listofdicts(self, legacy: bool=False, decode_pubkey: bool=False) -> list:
        """
        The block as a list of Transactions, converted to the required dict format.
        :param legacy:
        :param decode_pubkey:
        :return:
        """
        # Could be better as tuple, but may constraint higher level usage (may need to add something to the list) - to be checked later on
        return [transaction.to_dict(legacy=legacy, decode_pubkey=decode_pubkey) for transaction in self.transactions]

    def to_listoftuples(self) -> list:
        """
        The block as a list of Transactions, converted to legacy tuples.
        :return:
        """
        return [transaction.to_tuple() for transaction in self.transactions]

    def to_blocks_dict(self) -> dict:
        """a Block instance can also be a list of transactions from several different blocks.
        This formatter - ported from ApiHandler - does convert to a dict, heights as key"""
        # This is a specific format which use and specifics should be documented.
        tx_list = []
        block = {}
        blocks = {}
        # Egg: mostly kept the previous logic
        old = None
        for transaction_object in self.transactions:
            transaction = transaction_object.to_dict(legacy=True, decode_pubkey=True)
            height = transaction['block_height']
            block_hash = transaction['block_hash']
            del transaction['block_height']
            del transaction['block_hash']
            if old != height:  # if same block
                # using new objects rather than emptying the old ones: same reference, would break if several blocks.
                tx_list = []
                block = {}
            tx_list.append(transaction)
            block['block_height'] = height
            block['block_hash'] = block_hash
            block['transactions'] = tx_list
            blocks[height] = block
            old = height  # update
        return blocks

