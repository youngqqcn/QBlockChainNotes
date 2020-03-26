
#!coding:utf8

#author:yqq
#date:2019/9/25 0025 13:52
#description:


import json
import hashlib
import coincurve
import base64
from collections import OrderedDict
from binascii import hexlify , unhexlify
from coincurve.keys import ffi

def ecsign(rawhash, key):
    if coincurve and hasattr(coincurve, 'PrivateKey'):
        pk = coincurve.PrivateKey(key)
        signature = pk.sign_recoverable(rawhash, hasher=None)
        # v = safe_ord(signature[64]) + 27
        r = signature[0:32]
        s = signature[32:64]

        return r, s
    pass

def ecsign_test(rawhash, key):
    if coincurve and hasattr(coincurve, 'PrivateKey'):
        pk = coincurve.PrivateKey(key)
        # signature = pk.sign_recoverable(rawhash, hasher=None)
        sig_der = pk.sign(rawhash, hasher=None)
        return sig_der
        # v = safe_ord(signature[64]) + 27
        # r = signature[0:32]
        # s = signature[32:64]





def _is_canonical( sig):
    print("sig: " + str(sig))
    t1 = (sig[1] & 0x80) == 0
    t2 = not (sig[1] == 0 and ((sig[2] & 0x80) == 0))
    t3 = (sig[33] & 0x80) == 0
    t4 = not (sig[33] == 0 and ((sig[34] & 0x80) == 0))
    return t1 and t2 and t3 and t4

def _is_canoial_ex(sig_rs):
    t1 = (sig_rs[0] & 0x80) == 0
    t2 = (sig_rs[32] & 0x80) == 0
    return t1 and t2





def main1():

    test_data = 'b099531a13633f8cfb89b65b7794b1f8ecca8d03ab6bfd846d849d4609cd0ad0'
    priv_key =  '6fad07bf7166af32c864ec730df8a83ea87eeb8673f758e801f036e01000723f'
    if True:
        shaData = hashlib.sha256(unhexlify(test_data)).digest()
        print(hexlify(shaData))


        print(unhexlify(test_data))
        indata = shaData#unhexlify(test_data)
        print(len(indata))

        r, s = ecsign(indata, unhexlify( priv_key))
        print("r:{}".format(hexlify(r)))
        print("s:{}".format(hexlify(s)))

    pass


def main2():

    test_data = 'b099531a13633f8cfb89b65b7794b1f8ecca8d03ab6bfd846d849d4609cd0ad0'
    priv_key =  '6fad07bf7166af32c864ec730df8a83ea87eeb8673f758e801f036e01000723f'
    if True:
        # shaData = hashlib.sha256(unhexlify(test_data)).digest()
        # print(hexlify(shaData))

        # print(unhexlify(test_data))
        indata = unhexlify(test_data)
        print(len(indata))
        print(type(indata))


        r, s = ecsign(indata, unhexlify( priv_key))
        print("r:{}".format(hexlify(r)))
        print("s:{}".format(hexlify(s)))

    pass







def my_eos_sign(strrawdata):
    # test_data = 'b099531a13633f8cfb89b65b7794b1f8ecca8d03ab6bfd846d849d4609cd0ad0'
    priv_key = '6fad07bf7166af32c864ec730df8a83ea87eeb8673f758e801f036e01000723f'
    test_data = strrawdata
    # if True:
    cnt = 0
    while True:
        # shaData = hashlib.sha256(unhexlify(test_data)).digest()
        # print(hexlify(shaData))

        # print(unhexlify(test_data))
        indata = unhexlify(test_data)
        print(len(indata))
        print(type(indata))

        nonce_data = hashlib.sha256(indata + bytearray(cnt)).digest()
        print('nonce_data:{}'.format(hexlify(nonce_data)))

        sig_der = ecsign_custome_nonce(indata, unhexlify(priv_key), nonce_data)
        print(len(sig_der))
        print(hexlify(sig_der))
        if _is_canonical(sig_der):
            print('----------find-------------')
            return sig_der
        cnt += 1




from coincurve import  *
from coincurve.keys import lib
from coincurve.ecdsa import serialize_recoverable
from coincurve.utils import (
    bytes_to_hex,
    bytes_to_int,
    der_to_pem,
    ensure_unicode,
    get_valid_secret,
    hex_to_bytes,
    int_to_bytes_padded,
    pad_scalar,
    pem_to_der,
    sha256,
    validate_secret,
)
class MyKey( PrivateKey ):

    def __init__(self, secret=None, context=GLOBAL_CONTEXT):
        # self.secret =  validate_secret(secret) if secret is not None else get_valid_secret()
        # self.context = context
        # self.public_key = PublicKey.from_valid_secret(self.secret, self.context)
        PrivateKey.__init__(self, secret, )


    def my_sign_recoverable(self, message, hasher=None, custom_nonce_data=None):
            msg_hash = hasher(message) if hasher is not None else message
            if len(msg_hash) != 32:
                raise ValueError('Message hash must be 32 bytes long.')

            signature = ffi.new('secp256k1_ecdsa_recoverable_signature *')

            if custom_nonce_data:
                signed = lib.secp256k1_ecdsa_sign_recoverable(
                    self.context.ctx, signature, msg_hash, self.secret, ffi.NULL, custom_nonce_data
                )
            else:
                signed = lib.secp256k1_ecdsa_sign_recoverable(
                    self.context.ctx, signature, msg_hash, self.secret, ffi.NULL, ffi.NULL
                )

            if not signed:
                raise ValueError('The nonce generation function failed, or the private key was invalid.')

            return serialize_recoverable(signature, self.context)

def ecsign_custome_nonce(rawhash, key, nonce_data):
    # if coincurve and hasattr(coincurve, 'PrivateKey'):
    if True:
        pk = MyKey(key)
        # signature = pk.sign_recoverable(rawhash, hasher=None)
        # custom_nonce = (ffi.NULL , nonce_data )
        sig_der = pk.my_sign_recoverable(rawhash, hasher=None, custom_nonce_data=nonce_data)
        return sig_der

def main3():

    # test_data = 'b099531a13633f8cfb89b65b7794b1f8ecca8d03ab6bfd846d849d4609cd0ad0'
    test_data = '0251bfdfb21cc79f0b86b23ff47442ad9a1bc4336da83b71c194a524b984e9bf'
    priv_key =  '6fad07bf7166af32c864ec730df8a83ea87eeb8673f758e801f036e01000723f'
    # if True:
    cnt = 0
    while True:
        # shaData = hashlib.sha256(unhexlify(test_data)).digest()
        # print(hexlify(shaData))

        # print(unhexlify(test_data))
        indata = unhexlify(test_data)
        print(len(indata))
        print(type(indata))

        nonce_data =  hashlib.sha256( indata + bytearray(cnt) ).digest()
        print('nonce_data:{}'.format(hexlify(nonce_data)))

        sig_rsi = ecsign_custome_nonce(indata, unhexlify( priv_key), nonce_data)
        print(len(sig_rsi))
        print(hexlify(sig_rsi))
        if _is_canoial_ex(sig_rsi):
            from src.demo3 import MyEosKey
            eoskey = MyEosKey('5JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw')
            print("sig_r:{}".format(hexlify(sig_rsi[:32])))
            print("sig_s:{}".format(hexlify(sig_rsi[32:64])))

            # calc_sig = sig_rsi[:64]
            # i = eoskey._recovery_pubkey_param( indata,  calc_sig )

            new_sig_rsi =  bytes([int(sig_rsi[64]) + 4 + 27]) + sig_rsi[:64]
            print("sig_i:{}".format(new_sig_rsi[0]))
            print( 'SIG_K1_' + eoskey._check_encode(hexlify(new_sig_rsi), 'K1').decode() )

            print('----------find-------------')
            break
        cnt += 1
    pass

if __name__ == '__main__':

    # main1()
    # main2()
    main3()
