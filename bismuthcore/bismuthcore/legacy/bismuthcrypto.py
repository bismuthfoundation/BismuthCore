"""
Crypto related functions for Bismuth.

Keys, wallet loading, signature

Legacy functions kept for compatibility.
See new BismuthWallet Class
"""

import base64
import getpass
import hashlib
import json
import os
import re

from Cryptodome.Hash import SHA
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5
from os import path
from bismuthcore.simplecrypt import decrypt

__version__ = "0.0.21"


def sign_rsa(
    timestamp, address, recipient, amount, operation, openfield, key, public_key_hashed
):
    if not key:
        raise BaseException("The wallet is locked, you need to provide a decrypted key")

    transaction = (
        str(timestamp),
        str(address),
        str(recipient),
        "%.8f" % float(amount),
        str(operation),
        str(openfield),
    )  # this is signed, float kept for compatibility

    h = SHA.new(str(transaction).encode())
    signer = PKCS1_v1_5.new(key)
    signature = signer.sign(h)
    signature_enc = base64.b64encode(signature)

    verifier = PKCS1_v1_5.new(key)
    if verifier.verify(h, signature):
        return_value = (
            str(timestamp),
            str(address),
            str(recipient),
            "%.8f" % float(amount),
            str(signature_enc.decode("utf-8")),
            str(public_key_hashed.decode("utf-8")),
            str(operation),
            str(openfield),
        )  # float kept for compatibility
    else:
        return_value = False

    return return_value


def format_transaction(
    timestamp: float,
    address: str,
    recipient: str,
    amount: float,
    operation: str,
    openfield: str,
):
    """
    Returns the formatted tuple to use as transaction part and to be signed
    This exact formatting is MANDATORY - We sign a char buffer where every char counts.
    """
    str_timestamp = "%.2f" % timestamp
    str_amount = "%.8f" % amount
    transaction = (str_timestamp, address, recipient, str_amount, operation, openfield)
    return transaction


def stringify_transaction(
    timestamp: float,
    address: str,
    recipient: str,
    amount: float,
    operation: str,
    openfield: str,
):
    """Formats the transaction items into the string buffer to be signed"""
    transaction = format_transaction(
        timestamp, address, recipient, amount, operation, openfield
    )
    return str(transaction).encode("utf-8")


def sign_with_key(
    timestamp: float,
    address: str,
    recipient: str,
    amount: float,
    operation: str,
    openfield: str,
    key,
):
    # Sign with key - This is a helper function
    # Returns the encoded sig as a string
    as_string = stringify_transaction(
        timestamp, address, recipient, amount, operation, openfield
    )
    # print("As String1", as_string)
    h = SHA.new(as_string)
    signer = PKCS1_v1_5.new(key)
    signature = signer.sign(h)
    # print("signature1", signature)
    signature_enc = base64.b64encode(signature)
    verifier = PKCS1_v1_5.new(key)
    if verifier.verify(h, signature):
        print("OK")
        return signature_enc.decode("utf-8")
    else:
        return False


def keys_check(app_log, keyfile):
    # key maintenance
    if os.path.isfile("privkey.der") is True:
        app_log.warning("privkey.der found")
    elif os.path.isfile("privkey_encrypted.der") is True:
        app_log.warning("privkey_encrypted.der found")
        os.rename("privkey_encrypted.der", "privkey.der")

    elif os.path.isfile(keyfile) is True:
        app_log.warning("{} found".format(keyfile))
    else:
        # generate key pair and an address

        key = RSA.generate(4096)
        # public_key = key.publickey()

        private_key_readable = key.exportKey().decode("utf-8")
        public_key_readable = key.publickey().exportKey().decode("utf-8")
        address = hashlib.sha224(
            public_key_readable.encode("utf-8")
        ).hexdigest()  # hashed public key
        # generate key pair and an address

        app_log.info("Your address: {}".format(address))
        app_log.info("Your public key: {}".format(public_key_readable))

        # export to single file
        keys_save(private_key_readable, public_key_readable, address, keyfile)
        # export to single file


def keys_new(keyfile):
    if path.isfile(keyfile):
        return False
    key = RSA.generate(4096)
    # public_key = key.publickey()
    private_key_readable = key.exportKey().decode("utf-8")
    public_key_readable = key.publickey().exportKey().decode("utf-8")
    address = hashlib.sha224(
        public_key_readable.encode("utf-8")
    ).hexdigest()  # hashed public key
    # export to single file
    keys_save(private_key_readable, public_key_readable, address, keyfile)
    return True


def keys_save(private_key_readable, public_key_readable, address, file):
    wallet_dict = {}
    wallet_dict["Private Key"] = private_key_readable
    wallet_dict["Public Key"] = public_key_readable
    wallet_dict["Address"] = address

    if not isinstance(file, str):
        file = file.name

    with open(file, "w") as keyfile:
        json.dump(wallet_dict, keyfile)


def keys_load(privkey="privkey.der", pubkey="pubkey.der"):
    keyfile = "wallet.der"
    if os.path.exists("wallet.der"):
        print("Using modern wallet method")
        return keys_load_new("wallet.der")

    else:
        # print ("loaded",privkey, pubkey)
        # import keys
        try:  # unencrypted
            with open(privkey) as keyfile:
                key = RSA.importKey(keyfile.read())
            private_key_readable = key.exportKey().decode("utf-8")
            # public_key = key.publickey()
            encrypted = False
            unlocked = True

        except Exception:  # encrypted
            encrypted = True
            unlocked = False
            key = None
            try:
                with open(privkey) as keyfile:
                    private_key_readable = keyfile.read()
            except Exception:
                raise

        # public_key_readable = str(key.publickey().exportKey())
            with open(pubkey.encode("utf-8")) as keyfile:
                public_key_readable = keyfile.read()

        if (len(public_key_readable)) != 271 and (len(public_key_readable)) != 799:
            raise ValueError(
                "Invalid public key length: {}".format(len(public_key_readable))
            )

        public_key_hashed = base64.b64encode(public_key_readable.encode("utf-8"))
        address = hashlib.sha224(public_key_readable.encode("utf-8")).hexdigest()

        print("Upgrading wallet")
        keys_save(private_key_readable, public_key_readable, address, keyfile)

        return (
            key,
            public_key_readable,
            private_key_readable,
            encrypted,
            unlocked,
            public_key_hashed,
            address,
            keyfile,
        )


def keys_unlock(private_key_encrypted):
    password = getpass.getpass()
    encrypted_privkey = private_key_encrypted
    decrypted_privkey = decrypt(password, base64.b64decode(encrypted_privkey))
    key = RSA.importKey(decrypted_privkey)  # be able to sign
    private_key_readable = key.exportKey().decode("utf-8")
    return key, private_key_readable


def keys_load_new(keyfile="wallet.der"):
    # import keys
    with open(keyfile, "r") as keyfile:
        wallet_dict = json.load(keyfile)

    private_key_readable = wallet_dict["Private Key"]
    public_key_readable = wallet_dict["Public Key"]
    address = wallet_dict["Address"]

    try:  # unencrypted
        key = RSA.importKey(private_key_readable)
        encrypted = False
        unlocked = True

    except Exception:  # encrypted
        encrypted = True
        unlocked = False
        key = None

    # public_key_readable = str(key.publickey().exportKey())
    if (len(public_key_readable)) != 271 and (len(public_key_readable)) != 799:
        raise ValueError(
            "Invalid public key length: {}".format(len(public_key_readable))
        )

    public_key_hashed = base64.b64encode(public_key_readable.encode("utf-8"))

    return (
        key,
        public_key_readable,
        private_key_readable,
        encrypted,
        unlocked,
        public_key_hashed,
        address,
        keyfile,
    )


# Dup code, not pretty, but would need address module to avoid dup
def address_validate(address):
    return re.match("[abcdef0123456789]{56}", address)


# Dup code, not pretty, but would need address module to avoid dup
def validate_pem(public_key):
    # verify pem as cryptodome does
    pem_data = base64.b64decode(public_key).decode("utf-8")
    regex = re.compile("\s*-----BEGIN (.*)-----\s+")
    match = regex.match(pem_data)
    if not match:
        raise ValueError("Not a valid PEM pre boundary")
    marker = match.group(1)
    regex = re.compile("-----END (.*)-----\s*$")
    match = regex.search(pem_data)
    if not match or match.group(1) != marker:
        raise ValueError("Not a valid PEM post boundary")
        # verify pem as cryptodome does
