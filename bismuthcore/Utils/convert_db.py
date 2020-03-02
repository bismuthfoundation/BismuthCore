"""
Convert ledger.db from legacy to bin format.

Test temp util
"""

import sqlite3
import sys
from os import remove

sys.path.append('../')
from bismuthcore.transaction import Transaction

SQL_CREATE = ('''
              CREATE TABLE "misc" (
                  `block_height`	INTEGER,
                  `difficulty`	TEXT
              )''',
              '''CREATE TABLE "transactions" (
                  `block_height`	INTEGER,
                  `timestamp`	NUMERIC,
                  `address`	TEXT,
                  `recipient`	TEXT,
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


if __name__ == "__main__":

    try:
        remove('ledger_new.db')
    except:
        pass
    try:
        remove('ledger_legacy.db')
    except:
        pass
    test_new = sqlite3.connect('ledger_new.db', timeout=1)
    create(test_new, SQL_CREATE)
    test_legacy = sqlite3.connect('ledger_legacy.db', timeout=1)
    create(test_legacy, SQL_CREATE_LEGACY)

    with sqlite3.connect('../../../Bismuth-temp/static/ledger.db', timeout=1) as ledger:
        ledger.text_factory = str
        res = ledger.execute("select * from transactions where block_height > 700000 limit 100000")
        for row in res:
            tx = Transaction.from_legacy(row)
            test_legacy.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", row)
            tx.public_key = b''
            test_new.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", tx.to_bin_tuple())
    test_new.commit()
    test_new.close()
    test_legacy.commit()
    test_legacy.close()


"""
No indexes
- legacy            218091520
- new (no pubkey)   102821888
- new (dup pubkeys) 153661440

Indexes
- legacy            369516544
- new (no pubkey)   243277824
- new (dup pubkeys) 294117376
"""

