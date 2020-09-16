#!encoding:utf8

"""
author: yqq
date : 2019-08-19(进行代码重构)
description: 
    Cosmos区块监测程序, 获取交易交易所用户地址的充币信息
    支持 USDP  HTDF  HET 
"""

import sys

if sys.version_info < (3, 0):
    print("please use python3")
    raise Exception("please use  python3 !!")

import time
from time import sleep
from cosmos.cosmos_scanner import CosmosBlockScanner


import decimal
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 30
from utils import RoundDown


# s = RoundDown(Decimal('0.123456789012345'))


STR_COIN_TYPE = "htdf"

exec("from config import {}_NODE_RPC_HOST".format(STR_COIN_TYPE.upper()))
exec("from config import {}_NODE_RPC_PORT".format(STR_COIN_TYPE.upper()))

def main():
    print("start {} block scanner.........".format(STR_COIN_TYPE))
    scanner =  CosmosBlockScanner(
        eval("{}_NODE_RPC_HOST".format(STR_COIN_TYPE.upper())),
        eval("{}_NODE_RPC_PORT".format(STR_COIN_TYPE.upper())), 
         0, 
         0, 
        STR_COIN_TYPE, 
        "t_{}_charge".format(STR_COIN_TYPE),
        "t_{}_accounts".format(STR_COIN_TYPE), 
        "t_scan_start", 
        "t_{}_active_addrs".format(STR_COIN_TYPE), 
        "t_{}_patch_addrs".format(STR_COIN_TYPE))   

    while True:
        try:
            scanner.PatchForAddrsBalance() #查询patch表用户地址余额
            scanner.StartScanBlock()
        except Exception as e:
            print("error: %s" % str(e))
            sleep(15)
    pass



def test_bech32():
    from cosmos.my_bech32 import HexAddrToBech32, Bech32AddrToHex
    addr = 'htdf1kvq5t60r5j5x8skvyyw5xl8xk9tp2h8qj3s8vk'

    hexaddr = Bech32AddrToHex(addr=addr)
    # hexaddr = 'b30145e9e3a4a863c2cc211d437ce6b156155ce0'
    bech32addr = HexAddrToBech32('htdf', hexstraddr=hexaddr)
    print(bech32addr)
    pass

if __name__ == '__main__':
    main()
    # test_bech32()

