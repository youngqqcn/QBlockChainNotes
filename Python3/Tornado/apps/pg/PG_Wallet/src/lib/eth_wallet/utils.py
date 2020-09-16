#!/usr/bin/env python3

from mnemonic import Mnemonic
from binascii import hexlify

import os


def get_bytes(string):
    if isinstance(string, bytes):
        byte = string
    elif isinstance(string, str):
        byte = bytes.fromhex(string)
    else:
        raise TypeError("agreement must be either 'bytes' or 'string'!")
    return byte


def generate_mnemonic(language="english", strength=128):
    return Mnemonic(language=language).generate(strength=strength)


def generate_entropy(strength=128):
    if strength not in [128, 160, 192, 224, 256]:
        raise ValueError(
            "Strength should be one of the following "
            "[128, 160, 192, 224, 256], but it is not (%d)."
            % strength
        )
    return hexlify(os.urandom(strength // 8)).decode()


def check_mnemonic(mnemonic, language=None):
    if language and language not in ["english", "french", "italian", "japanese",
                                     "chinese_simplified", "chinese_traditional", "korean", "spanish"]:
        raise ValueError("Invalid language, use only this options english, french, "
                         "italian, spanish, chinese_simplified, chinese_traditional, japanese & korean.")
    try:
        if language is None:
            for _language in ["english", "french", "italian",
                              "chinese_simplified", "chinese_traditional", "japanese", "korean", "spanish"]:
                valid = False
                if Mnemonic(language=_language).check(mnemonic=mnemonic) is True:
                    valid = True
                    break
            return valid
        else:
            return Mnemonic(language=language).check(mnemonic=mnemonic)
    except:
        return False


def get_mnemonic_language(mnemonic):
    if not check_mnemonic(mnemonic=mnemonic):
        raise ValueError("Invalid 12 word mnemonic.")

    language = None
    for _language in ["english", "french", "italian",
                      "chinese_simplified", "chinese_traditional", "japanese", "korean", "spanish"]:
        if Mnemonic(language=_language).check(mnemonic=mnemonic) is True:
            language = _language
            break
    return language
