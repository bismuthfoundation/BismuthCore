"""
Old methods needed for compatibility and benchmark reasons
"""

from decimal import Decimal

DECIMAL_ZERO_2DP = Decimal('0.00')
DECIMAL_ZERO_8DP = Decimal('0.00000000')
DECIMAL_ZERO_10DP = Decimal('0.0000000000')


def quantize_two(value) -> Decimal:
    if not value:
        return DECIMAL_ZERO_2DP
    value = Decimal(value)
    value = value.quantize(DECIMAL_ZERO_2DP)
    return value


def quantize_eight(value) -> Decimal:
    if not value:
        # Will match 0 as well as False and None
        return DECIMAL_ZERO_8DP
    value = Decimal(value)
    value = value.quantize(DECIMAL_ZERO_8DP)
    return value


def quantize_ten(value) -> Decimal:
    if not value:
        return DECIMAL_ZERO_10DP
    value = Decimal(value)
    value = value.quantize(DECIMAL_ZERO_10DP)
    return value


def bin_convert(string: str):
    return ''.join(format(ord(x), '8b').replace(' ', '0') for x in string)

