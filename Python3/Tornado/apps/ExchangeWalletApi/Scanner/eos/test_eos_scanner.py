#!coding:utf8

#author:yqq
#date:2019/12/26 0026 16:26
#description:


import sys

if sys.version_info < (3, 0):
    print("please use python3")
    raise Exception("please use  python3 !!")


import time
import sql
import json
from  eos.eos_proxy import EosProxy
from dateutil import parser

import decimal
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 30
from utils import RoundDown
from utils import timestamp_parse
from pprint import  pprint
import requests

from eos.eos_scanner import EosScanner
from pprint import pprint
import unittest
import time

class TestScanner(unittest.TestCase):

    def setUp(self):
        # self.scanner = EosScanner(node_host='https://api.eosnewyork.io')
        self.test_account = 'hetbitesteos'
        self.scanner = EosScanner(node_host='http://jungle2.cryptolions.io:80')
        pass

    def test__GetAddresses(self):
        try:
            addrs = self.scanner._GetAddresses()
            print('--------test_GetAddresses---------')
            print(addrs)
            print('----------------------------------')
            self.assertFalse(len(addrs) == 0)
        except Exception as e:
            print(e)
            self.assertTrue(False)


    def test__GetBalanceAndScannedBlockFromDB(self):
        try:
            account, str_balance, n_scanned_block = self.scanner._GetBalanceAndScannedBlockFromDB(self.test_account)
            print('--------test_GetBalanceAndScannedBlockFromDB-----------')
            print('{} , {}, {}'.format(account, str_balance, n_scanned_block))
            print('--------------------------------------')
            self.assertEqual(account, 'hetbitesteos', 'account is not equal!')
            self.assertGreater(Decimal(str_balance), Decimal('0'), 'balance is less than 0!')
            self.assertGreater(n_scanned_block, 0, 'scanned block is less than 0!')
        except Exception as e:
            print(e)
            self.assertTrue(False)
            pass


    def test__GetCoreLiquidBalanceAndHeaderBlockNum(self):
        try:
            n_header_block_num, decm_balance = self.scanner._GetCoreLiquidBalanceAndHeaderBlockNum(self.test_account)
            print('----------test__GetCoreLiquidBalanceAndHeaderBlockNum------------')
            print('{}, {}'.format(n_header_block_num, decm_balance))
            print('------------------------------')
            self.assertGreater(n_header_block_num,  9999, 'n_header_block_num is less than 9999')
            self.assertGreater(decm_balance, Decimal('0'), 'decm_balance is less than 0')
        except Exception as e:
            print(e)
            self.assertTrue(False)
            pass




    def test__GetDepositTrxsFromBlock(self):
        try:
            trxs = self.scanner._GetDepositTrxsFromBlock(block_number=96628988)
            print('---------test__GetDepositTrxsFromBlock----------------')
            pprint(trxs)
            print('----------------------------------------')
            self.assertTrue(isinstance(trxs, list), 'trxs is not list')
            self.assertFalse(len(trxs) == 0, 'trxs is empty list')
        except Exception as e:
            print(e)
            self.assertTrue(False)
            pass


    def test__UpdateBalanceAndScannedBlockIntoDB(self):
        try:
            self.scanner._UpdateBalanceAndScannedBlockIntoDB(self.test_account, 96628980, '1.234')
        except Exception as e:
            print(e)
            self.assertTrue(False)
            pass


    def test_StartScan(self):
        try:
            self.scanner.StartScan(enable_speedup_plugin=False)
            pass
        except Exception as e:
            print(e)
            self.assertTrue(False)


    def test__SpeedUpPlugin_GetDepositTrxBlockNum(self):
        """仅适用主网"""
        try:
            retblknums = self.scanner._SpeedUpPlugin_GetDepositTrxBlockNum(self.test_account, 96628980, 99928980)
            print('---------test__SpeedUpPlugin_GetDepositTrxBlockNum---------')
            print(retblknums)
            print('--------------------------------------------------------')
            self.assertFalse( len(retblknums) == 0)
            pass
        except Exception as e:
            print(e)
            self.assertTrue(False)


def main():

    

    pass


if __name__ == '__main__':

    main()