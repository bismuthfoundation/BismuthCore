"""
Export 100k tx to json format for benchmark

Test temp util
"""

import json
import sqlite3
import sys
from os import remove

sys.path.append('../')
from bismuthcore.structures import Transaction


if __name__ == "__main__":

    try:
        remove('tx_dataset.json')
    except:
        pass
    try:
        remove('tx_tuple_dataset.json')
    except:
        pass

    with sqlite3.connect('../../../Bismuth-temp/static/ledger.db', timeout=1) as ledger:
        # TODO: use a default path and give custom db path to command line for more flexible use depending on context
        ledger.text_factory = str
        res = ledger.execute("select * from transactions where block_height > 700000 limit 100000")
        with open("tx_dataset.json", "w") as fp:
            for row in res:
                tx = Transaction.from_legacy(row)
                fp.write(tx.to_json() + "\n")
        res = ledger.execute("select * from transactions where block_height > 700000 limit 100000")
        with open("tx_tuple_dataset.json", "w") as fp:
            for row in res:
                tx = Transaction.from_legacy(row)
                fp.write(json.dumps(tx.to_tuple()) + "\n")

