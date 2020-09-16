#!coding:utf8

#author:yqq
#date:2019/12/11 0011 13:48
#description:


import sys

if sys.version_info < (3, 0):
    print("please use python3")
    raise Exception("please use  python3 !!")


import sys
sys.path.append('.')
sys.path.append('..')

from config import RIPPLE_RPC_HOST
# from config import RIPPLE_RPC_PORT
from ripple.ripple_proxy import RippleProxy
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

class RippleScanner(object):

    def __init__(self, url : str ):
        self.rpcnode = RippleProxy(url)
        self.addrs = self._GetAddresses()


    def _GetAddresses(self) -> list:

        """
        获取地址
        :return:   [addr1, addr2]
        """
        try:
            sqlstr = """SELECT DISTINCT `address` FROM `tb_xrp_deposit_addrs`;"""
            sql_result = sql.run(sqlstr)
            addrs = []
            for item in sql_result:
                if 'address' not in item: continue
                addrs.append(item['address'].strip())
            return addrs
        except  Exception as e:
            print(" _GetAddresses() error: " , e)
            return []




    def _GetStartTimestamp(self) -> int:
        """
        获取起始时间戳, 如果没有则以   2019-12-01 00:00  UTC-0 为默认值
        :return:  int
        """

        try:
            # sqlstr = """SELECT MAX(`timestamp`) FROM `tb_xrp_deposit`  WHERE `sequence`>99999; """
            sqlstr = """SELECT MAX(`timestamp`) FROM `tb_xrp_deposit`;"""
            sql_result = sql.run(sqlstr)

            if 'MAX(`timestamp`)' in sql_result[0]:
                max_timestamp = sql_result[0]['MAX(`timestamp`)']
                if max_timestamp != None:
                    return max_timestamp

            dtstr = "2019-12-01T00:00:00+00:00"
            dt = parser.parse(dtstr)
            default_time = int(dt.timestamp())
            return default_time

        except  Exception as e:
            print(" _GetStartTimestamp() error: " , e)
            return 1575158400



    def _GetTransactions(self,  starttime : int) -> list:

        try:

            deposit_txs_ret = []
            for addr in self.addrs:

                # 获取所有交易(包括分页处理)
                all_transactions = []
                marker = None
                while True:
                    params = dict(
                        limit=20,
                        start=starttime,
                        result='tesSUCCESS',
                        type='Payment'
                    )
                    if marker:  params['marker'] = marker

                    response = self.rpcnode.get_account_transaction_history(address=addr, **params)
                    if 'result' not in response:
                        if 'status' in response:  # 发生错误
                            print(response)
                        break

                    if response['count'] > 0:
                        all_transactions.extend(response['transactions'])

                    marker = response['marker'] if 'marker' in response else None
                    if marker == None: break

                # 处理所有交易
                for tx in all_transactions:

                    #2020-06-23
                    # 不填memo的 直接跳过
                    # if not ('Amount' in tx['tx'] and 'DestinationTag' in tx['tx']):
                    #     print('not found `Amount` , `DestinationTag` in tx, skipped! tx:{}'.format(tx['hash']))
                    #     continue



                    # 检查是否是 'XRP' 的交易, 如果是dict类型则是其他货币,如'USD'
                    currency_amount = tx['tx']['Amount']
                    if not isinstance(currency_amount, str):
                        continue

                    destination = tx['tx']['Destination']
                    if addr != destination:
                        continue

                    tx_type = tx['tx']['TransactionType']
                    if tx_type != 'Payment':
                        continue

                    tx_reuslt = tx['meta']['TransactionResult']
                    if tx_reuslt != 'tesSUCCESS':
                        continue

                    tmp_deposit_tx = {}
                    tmp_deposit_tx['txid'] = tx['hash']
                    tmp_deposit_tx['timestamp'] = int(parser.parse(tx['date']).timestamp())  #会自动转为当前时区时间UTC+8
                    tmp_deposit_tx['ledger_index'] = tx['ledger_index']
                    tmp_deposit_tx['sequence'] = tx['tx']['Sequence']
                    tmp_deposit_tx['src_addr'] = tx['tx']['Account']
                    tmp_deposit_tx['dst_addr'] = tx['tx']['Destination']
                    tmp_deposit_tx['destination_tag'] = str(tx['tx']['DestinationTag']) if 'DestinationTag' in tx['tx'] else '1'  # 约定, 默认填充 '1'
                    tmp_deposit_tx['source_tag'] = str(tx['tx']['SourceTag']) if 'SourceTag' in tx['tx'] else '1'  # 约定, 默认填充 '1'
                    tmp_deposit_tx['delivered_amount'] = '%.8f' % RoundDown( Decimal(tx['meta']['delivered_amount']) / Decimal(10 ** 6))  # 防止假充值
                    tmp_deposit_tx['confirmations'] = 1


                    #处理非法tag , 2020-02-09
                    if not( len(tmp_deposit_tx['destination_tag']) <= 10 and tmp_deposit_tx['destination_tag'].isalnum()):
                        tmp_deposit_tx['destination_tag'] = '1'

                    if not( len(tmp_deposit_tx['source_tag']) <= 10 and tmp_deposit_tx['source_tag'].isalnum()):
                        tmp_deposit_tx['source_tag'] = '1'

                    deposit_txs_ret.append(tmp_deposit_tx)

            return deposit_txs_ret

        except Exception as e:
            print("_GetTransactions() error:", e)
            return []



    def _PushTxIntoDB(self, txs : list) -> bool:

        try:
            for tx in txs:
                strSql = """INSERT INTO tb_xrp_deposit(`txid`,`timestamp`,`src_addr`,`dst_addr`,`delivered_amount`,`ledger_index`,`sequence`,`confirmations`, `destination_tag`, `source_tag`) """
                strSql += """ VALUES('{}',{},'{}','{}','{}',{},{},{},{},{})  """\
                            .format( tx['txid'], tx['timestamp'], tx['src_addr'], tx['dst_addr'], tx['delivered_amount'],
                                     tx['ledger_index'] , tx['sequence'], tx['confirmations'], tx['destination_tag'], tx['source_tag'])
                strSql += """ ON DUPLICATE KEY UPDATE `confirmations`={}; """.format(tx['confirmations'])
                print("sql: {}  ".format(strSql))
                sqlRet = sql.run(strSql)

            return True
        except Exception as e:
            print("PushTxDataIntoDB( txDatas):", e)
            return False


    def StartScan(self):
        """
        开始获取交易
        :return:
        """

        starttime = self._GetStartTimestamp()
        txs = self._GetTransactions(starttime=starttime)
        self._PushTxIntoDB(txs)

        # sleep(5 * 60) #5分钟查一次
        for i in range(5 * 60):
            sleep(1)
            strtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            print("{} sleeping...".format(strtime))

        pass




def main():

    scanner = RippleScanner(url=RIPPLE_RPC_HOST)
    # starttime = scanner._GetStartTimestamp()
    # txs  = scanner._GetTransactions(starttime)

    while True:
        try:
            scanner.StartScan()
        except Exception as e:
            print("error: %s" % str(e))
            sleep(15)

    pass


if __name__ == '__main__':

    main()