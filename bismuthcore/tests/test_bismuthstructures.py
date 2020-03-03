#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `bismuthcore` package."""

import pytest
import random
import sys
from decimal import Decimal, getcontext, ROUND_HALF_EVEN

sys.path.append('../')
from bismuthcore.transaction import Transaction

getcontext().rounding = ROUND_HALF_EVEN

# A Test transaction
TX = Transaction.from_legacy_params(block_height=1, timestamp=0.01,
                                    address='ABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFab',
                                    recipient='01234567890123456789012345678901234567890123456789012345',
                                    amount='0.01000000',
                                    signature='0ABCDEF0', public_key='00112233',
                                    block_hash='0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF01234567',
                                    fee='0.01000000', reward='0.00000000',
                                    operation='TEST', openfield='test_openfield'
                                    )


def test_create_transaction():
    """Can create a Transaction object"""
    tx = Transaction()


def test_convert_amount():
    """double convert gives same amount"""
    random.seed('Reproducible test')
    for i in range(10):
        amount = random.random()*100
        f8_amount =  str('{:.8f}'.format(Decimal(amount)))
        int_amount = Transaction.f8_to_int(f8_amount)
        assert f8_amount == Transaction.int_to_f8(int_amount)


def test_checksum(verbose=False):
    if verbose:
        print(TX.checksum)
    assert TX.checksum == b'{\xa4PB\xea\xfa\x98\x96\x84\x13cE\tJ\x9e\xf7=\xd4G$'


def test_to_tuple(verbose=False):
    """Legacy export format"""
    if verbose:
        print(TX.to_tuple())
    assert TX.to_tuple() == (1, 0.01, 'ABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFab',
                           '01234567890123456789012345678901234567890123456789012345',
                           '0.01000000',
                           '0ABCDEF0', '00112233',
                           '0123456789abcdef0123456789abcdef0123456789abcdef01234567',
                           '0.01000000', '0.00000000',
                           'TEST', 'test_openfield')


def test_to_json(verbose=False):
    """Json export format"""
    if verbose:
        print(TX.to_json())
    assert TX.to_json() == '{"block_height": 1, "timestamp": 0.01, ' \
                           '"address": "ABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFab", ' \
                           '"recipient": "01234567890123456789012345678901234567890123456789012345", ' \
                           '"amount": "0.01000000", ' \
                           '"signature": "0ABCDEF0", "public_key": "00112233", ' \
                           '"block_hash": "0123456789abcdef0123456789abcdef0123456789abcdef01234567", ' \
                           '"fee": "0.01000000", "reward": "0.00000000", ' \
                           '"operation": "TEST", "openfield": "test_openfield", "format": "Legacy"}'


def test_to_dict_bin(verbose=False):
    """Bin dict export format"""
    if verbose:
        print(TX.to_dict(legacy=False))
        assert TX.to_dict(legacy=False) == {'block_height': 1, 'timestamp': 0.01,
                                           'address': "ABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFab",
                                           'recipient': "01234567890123456789012345678901234567890123456789012345",
                                           'amount': '0.01000000',
                                           'signature': b'\xd0\x00B\x0cAt', 'public_key': b'\xd3Mu\xdbm\xf7',
                                           'block_hash': b'\x01#Eg\x89\xab\xcd\xef\x01#Eg\x89\xab\xcd\xef\x01#Eg\x89\xab\xcd\xef\x01#Eg',
                                           'fee': '0.01000000', 'reward': '0.00000000',
                                           'operation': 'TEST', 'openfield': 'test_openfield', 'format': 'Bin'}


if __name__ == "__main__":
    """
    test_to_tuple(verbose=True)
    test_to_json(verbose=True)
    test_to_dict_bin(verbose=True)
    """
    test_checksum(verbose=True)
