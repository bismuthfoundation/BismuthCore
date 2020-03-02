"""
Tx insert benchmark
"""

import sqlite3
import sys
import json
from time import time
from os import remove
from decimal import Decimal

sys.path.append('../')
from bismuthcore.transaction import Transaction
from bismuthcore.decorators import timeit
from bismuthcore.compat import quantize_eight
from bismuthcore.helpers import native_tx_to_bin_sqlite, TxConverter

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
                  `iamount`	INTEGER,
                  `signature`	BLOB,
                  `public_key`	BLOB,
                  `block_hash`	BLOB(28),
                  `ifee`	INTEGER,
                  `ireward`	INTEGER,
                  `operation`	TEXT,
                  `openfield`	TEXT
              )''',
              'CREATE INDEX `Timestamp Index` ON `transactions` (`timestamp`)',
              'CREATE INDEX `Signature Index` ON `transactions` (`signature`)',
              'CREATE INDEX `Reward Index` ON `transactions` (`ireward`)',
              'CREATE INDEX `Recipient Index` ON `transactions` (`recipient`)',
              'CREATE INDEX `Openfield Index` ON `transactions` (`openfield`)',
              'CREATE INDEX `Fee Index` ON `transactions` (`ifee`)',
              'CREATE INDEX `Block Height Index` ON `transactions` (`block_height`)',
              'CREATE INDEX `Block Hash Index` ON `transactions` (`block_hash`)',
              'CREATE INDEX `Amount Index` ON `transactions` (`iamount`)',
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
def insert_new(txs):
    # Using inram DB to avoid disk I/O artefacts
    test_new = sqlite3.connect('file:ledger_new?mode=memory', uri=True, timeout=1)
    create(test_new, SQL_CREATE)
    for tx in txs:
        # Creates instance from tuple data, copy to inner properties
        tx = Transaction.from_legacy(tx)
        # Then converts to bin and into bin tuple
        test_new.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", tx.to_bin_tuple(sqlite_encode=True))
    return test_new


@timeit
def insert_new_function(txs):
    """ Uses a call to a function helper"""
    test_new = sqlite3.connect('file:ledger_new_function?mode=memory', uri=True, timeout=1)
    create(test_new, SQL_CREATE)
    for tx in txs:
        # converts into bin tuple - just conversion, no object created, no stored property.
        test_new.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", native_tx_to_bin_sqlite(tx))
    return test_new

@timeit
def insert_new_class(txs):
    """ Uses a call to a function helper"""
    test_new = sqlite3.connect('file:ledger_new_class?mode=memory', uri=True, timeout=1)
    create(test_new, SQL_CREATE)
    for tx in txs:
        # converts into bin tuple - just conversion, no object created, no stored property.
        test_new.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", TxConverter.native_tx_to_bin_sqlite(tx))
    return test_new

@timeit
def insert_legacy(txs):
    test_legacy = sqlite3.connect('file:ledger_legacy?mode=memory', uri=True, timeout=1)
    create(test_legacy, SQL_CREATE_LEGACY)
    for tx in txs:
        # Directly insert tuple without any conversion to db
        test_legacy.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", tx)
    return test_legacy


@timeit
def insert_legacy_object(txs):
    test_legacy = sqlite3.connect('file:ledger_legacy?mode=memory', uri=True, timeout=1)
    create(test_legacy, SQL_CREATE_LEGACY)
    for tx in txs:
        # Creates instance from tuple data, copy to inner properties (converts to binary as well)
        tx = Transaction.from_legacy(tx)
        # Then export again
        test_legacy.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", tx.to_tuple())
    return test_legacy


@timeit
def balance_new(db, address: str):
    q1 = db.execute(
        "SELECT sum(iamount + ireward) FROM transactions WHERE recipient = ? ",
        (address,),
    )
    r1 = q1.fetchone()
    credit = r1[0] if r1[0] else 0
    q2 = db.execute(
        "SELECT sum(iamount + ifee) FROM transactions WHERE address = ? ",
        (address,),
    )
    r2 = q2.fetchone()
    debit = r2[0] if r2[0] else 0
    return Transaction.int_to_f8(credit-debit)


@timeit
def balance_new2(db, address: str):
    q1 = db.execute(
        "SELECT (SELECT sum(iamount + ireward) FROM transactions WHERE recipient = ? ) - (SELECT sum(iamount + ifee) FROM transactions WHERE address = ?)",
        (address, address),
    )
    r1 = q1.fetchone()
    balance = r1[0] if r1[0] else 0

    return Transaction.int_to_f8(balance)


@timeit
def balance_legacy(db, address: str):
    # from essentials.py
    credit_ledger = Decimal(0)
    q1 = db.execute("SELECT amount, reward FROM transactions WHERE recipient = ?", (address,))
    entries = q1.fetchall()
    for entry in entries:
        credit_ledger += quantize_eight(entry[0]) + quantize_eight(entry[1])

    debit_ledger = Decimal(0)
    q2 = db.execute("SELECT amount, fee FROM transactions WHERE address = ?", (address,))
    entries = q2.fetchall()
    for entry in entries:
        debit_ledger += quantize_eight(entry[0]) + quantize_eight(entry[1])

    return quantize_eight(credit_ledger - debit_ledger)


if __name__ == "__main__":

    # read data
    txs=[]
    with open("../Utils/tx_tuple_dataset.json") as f:
        for raw in f:
            txs.append(json.loads(raw))
    print("Bench {} txs".format(len(txs)))
    new_db = insert_new(txs)
    insert_new_function(txs)
    insert_new_class(txs)
    bal_new = balance_new(new_db, "e13e79dc7e4b8265d7cdafe31819939fcce98abc2c7662f7fb53fa38")
    # balances can be negative here since we don't have the chain from start.
    print(bal_new)
    bal_new2 = balance_new2(new_db, "e13e79dc7e4b8265d7cdafe31819939fcce98abc2c7662f7fb53fa38")
    # balances can be negative here since we don't have the chain from start.
    print(bal_new2)
    # da8a39cc9d880cd55c324afc2f9596c64fac05b8d41b3c9b6c481b4e
    insert_legacy_object(txs)
    legacy_db = insert_legacy(txs)
    bal_legacy = balance_legacy(legacy_db, "e13e79dc7e4b8265d7cdafe31819939fcce98abc2c7662f7fb53fa38")
    print(bal_legacy)


"""
Bench 100000 txs
bench_new  7.203981 s
bench_legacy  4.797854 s
bench_legacy_object  8.732996 s
"""

"""
select distinct(address), count(*) as total from transactions where block_height > 700000 group by address order by total desc limit 50;
e13e79dc7e4b8265d7cdafe31819939fcce98abc2c7662f7fb53fa38|518996
952cfda35b32e2eac3e3431f566b80a0c47c6c512d3f283c1e57aee3|379497
de98671db1ce0e5c9ba89ab7ccdca6c427460295b8dd3642e9b2bb96|236017
da8a39cc9d880cd55c324afc2f9596c64fac05b8d41b3c9b6c481b4e|114178
b54317cb538c6b3a5ae8b84f8b53c83652037038ad8ad6bef4c8b43a|53728
3d2e8fa99657ab59242f95ca09e0698a670e65c3ded951643c239bc7|43782
de5383d490cd531d48d8aff03dde9d2d37cab96c9e57c76403542100|41322
8ee55ddf7709c4f0d1d5b7994400264a951aeb1399519fe9887e3b88|11329
921017bd8384a9e0650824161f3e9b975faff53190f3d7b5fe1eadb7|9074
3e08b5538a4509d9daa99e01ca5912cda3e98a7f79ca01248c2bde16|8604
84d5e70542fc5a14e89d7ced56ba1e09423553868887c9e24c58199b|5978
9ba0f8ca03439a8b4222b256a5f56f4f563f6d83755f525992fa5daf|4854
25125e9bb305fafd51ceb2858d355f77da99550b933ec0923cd156ff|3641
14c1b5851634f0fa8145ceea1a52cabe2443dc10350e3febf651bd3a|2860
bc78b4271976a8ece3206082f6545975273f26b7ac8fd6592604dd2b|2450
05ff36bb190eb73a467dde487f40005edbc3327afea110b378f5cb63|2296
3b7fc45dfb30a95b0277ed0e5fe0244460827f59f08b8f0b9e7da66e|1900
edf2d63cdf0b6275ead22c9e6d66aa8ea31dc0ccb367fad2e7c08a25|1822
f6c0363ca1c5aa28cc584252e65a63998493ff0a5ec1bb16beda9bac|1424
340c195f768be515488a6efedb958e135150b2ef3e53573a7017ac7d|1373
07848518807ca9cfcba2d0ee52dcd27a0a1d69d3eb956253c8d12eea|983
9a01bcc07c8412e2ee59e7fe728431b3679d4e9c97633919b5f65768|940
d0db8ba979cf3ac823027a9302272e2967f1f8e91e40bdd03f6d1dbd|936
731337bb0f76463d578626a48367dfea4c6efcfa317604814f875d10|660
827a8ccd27ba0f812eb7d5d8ab74a8c424f8fb09a934b5754e509c34|592
761b9d7d1af4fd5899f59ec20b5cc5fc9880923fae68580743ae5721|553
d9dcbda8025fd296d842289bba7a1bd2fab5c63decf73d0458bbea70|491
84ec59f7728ed54ab4024b0c0bdedd6fecf787b0386b5c38701139e8|488
1dd46c0639afa99e76311be88a0422bd9d624798572c6d2c570ebc6f|478
b4574154e24ced53148a72b7d81674abfb4e1975a7bbd2c33492cf67|468
0fc197a9a44a68bd6e9553ae9b97e717e9a07b4dd9e233886f4198ad|464
3ba8b25e659db6d109b99d9caceed50640a888c2198e75ef6f7a3894|416
05934f415e199f4d3041d87320027cda64bf58d7aadd0c39d915d486|414
c0d4985366d93128bbafa2e9f540fe8fef16840869f5846b0e08ca68|393
e853304588cac5a88fb37c930e9aaf84cf57c1aafa3fffec5bed6ccc|386
3633587a5655611c378ed5b96418ed63ff5baac69e6d09d638f624f0|339
43c4e85fe3f210149796f33df49a0223f3aa44bad79e056ce1e31775|334
688997bc367abb988068217daaf629e06cca736f86c2ac5dbc0fadd6|332
b2565d21527f1924521dcc78eaf38aeaf20c25264fecf6c61793564b|319
d59bab600494bdfd13fe6bda4ccf7775481f05b21abcaa36efbfbd98|313
15158a334b969fa7486a2a1468d04a583f3b51e6e0a7d330723701c3|312
325643775125e6550d16534519d4b49b9d5e32dcd5ea18ed91af1309|307
d7991f990d2950979dd442e5dac7376bfac514a9ca82b726b9d283f1|299
5b2d8418358ef8707e2db65be123a00579217f1538c300767682ba8c|289
2d865347cf1358e7f81dfede2284f6f19789eab2bb082d34e0682087|286
9892caa4b6b334db9c41334424991ffbc1edf20da1308894038ffb2f|285
989f56e1efd230e9cb753b361ed5564cc42e11039615548f2da3c5d1|274
376518d6f45761cd9dc832a68f4cb2bcf6a225c74a84a4ddb80d8722|268
af2ca51e90bb3f33038530f3bdcec8ab32ca3556b4ace01a5bdc9e97|262
2bb182e452b1c1574f3551805ce077a1c0afdd8cefb744929fe03304|255

"""
