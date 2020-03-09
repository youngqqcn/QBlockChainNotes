#!coding:utf8

#author:yqq
#date:2020/3/4 0004 10:23
#description:


from tronapi import Tron

from tronapi.trx import  Trx
import logging
from pprint import pprint

import hashlib
from binascii import hexlify, unhexlify


from src.my_variant_encoding import my_encode_int64

from time import sleep

import coincurve


def safe_ord(value):
    if isinstance(value, int):
        return value
    else:
        return ord(value)

def new_ecsign(rawhash, key):
    if coincurve and hasattr(coincurve, 'PrivateKey'):
        pk = coincurve.PrivateKey(key)
        signature = pk.sign_recoverable(rawhash, hasher=None)
        v = safe_ord(signature[64]) + 27
        r = signature[0:32]
        s = signature[32:64]

        sig = r + s + unhexlify(hex(v)[2:])

        return sig




def main():
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger()

    full_node = 'https://api.trongrid.io'
    solidity_node = 'https://api.trongrid.io'
    event_server = 'https://api.trongrid.io'



    privkey = "你的私钥"


    tron = Tron(full_node=full_node,
                solidity_node=solidity_node,
                event_server=event_server,
                private_key=privkey)


    trx = Trx(tron)


    from_addr = 'TPcUx2iwjomVzmX3CHDDYmnEPJFTVeyqqS'
    to_addr = 'TDUjsjJzQABwVv8DnLVDZ778uKQ7X5Fs7E'
    options = {
        'from' : from_addr
    }

    amount = float(0.123)

    # receipt = trx.send_transaction( to=to_addr, amount=amount, options=options )


    #构造交易
    tx = trx.tron.transaction_builder.send_transaction(
        to_addr,
        amount,
        options['from']
    )








    if  False:
        sign = trx.sign(tx)

        sleep(61)  # 休眠 61秒  广播时报错:  {'code': 'TRANSACTION_EXPIRATION_ERROR', 'message': 'transaction expired'}

        result = trx.broadcast(sign)
        pprint(result)

        return



    old_expiration_hex = my_encode_int64(tx['raw_data']['expiration'])

    #改变 raw_data.expiration,  增加一个小时
    tx['raw_data']['expiration'] +=  3600 * 1000

    new_expiration_hex = my_encode_int64(tx['raw_data']['expiration'])

    #也要改变  raw_data_hex 中相应的字段

    # tmp_hex = tx['raw_data_hex'][30:]
    # tx['raw_data_hex'] = tx['raw_data_hex'][0:30]



    raw_data_hex = str(tx['raw_data_hex'])
    index =  raw_data_hex.find(old_expiration_hex)
    logger.info( "index : {}".format( index) )

    new_raw_data_hex = raw_data_hex.replace(old_expiration_hex, new_expiration_hex)

    old_txid = hashlib.sha256( unhexlify( tx['raw_data_hex'] )).hexdigest()

    new_txid = hashlib.sha256( unhexlify( new_raw_data_hex) ).hexdigest()

    if old_txid == tx['txID'] :
        logger.info('txid 比对成功!')
    else:
        logger.info('txid比对失败!')

    tx['txID'] = new_txid


    sign = trx.sign(tx)


    my_sig = new_ecsign( unhexlify( new_txid), unhexlify( privkey) )

    logger.info( type(hexlify(my_sig)) )
    logger.info( type(sign['signature'][0] ))

    logger.info( "我的签名: {}".format( str(hexlify(my_sig), encoding='latin') ))

    logger.info("原始签名: {}".format( sign['signature'][0] ))

    if sign['signature'][0] == str(hexlify(my_sig), encoding='latin'):
        logger.info('签名对比成功!')
    else:
        logger.info('签名对比失败')



    sleep(61)  #休眠 61秒,  来测试修改 expiration的效果

    result = trx.broadcast(sign)
    pprint(result)

    #测试成功  txid为:  8c2b0a40812be8bcee3f92587e6824dc5a6035572cffe13707211821085ea7d3

    pass



if __name__ == '__main__':

    main()
    

