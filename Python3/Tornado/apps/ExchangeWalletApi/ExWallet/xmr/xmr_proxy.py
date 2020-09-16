#!coding:utf8

#author:yqq
#date:2020/4/3 0003 17:33
#description:

import decimal
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 30
from utils import RoundDown

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from monero.wallet import Wallet
from monero.wallet import keccak_256
from monero.wallet import ed25519, const, address, base58
from monero.address import BaseAddress, Address, SubAddress
from monero.seed import Seed
from monero.transaction import IncomingPayment, OutgoingPayment, Transaction, PaymentFilter
from monero.backends.jsonrpc import JSONRPCWallet
from binascii import  hexlify, unhexlify
import struct
from monero.numbers import as_monero, to_atomic, from_atomic, PICONERO


class  XMR_Proxy(JSONRPCWallet):


    def refresh(self):
        return self.raw_request(method='refresh')


    #重写父类 export_outputs 方法
    def export_outputs(self):
        return self.raw_request(method='export_outputs', params={'all':True})
        pass


    #重写 import_key_images
    def import_key_images(self, key_images : list):
        rsp = self.raw_request('import_key_images', {'signed_key_images': key_images})
        # rpc.import_key_images()
        unspent = RoundDown(Decimal(rsp['unspent']) * PICONERO)
        spent = RoundDown(Decimal(rsp['spent']) * PICONERO)

        #这里转为浮点数返回
        retdata = {
            'height': rsp['height'],
            'unspent': unspent,
            'spent': spent
        }
        return retdata



    #重写transfer
    def transfer(self, destinations : list, priority = 0,
            payment_id=None, unlock_time=0, account=0,relay=False):

        dests = [(dst['address'], dst['amount']) for dst in  destinations]

        params = {
            'account_index': account,
            'destinations': list(map(lambda dst: {'address': dst[0], 'amount': to_atomic(dst[1])}, dests)),
            'priority': priority,
            'unlock_time': 0,
            'get_tx_keys': False,
            'get_tx_hex': False,
            'do_not_relay': not relay,
        }

        # 参考: https://github.com/monero-project/monero/blob/master/src/wallet/wallet2.cpp#L109
        # unsigned_txset 开头固定是 4d6f6e65726f20756e7369676e65642074782073657404
        # 即:
        # binascii.b2a_hex( b'Monero unsigned tx set\004'  )
        # b'4d6f6e65726f20756e7369676e65642074782073657404'

        rawtxs = self.raw_request('transfer_split', params=params)
        return rawtxs


    def submit_transfer(self, signed_tx_hex : str):
        return self.raw_request(method='submit_transfer', params={'tx_data_hex' : signed_tx_hex })


    def balances(self, account=0):
        rsp = self.raw_request('getbalance', {'account_index': account})
        retdata = {
            'account_index' : 0,
            'unlocked_balance':  RoundDown(  from_atomic( rsp['unlocked_balance'] ) ) ,
            'balance':  RoundDown( from_atomic( rsp['balance'] ) ) ,
            'blocks_to_unlock' :  rsp['blocks_to_unlock']
        }
        return  retdata

