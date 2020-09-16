#!coding:utf8

#author:yqq
#date:2020/2/6 0006 14:07
#description:  XLM 充币扫描实现

import sys

if sys.version_info < (3, 0):
    print("please use python3")
    raise Exception("please use  python3 !!")


import sys
sys.path.append('.')
sys.path.append('..')

from config import XLM_RPC_HOST
import time
from time import sleep
from datetime import datetime
import sql
from dateutil import parser

import decimal
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 30
from utils import RoundDown
from pprint import pprint
from utils import  timestamp_parse

from stellar_sdk.server import Server

class  XLMScanner(object):

    def __init__(self):
        pass

    def _GetExDepositAccountFromDB(self):
        try:
            sqlstr = """SELECT DISTINCT `address` from `tb_xlm_deposit_addrs`;"""
            sql_result = sql.run(sqlstr)
            addrs = []
            for item in sql_result:
                if 'address' not in item: continue
                addrs.append(item['address'].strip())
            return addrs
        except  Exception as e:
            print(" _GetAddresses() error: ", e)
            return []

    def _PushTxIntoDB(self, tx : dict) -> bool:

        try:
            # for tx in txs:
            if True:
                strSql = """INSERT INTO tb_xlm_deposit(`txid`,`timestamp`,`src_account`,`dst_account`,`amount`,`symbol`,`confirmations`, `memo`, `paging_token`) """
                strSql += f"""VALUES('{tx['txid']}',{tx['timestamp']},'{tx['src_account']}',
                            '{tx['dst_account']}','{tx['amount']}','{tx['symbol']}',
                            {tx['confirmations']},'{tx['memo']}', '{tx['paging_token']}') """

                strSql += """ ON DUPLICATE KEY UPDATE `confirmations`={}; """.format(tx['confirmations'])
                print("sql: {}  ".format(strSql))
                sqlRet = sql.run(strSql)

            return True
        except Exception as e:
            print("PushTxDataIntoDB( txDatas):", e)
            return False

    def _LoadLastPagingToken(self):
        # Get the last paging token from a local database or file
        strsql = """SELECT MAX(`paging_token`) from tb_xlm_deposit;"""
        sql_result = sql.run(strsql)
        if not sql_result:
            return None

        if 'MAX(`paging_token`)' in sql_result[0]:
            max_paging_token = sql_result[0]['MAX(`paging_token`)']
            if max_paging_token != None:
                return max_paging_token

        return None

    def StartScan(self):



        # server = Server("http://horizon-testnet.stellar.org")
        server = Server(XLM_RPC_HOST)
        accounts = self._GetExDepositAccountFromDB()
        if 0 == len(accounts):
            print("NO DEPOSIT ACCOUNT FOUND! PLEASE ADD ACCOUNT FISRTLY!!")
            return

        ex_deposit_account = accounts[0]


        payments = server.payments().for_account(ex_deposit_account)
        last_paging_token = self._LoadLastPagingToken()
        if last_paging_token:
            payments.cursor(last_paging_token)


        #########################
        #1.也是轮询
        for payment in payments.stream():

        #########################
        #2.使用同步的方式(http短连接轮询)
        # print('before call')
        # rsp = payments.call()
        # print('after call')
        # if ('_embedded' not in rsp) :
        #     print("_embedded not in response")
        #     return
        # if 'records' not in rsp['_embedded']:
        #     print('records not in _embedded')
        #     return
        #
        # trxs = rsp['_embedded']['records']
        # for payment in trxs:
        #########################


            pprint(payment)

            # Record the paging token so we can start from here next time.
            # save_paging_token(payment["paging_token"])

            # We only process `payment`, ignore `create_account` and `account_merge`.
            if payment["type"] != "payment":
                continue

            # The payments stream includes both sent and received payments. We
            # only want to process received payments here.
            if payment['to'] != ex_deposit_account:
                continue

            # In Stellar’s API, Lumens are referred to as the "native" type. Other
            # asset types have more detailed information.
            if payment["asset_type"] == "native":
                # asset = "Lumens"
                asset = "XLM"
            else:
                print( f"received : {payment['asset_code']}:{payment['asset_issuer']}" )
                continue
                # asset = f"{payment['asset_code']}:{payment['asset_issuer']}"
            print(f"{payment['amount']} {asset} from {payment['from']}")

            if not payment['transaction_successful']:
                pprint(f'a failed transaction {payment}')
                continue

            txdetails = server.transactions().transaction(payment['transaction_hash']).call()
            if txdetails and 'memo' in txdetails and  txdetails['memo_type'] != 'text':
                print(f"memo_type is no `text` {txdetails}")
                continue

            strmemo = str(txdetails['memo'])
            if not (strmemo.isalnum() and 2 < len(strmemo) <= 10 ):
                print(f'memo is invalid : {strmemo}')
                strmemo = '1'


            txinfo = {
                'txid' : payment['transaction_hash'],
                'timestamp' : timestamp_parse(payment['created_at']),
                'src_account' : payment['from'],
                'dst_account' : payment['to'],
                'amount' : payment['amount'],
                'symbol' : asset,
                'memo': strmemo,
                'confirmations' : 100,
                'paging_token' : payment['paging_token']
            }

            self._PushTxIntoDB(txinfo)

        print('one scan loop overed.')

        pass



def main():
    scanner  = XLMScanner()

    while True:
        try:
            scanner.StartScan()
            sleep(15)
        except Exception as e:
            print("error: %s" % str(e))
            sleep(15)



    pass


if __name__ == '__main__':

    main()