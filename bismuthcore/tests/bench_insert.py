"""
Tx insert benchmark
"""

import sqlite3
import sys
import json
from time import time
from os import remove

sys.path.append('../')
from bismuthcore.structures import Transaction
from bismuthcore.decorators import timeit

SQL_CREATE = ('''
              CREATE TABLE "misc" (
                  `block_height`	INTEGER,
                  `difficulty`	TEXT
              )''',
              '''CREATE TABLE "transactions" (
                  `block_height`	INTEGER,
                  `timestamp`	NUMERIC,
                  `address`	BLOB(28),
                  `recipient`	BLOB(28),
                  `amount`	INTEGER,
                  `signature`	BLOB,
                  `public_key`	BLOB,
                  `block_hash`	BLOB(28),
                  `fee`	INTEGER,
                  `reward`	INTEGER,
                  `operation`	TEXT,
                  `openfield`	TEXT
              )''',
              'CREATE INDEX `Timestamp Index` ON `transactions` (`timestamp`)',
              'CREATE INDEX `Signature Index` ON `transactions` (`signature`)',
              'CREATE INDEX `Reward Index` ON `transactions` (`reward`)',
              'CREATE INDEX `Recipient Index` ON `transactions` (`recipient`)',
              'CREATE INDEX `Openfield Index` ON `transactions` (`openfield`)',
              'CREATE INDEX `Fee Index` ON `transactions` (`fee`)',
              'CREATE INDEX `Block Height Index` ON `transactions` (`block_height`)',
              'CREATE INDEX `Block Hash Index` ON `transactions` (`block_hash`)',
              'CREATE INDEX `Amount Index` ON `transactions` (`amount`)',
              'CREATE INDEX `Address Index` ON `transactions` (`address`)',
              'CREATE INDEX `Operation Index` ON `transactions` (`operation`)',
)


SQL_CREATE_LEGACY = ('''
                     CREATE TABLE "misc" (
                         `block_height`	INTEGER,
                         `difficulty`	TEXT
                     )''',
                     '''CREATE TABLE "transactions" (
                         `block_height`	INTEGER,
                         `timestamp`	NUMERIC,
                         `address`	TEXT,
                         `recipient`	TEXT,
                         `amount`	NUMERIC,
                         `signature`	TEXT,
                         `public_key`	TEXT,
                         `block_hash`	TEXT,
                         `fee`	NUMERIC,
                         `reward`	NUMERIC,
                         `operation`	TEXT,
                         `openfield`	TEXT
                     )''',
                     'CREATE INDEX `Timestamp Index` ON `transactions` (`timestamp`)',
                     'CREATE INDEX `Signature Index` ON `transactions` (`signature`)',
                     'CREATE INDEX `Reward Index` ON `transactions` (`reward`)',
                     'CREATE INDEX `Recipient Index` ON `transactions` (`recipient`)',
                     'CREATE INDEX `Openfield Index` ON `transactions` (`openfield`)',
                     'CREATE INDEX `Fee Index` ON `transactions` (`fee`)',
                     'CREATE INDEX `Block Height Index` ON `transactions` (`block_height`)',
                     'CREATE INDEX `Block Hash Index` ON `transactions` (`block_hash`)',
                     'CREATE INDEX `Amount Index` ON `transactions` (`amount`)',
                     'CREATE INDEX `Address Index` ON `transactions` (`address`)',
                     'CREATE INDEX `Operation Index` ON `transactions` (`operation`)',
                     )


def create(db, sql: tuple):
    for line in sql:
        db.execute(line)
    db.commit()


@timeit
def bench_new(txs):
    # Using inram DB to avoid disk I/O artefacts
    test_new = sqlite3.connect('file:ledger_new?mode=memory', uri=True, timeout=1)
    create(test_new, SQL_CREATE)
    for tx in txs:
        # Creates instance from tuple data, copy to inner properties
        tx = Transaction.from_legacy(tx)
        # Then converts to bin and into bin tuple
        test_new.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", tx.to_bin_tuple())


@timeit
def bench_legacy(txs):
    test_new = sqlite3.connect('file:ledger_legacy?mode=memory', uri=True, timeout=1)
    create(test_new, SQL_CREATE_LEGACY)
    for tx in txs:
        # Directly insert tuple without any conversion to db
        test_new.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", tx)

@timeit
def bench_legacy_object(txs):
    test_new = sqlite3.connect('file:ledger_legacy?mode=memory', uri=True, timeout=1)
    create(test_new, SQL_CREATE_LEGACY)
    for tx in txs:
        # Creates instance from tuple data, copy to inner properties (converts to binary as well)
        tx = Transaction.from_legacy(tx)
        # Then export again
        test_new.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", tx.to_tuple())


if __name__ == "__main__":

    # read data
    txs=[]
    with open("../Utils/tx_tuple_dataset.json") as f:
        for raw in f:
            txs.append(json.loads(raw))
    print("Bench {} txs".format(len(txs)))
    bench_new(txs)

    bench_legacy(txs)

    bench_legacy_object(txs)

"""
Bench 100000 txs
bench_new  7.203981 s
bench_legacy  4.797854 s
bench_legacy_object  8.732996 s
"""
