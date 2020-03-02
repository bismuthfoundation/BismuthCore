
"""
Bismuth core Block Class
"""


class Block:
    """A generic Bismuth Block with its transactions"""

    # Inner storage is compact, binary form
    __slots__ = ('transactions', )

    def __init__(self, transactions):
        """Default constructor with list of binary, non verbose, transactions, mining transaction at the end."""
        self.transactions = transactions


