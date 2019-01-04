"""
Convert ledger.db from legacy to bin format.

Test temp util
"""

import sqlite3
import sys
sys.path.append('../bismuthcore')
from structures import Transaction

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


if __name__ == "__main__":
    with sqlite3.connect('../../../Bismuth-temp/static/ledger.db', timeout=1) as ledger:
        ledger.text_factory = str
        res = ledger.execute("select * from transactions where block_height > 800000 limit 100")
        for row in res:
            print(len(str(row)))  # About 2000
            tx = Transaction.from_legacy(row)
            print(tx.to_json(legacy=True))

