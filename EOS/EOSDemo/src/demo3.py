#!coding:utf8

#author:yqq
#date:2019/9/23 0023 13:40
#description:
import eospy
import pytz
import eospy.cleos
import eospy.keys
import json

from eospy.types import Transaction

def eos_make_raw_transaction():
    ce = eospy.cleos.Cleos(url='http://jungle2.cryptolions.io:80')

    arguments = {
        "from": "yangqingqin1",  # sender
        "to": "hetbitesteos",  # receiver
        "quantity": '0.6646 EOS',  # In EOS
        "memo": "123923422",
    }
    payload = {
        "account": "eosio.token",
        "name": "transfer",
        "authorization": [{
            "actor": "yangqingqin1",
            "permission": "active",
        }],
    }

    # arguments = {
    #     "from": "hetbitesteos",  # sender
    #     "to": "yangqingqin1",  # receiver
    #     "quantity": '1.1234 EOS',  # In EOS
    #     "memo": "EOS to the moon",
    # }
    # payload = {
    #     "account": "eosio.token",
    #     "name": "transfer",
    #     "authorization": [{
    #         "actor": "hetbitesteos",
    #         "permission": "active",
    #     }],
    # }



    # Converting payload to binary
    data = ce.abi_json_to_bin(payload['account'], payload['name'], arguments)
    # Inserting payload binary form as "data" field in original payload
    payload['data'] = data['binargs']
    # final transaction formed
    trx = {"actions": [payload]}
    import datetime as dt
    # trx['expiration'] = str((dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))
    trx['expiration'] = str((dt.datetime.utcnow() + dt.timedelta(seconds=60 * 60)).replace(tzinfo=pytz.UTC))

    print(json.dumps(trx))

    # key = eospy.keys.EOSKey('5JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw')

    # resp = ce.push_transaction(trx, key, broadcast=False)
    # print(resp)

    chain_info, lib_info = ce.get_chain_lib_info()
    rawtx = Transaction(trx, chain_info, lib_info)
    encoded = rawtx.encode()
    print( "encode: {}".format( encoded) )
    from eospy.utils import sig_digest
    digest = sig_digest(rawtx.encode(), chain_info['chain_id'])
    print( "digest: {}".format( digest) )

    return rawtx, digest


import base58
import os
import ecdsa
import re
from binascii import hexlify, unhexlify
import hashlib
import time
import struct
import array

class MyEosKey( eospy.keys.EOSKey ):

    def __init__(self, private_str='') :
      eospy.keys.EOSKey.__init__(self, private_str)

    def sign_ex(self, digest):
        ''' '''
        cnt = 0
        # convert digest to hex string
        digest = unhexlify(digest)
        if len(digest) != 32:
            raise ValueError("32 byte buffer required")
        while 1:
            print('-------------------------------')
            # get deterministic k
            if cnt:
                sha_digest = hashlib.sha256(digest + bytearray(cnt)).digest()
            else:
                sha_digest = hashlib.sha256(digest).digest()

            print("sha:{}".format(  hexlify(sha_digest)))

            k = ecdsa.rfc6979.generate_k(self._sk.curve.generator.order(),
                                         self._sk.privkey.secret_multiplier,
                                         hashlib.sha256,
                                           # hashlib.sha256(digest + struct.pack('d', time.time())).digest() # use time to randomize
                                         sha_digest
                                         )
            # print("k:{}".format( k))
            # sign the message
            sigder = self._sk.sign_digest(digest, sigencode=ecdsa.util.sigencode_der, k=k)
            # sigder = self._sk.sign_digest(digest, sigencode=ecdsa.util.sigencode_der)
            #print(sigder)
            print('sigder:' + ''.join( [hex(i)[2:]  for i in sigder ]))

            # reformat sig
            r, s = ecdsa.util.sigdecode_der(sigder, self._sk.curve.generator.order())
            print("r:{}".format(  hex(r)))
            print("s:{}".format(  hex(s)))

            sigder = array.array('B', sigder)
            # print(sigder)

            sig = ecdsa.util.sigencode_string(r, s, self._sk.curve.generator.order())

            # ensure signature is canonical
            lenR = sigder[3]
            lenS = sigder[5 + lenR]
            # print('--------------')
            # print([ i  for i in sig])
            # print('--------------')

            tmp_sig = struct.pack('<B', 0) + sig

            # if True:
            # if self._is_canonical(tmp_sig):
            if lenR == 32 and lenS == 32:
                # derive recover parameter
                i = self._recovery_pubkey_param(digest, sig)
                # compact
                i += 27
                # compressed
                i += 4
                sigstr = struct.pack('<B', i) + sig
                print([ i for i in sigstr])
                break
                # if self._is_canonical(sigstr):
                #     print('is canonical')
                #     break
            cnt += 1
            print('--------------------------------\n')
            if not cnt % 10:
                print('Still searching for a signature. Tried {} times.'.format(cnt))
                # encode

        print( "sigstr:{}".format( hexlify(sigstr)) )
        return 'SIG_K1_' + self._check_encode(hexlify(sigstr), 'K1').decode()



def eos_sign_raw_transaction(digest):
    key = MyEosKey('5JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw')
    priv, fmt, kt = key._parse_key('5JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw')
    print("privkey:{}".format( priv))

    return [ key.sign_ex(digest) ]



def eos_sign_raw_transaction_raw(digest):
    key = eospy.keys.EOSKey('5JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw')
    # priv, fmt, kt = key._parse_key('5JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw')
    # print("privkey:{}".format( priv))
    # sigstr = unhexlify('1f6115d60ff20f3fc7debe20959d48d93b01a1c45ace5bd7d46f48bae137ad72fc0a304eae702afdc3a0ad06cfdad40ec9b98cfdc8f8e5aa9573b419c66e6005c9')
    from .demo_coincurve import my_eos_sign
    sigstr = my_eos_sign(hexlify(digest))

    return [ 'SIG_K1_' + key._check_encode(hexlify(sigstr), 'K1').decode() ]
    # return [ key.sign(digest) ]



def test_base58_encode(digest):
    key = eospy.keys.EOSKey('5JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw')
    # priv, fmt, kt = key._parse_key('5JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw')
    # print("privkey:{}".format( priv))
    # sigstr = unhexlify('1f6115d60ff20f3fc7debe20959d48d93b01a1c45ace5bd7d46f48bae137ad72fc0a304eae702afdc3a0ad06cfdad40ec9b98cfdc8f8e5aa9573b419c66e6005c9')
    # from .demo_coincurve import my_eos_sign
    # sigstr = my_eos_sign(hexlify(digest))

    return [ 'SIG_K1_' + key._check_encode(hexlify(digest), 'K1').decode() ]
    # return [ key.sign(digest) ]


def test_abi_json_to_bin():
    ce = eospy.cleos.Cleos(url='http://jungle2.cryptolions.io:80')

    arguments = {
        "from": "yangqingqin1",  # sender
        "to": "hetbitesteos",  # receiver
        "quantity": '0.1234 EOS',  # In EOS
        "memo": "2349232",
    }

    payload = {
        "account": "eosio.token",
        "name": "transfer",
        "authorization": [{
            "actor": "yangqingqin1",
            "permission": "active",
        }],
    }
    # arguments = {
    #     "from": "hetbitesteos",  # sender
    #     "to": "yangqingqin1",  # receiver
    #     "quantity": '39.1235 EOS',  # In EOS
    #     "memo": "232424",
    # }
    # payload = {
    #     "account": "eosio.token",
    #     "name": "transfer",
    #     "authorization": [{
    #         "actor": "hetbitesteos",
    #         "permission": "active",
    #     }],
    # }

    # Converting payload to binary
    data = ce.abi_json_to_bin(payload['account'], payload['name'], arguments)
    print(data)



def eos_push_singed_raw_transaction(txdata):
    ce = eospy.cleos.Cleos(url='http://jungle2.cryptolions.io:80')

    rsp = ce.post('chain.push_transaction', params=None, data=txdata, timeout=30)
    print('-------------rsp---------')
    print(rsp)

def fix_sig_tmp():


    return


#{"compression": "none", "transaction": {"expiration": "2019-09-25T09:41:05.075339+00:00", "ref_block_num": 1734, "ref_block_prefix": 2902086935, "net_usage_words": 0, "max_cpu_usage_ms": 0, "delay_sec": 0, "context_free_actions": [], "actions": [{"account": "eosio.token", "name": "transfer", "authorization": [{"actor": "yangqingqin1", "permission": "active"}], "data": "10a6b36c3acba6f1c0a6b36c3acba6f1d20400000000000004454f53000000000f454f5320746f20746865206d6f6f6e"}], "transaction_extensions": []}, "signatures": ["SIG_K1_KWYjQdiqR2ypURZL3Rf2iRSKBwUokZeWDPWTFU1w3kwPhpFrybsUuJb3WzFJQCvZBwpnyr2m8vTF44N6QxY1ZTP5eKLgty"]}


def main():
    # a = test_abi_json_to_bin()
    # b = test_abi_json_to_bin()
    # c = test_abi_json_to_bin()
    # print(a == b == c)
    # return



    # data = '1f3b1ac9c7f4fda5044cae0f24042e6267be8a900e1bed35a39254e7fdd5a192622caef9ba81535f27ba4694a09b724d4379f7b56f6b12780486bc9c2fc9153732'
    #
    # print(test_base58_encode(unhexlify(data)))
    # return



    # final_trx ={"compression": "none", "transaction": {"expiration": "2019-09-30T10:40:11.998612+00:00", "ref_block_num": 4733, "ref_block_prefix": 3635564472, "net_usage_words": 0, "max_cpu_usage_ms": 0, "delay_sec": 0, "context_free_actions": [], "actions": [{"account": "eosio.token", "name": "transfer", "authorization": [{"actor": "yangqingqin1", "permission": "active"}], "data": "10a6b36c3acba6f1c0a6b36c3acba6f1d20400000000000004454f53000000000f454f5320746f20746865206d6f6f6e"}], "transaction_extensions": []}, "signatures": ["SIG_K1_K11vtuZpzujG3jHUAURVnypmg4YTDJPDXMzGJWySp7qzdJoFo4VaNpkc4A5jrH7FDzf1Zkw7PVjZHpkdBHd2Ca34X1vghP"]}
    # from eospy.types import EOSEncoder
    # data = json.dumps(final_trx, cls=EOSEncoder)
    # print(data)
    # eos_push_singed_raw_transaction(data)
    # pass
    # return

    trx,digest = eos_make_raw_transaction()
    #
    # digest = 'b099531a13633f8cfb89b65b7794b1f8ecca8d03ab6bfd846d849d4609cd0ad0'
    # digest = '0251bfdfb21cc79f0b86b23ff47442ad9a1bc4336da83b71c194a524b984e9bf'
    print("digest:{}".format(digest))
    sig = eos_sign_raw_transaction(digest)
    print('---------------sig-----------------')
    print(sig)
    # return

    # build final trx
    final_trx = {
        'compression': 'none',
        'transaction': trx.__dict__,
        'signatures': sig
        # 'signatures': []
    }
    print('---------------data------------------')
    from eospy.types import EOSEncoder
    data = json.dumps(final_trx, cls=EOSEncoder)
    print(data)
    eos_push_singed_raw_transaction(data)
    pass


if __name__ == '__main__':

    # main()
    main()