#!coding:utf8

#author:yqq
#date:2020/2/19 0019 17:23
#description:   TRX  区块扫描

import sys

if sys.version_info < (3, 0):
    print("please use python3")
    raise Exception("please use  python3 !!")

sys.path.append('.')
sys.path.append('..')
import logging

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
from utils import RoundDown
from pprint import pprint
from utils import  timestamp_parse


from tronapi import Tron
from tronapi.trx import Trx
from tronapi.common.account import Account

full_node = 'https://api.trongrid.io'
solidity_node = 'https://api.trongrid.io'
event_server = 'https://api.trongrid.io/'


# from logging.handlers import TimedRotatingFileHandler
# from logging.handlers import RotatingFileHandler

#
#
# def InitLogSetting():
#     #日志打印格式
#     # log_fmt = '%(asctime)s\tFile \"%(filename)s\",line %(lineno)s\t%(levelname)s: %(message)s'
#     log_fmt = '[%(asctime)s | %(pathname)s | PID %(process)d |func %(funcName)s | line %(lineno)d | %(levelname)s] %(message)s'
#
#     formatter = logging.Formatter(log_fmt)
#     #创建TimedRotatingFileHandler对象
#     log_file_handler = TimedRotatingFileHandler(filename="ds_update", when="M", interval=2, backupCount=2)
#     #log_file_handler.suffix = "%Y-%m-%d_%H-%M.log"
#     #log_file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}.log$")
#     log_file_handler.setFormatter(formatter)
#     logging.basicConfig(level=logging.INFO)
#
#
#     log = logging.getLogger()
#     log.addHandler(log_file_handler)


    #循环打印日志
    # log_content = "test log"
    # count = 0
    # while count < 30:
    #     log.error(log_content)
    #     time.sleep(20)
    #     count = count + 1
    # log.removeHandler(log_file_handler)



class TrxScanner(object):


    def __init__(self):

        self.N_BLOCK_COUNT_EACH_TIME = 5

        self.tron = Tron(full_node=full_node,
                    solidity_node=solidity_node,
                    event_server=event_server)

        self.api = Trx(tron=self.tron)

        # self.connected = self.tron.is_connected()

        self.addrs = self._GetExDepositAddrsFromDB()
        logging.info("len(addrs) : {}".format(len(self.addrs)))

        #使用 dict提高查询速度
        self.hex_addrs = set()
        for addr in self.addrs:
            self.hex_addrs.add(  str(self.tron.address.to_hex(address=addr)).lower()  )

        logging.info("hex_addr: {}".format(self.hex_addrs))

        pass


    def _GetExDepositAddrsFromDB(self):
        try:
            sqlstr = """SELECT DISTINCT `address` from `tb_trx_deposit_addrs`;"""
            sql_result = sql.run(sqlstr)
            addrs = []
            for item in sql_result:
                if 'address' not in item: continue
                addrs.append(item['address'].strip())
            return addrs
        except  Exception as e:
            logging.error(" _GetAddresses() error: {}".format( e))
            return []

    def _PushTxIntoDB(self, tx : dict) :
        strSql = """INSERT INTO tb_trx_deposit(`txid`,`timestamp`,`from`,`to`,`amount`,`symbol`,`confirmations`, `block_number`) """
        strSql += f"""VALUES('{tx['txid']}',{tx['timestamp']},'{tx['from']}',
                            '{tx['to']}','{tx['amount']}','{tx['symbol']}',{tx['confirmations']}, {tx['blocknumber']}) """

        strSql += """ ON DUPLICATE KEY UPDATE `confirmations`={}; """.format(tx['confirmations'])
        logging.info("sql: {}  ".format(strSql))

        sqlRet = sql.run(strSql)



    def _UpdateActiveBalance(self, addr : str):

        account_info = self.api.get_account(address=addr)

        if 'balance' in account_info:
            decBalance = Decimal(account_info['balance']) / Decimal('1000000')
            fmtBalance = decBalance.quantize(Decimal("0.000000"), getattr(decimal, 'ROUND_DOWN'))
        else:
            fmtBalance = '0.000000'

        strSql = """INSERT INTO `tb_trx_active_addrs`(`symbol`, `address`, `balance`)"""
        strSql += f"""VALUES('TRX', '{addr}', {fmtBalance})"""
        strSql += """ON DUPLICATE KEY  UPDATE `balance`=VALUES(`balance`);"""

        logging.info("sql: {}  ".format(strSql))

        sqlRet = sql.run(strSql)


        pass



    def _GetDepositTrxsFromBlockRange(self, nStart : int, nEnd : int):

        logging.info("starting get block {} to {}".format(nStart, nEnd))

        #TODO: 可以增加 visible字段, 地址会以 Base58格式返回; 如果是代币, assetname会是代币名称
        blocks_info = self.api.get_block_range(start=nStart, end=nEnd)
        if not blocks_info:
            raise Exception("blocks_info is none")

        rettrxs = []

        for oneblock in blocks_info:

            try:
                if 'transactions' not in oneblock:
                    continue

                transactions = oneblock['transactions']
                for tx in transactions:
                    valueinfo = tx['raw_data']['contract'][0]['parameter']['value']

                    # 只包含   amount,  owner_address,  to_address
                    if len(valueinfo) != 3:
                        logging.info("valueinfo's length is not 3, pass it! ")
                        continue

                    if 'amount' not in valueinfo:
                        logging.info("amount not in valueinfo, it's not normal TRX transaction")
                        continue


                    dst_hex_addr = valueinfo['to_address']
                    src_hex_addr = valueinfo['owner_address']

                    # 如果from地址是交易所的地址(一般是归集操作)
                    if src_hex_addr in self.hex_addrs:
                        src_b58_addr = str(self.tron.address.from_hex(valueinfo['owner_address']), encoding='utf8')
                        self._UpdateActiveBalance(addr=src_b58_addr)


                    if  dst_hex_addr not in self.hex_addrs:
                        logging.info("addr {} is not exchange addr".format(dst_hex_addr))
                        continue
                    else: #如果目的地址是交易所的地址, 则跟新活跃地址表的余额, 方便后期归集
                        dst_b58_addr = str(self.tron.address.from_hex(dst_hex_addr), encoding='utf8')
                        self._UpdateActiveBalance(addr=dst_b58_addr)


                    src_b58_addr = str(self.tron.address.from_hex(src_hex_addr), encoding='utf8')
                    dst_b58_addr = str(self.tron.address.from_hex(dst_hex_addr), encoding='utf8')
                    txid = tx['txID']
                    blocknumber = oneblock['block_header']['raw_data']['number']
                    timestamp = int(tx['raw_data']['timestamp'] / 1000)

                    damount = Decimal(str(valueinfo['amount'])) / Decimal('1000000')
                    stramount = damount.quantize(Decimal("0.000000"), getattr(decimal, 'ROUND_DOWN'))



                    successed = ("SUCCESS" == tx['ret'][0]['contractRet'])
                    if not successed:
                        logging.info("tx {} is not successed tx".format(txid))
                        continue

                    txinfo = {
                        'txid' : txid,
                        'to' : dst_b58_addr,
                        'from': src_b58_addr,
                        'amount': stramount,
                        'timestamp': timestamp,
                        'blocknumber' : blocknumber,
                        'confirmations': 100,
                        'symbol' : 'TRX'
                    }

                    logging.info('found a deposit tx: {}'.format(txinfo))



                    rettrxs.append(txinfo)


            except Exception as e:
                logging.error(e)
                continue

        return rettrxs


    def __GetScanStartBlock(self, strCoinType):
        """
        从数据库中获取币种的 扫描的起始区块
        """

        #类型判断
        assert (isinstance( strCoinType, str) )

        #对参数进行检查
        #注意sql注入
        strType = strCoinType.lower()
        sqlRet = sql.run("""SELECT start_block FROM t_scan_start WHERE coin_type='{0}';""".format(strType))
        if len(sqlRet) > 0 :
            item = sqlRet[0]
            if 'start_block' in item:
                nRet = int(str(item['start_block']), 10)
                return nRet
        return 0

    def __GetLatestBlockNumber(self):
        while True:
            try:
                block = self.api.get_current_block()
                number = block['block_header']['raw_data']['number']
                return number
            except Exception as e:
                logging.error("{},  will try again".format(e))




    def StartScan(self):

        nLatestestBlock = self.__GetLatestBlockNumber()
        nStartBlock = self.__GetScanStartBlock('trx')

        # for n in range(nStartBlock, nLatestestBlock + 1):
        n = nStartBlock

        while n < nLatestestBlock + 1:

            nTmpEnd = n + self.N_BLOCK_COUNT_EACH_TIME if n + self.N_BLOCK_COUNT_EACH_TIME <= nLatestestBlock + 1 else nLatestestBlock + 1

            txs = self._GetDepositTrxsFromBlockRange(n, nTmpEnd)

            for tx in txs:
                self._PushTxIntoDB(tx)

            # 保存本次扫描的结束区块高度
            strSql = """update t_scan_start set start_block={0} where coin_type='{1}';""".format(nTmpEnd - 1, 'trx')
            logging.info("sql : {}".format(strSql))
            sql.run(strSql)

            n = nTmpEnd

        pass






def InitLoggingSetting():
    log_format = '[%(asctime)s | %(pathname)s | PID %(process)d |func %(funcName)s | line %(lineno)d | %(levelname)s] %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)



def main():
    InitLoggingSetting()

    logging.info("trx scanner starting ...")


    trxscanner = TrxScanner()
    logging.info("init scanner successed")

    while True:
        try:
            trxscanner.StartScan()
        except Exception as e:
            logging.error("{}".format(e))
            sleep(0.1)
            pass


    # trxs  = trxscanner._GetDepositTrxsFromBlockRange(nStart=14455630, nEnd=14455635)
    # for tx in trxs:
    #     trxscanner._PushTxIntoDB(tx)


    pass


if __name__ == '__main__':

    main()