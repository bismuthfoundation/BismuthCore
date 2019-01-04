"""
Convert ledger.db from legacy to bin format.

Test temp util
"""

SQL_CREATE=('''
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

signature
rBjfn9EI3xoJ0zJ34x+l8dyvTP1StvAp1vhN/dXG38VarTnoCymfoTMbtwprkfTikE374uZcU8x++C6sIY2hp45mnM1Ms2F8vPfYRwetpOZrAfVAI/VYjeYEd5UOToby+aITH8AKzq404ShTX6D8Jgw6t+wBG1GLjZCYZwDV1vwNqXY1Dth5jAxmcbpzdopglgdQ51JbOeIs8aOXPJ2saZG7dgIthTacknrgFNVwPQiErfm+wejyPVQcfN3YSzwVRZ4NaQb6vJSqz02wrF4DrO2bQxQgMYKGpi9PfulVv30/6wVG+IfWA17PuZODxvZw0TJcrbPGTVXLY6Nzr9YFJzvMupPiMdMgQOntmpWwSOOBlH+C0R5+qbSiVQSC04YHXPK4t6o2OtulRFj/ZQnTWPm+2sWBHryKUTFDA6uaxNWQtpeR7ppBt96JuZm0H7L75bgDjhnHEU1N3+OF9W9pJRRBIn6MwYEgn4Pi0mAiwm95MGg6sBr8YPRi01IB1rhFW7iHgMU9g8Nb1Y4n0NHs+d28jaItOTvkXlTOz6sXpkXItlcJRISL7PjgfCeqW5tAaTNOP+ee/8L/lIXULsKMsBuGTLWXI2A+yXXlTmJ4/vqEJ5tOCMFPlP3QVQDrSiPdNKvrhyJgGp07qEwGWw0VpRyjnZMCLOwjy+rmY86ZGM4=


pubkey
LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQ0lqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FnOEFNSUlDQ2dLQ0FnRUFzbzN1ZFpPU3JBYUczZ1pxU2J3TQpRMTRNb3dkTHhFRU9weG9hdFB6V0RBYzhUcmk1MDQraGdOb3NGVjB3QUIwMFBxcXJlZ1Q2YVVaWXl1aGZjSDYrCjRwVVpKUTlmQUlvZS9VZXRGdHN1TXNwM0FxUDFaL3lTYmZnMmkzSzJnTWF2Tjhua2RzU0ZSaGNqcUUwbGtqVUIKRVVQYlc5VVUyZ1FwWmVaVTZDblVvLzFpVHJ3N1NjNGZFUVpCU21BK2Z5Q3Y2ZDJub08xK0FFZTlCdXBCYXhIdwpkWXV1b3ZZUldaUURJTHowb0dwTVpXV1BkTEN4QU1aTU44Qk9QUExTWlpyNjh1NXRDbmwvNGNmU0g2c0VPZ3hnCk0rWjdzbkNYdDdvRlFpUERzc3YyV1E3K3AzSmJMNmpKakR5Y01wd3A0cit3YVlNV0hhYnVSVTQ3aVduejdpc0kKN1lBNnphSkpub292aENUUENzLzJjRERmdGIwNXVoUlFLZkNmTEVremZraXNVQTRWaXZEU083S2F4a0ticGNIMApUTGE3aUFCTVBHQXFhbzY5eE92Nmlsd0tHQ1ArSG90ZTNXZThmSTNudks5a2lHK0NnN2F4S3VndUV1d2tjMTUvClRLaUpRQkpQRkdtTXpjdVVoSFJJYktlWDQ1RHZqMkpjem44L3lvSkxMZUYxVjdFMXlLNys3N1lqUzl3K3NJYWYKZSt1d2RDVzNmWGR2RGxxclNaejZZcW5QdzZnMEZuZndiNHlZdlNDTGxxZzJGTEdFRnR1anlXblRSMVBWZU50Ywo0RGVnYW93RSs4eGE2MzJ1K2szOTVNYXVOVFJtSHpPblVVVllWVURNNGwzYnNEWTBZYTFTVnV0NHhvQXIwTG5uCk5sR0VKK2hidTdIU3REVGpBQzVtYjg4Q0F3RUFBUT09Ci0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQ==
