# -*- coding: utf-8 -*-
"""
author: yqq
date: 2019-05-11 20:26
descriptions: USDP处理
"""
import json

from base_handler import BaseHandler
from utils import decimal_default,str_to_decimal,get_linenumber
from .proxy import USDPProxy
from constants import USDP_IP_ADDR, USDP_RPC_PORT

g_IP, g_PORT = USDP_IP_ADDR, USDP_RPC_PORT

            
class USDP_GetBalance(BaseHandler):
    @staticmethod
    def get_balance(rpcconn, addr):
        balance = rpcconn.getBalance(addr)
        return balance

    def post(self):
        rpcconn = USDPProxy(g_IP, g_PORT)
        try:
            address = self.get_argument("address")
            if len(address) != 43:
                self.write(json.dumps(BaseHandler.error_ret_with_data("arguments error")))
                return
            balance = USDP_GetBalance.get_balance(rpcconn, address)
            self.write(json.dumps(BaseHandler.success_ret_with_data(str(balance)), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("USDP_GetBalance error:{0} in {1}".format(e,get_linenumber()))

           
class USDP_SendRawTransaction(BaseHandler):
    def post(self):
        rpcconn = USDPProxy(g_IP, g_PORT)
        try:
            data = str(self.get_argument("tx"))
            if len(data) < 40:
                self.write(json.dumps(BaseHandler.error_ret_with_data("arguments error")))
                return
            rsp = rpcconn.sendRawTransaction(data)

            retData = {}
            retData["txid"] = rsp["txhash"]
            retData["blockNumber"] = rsp["height"]
            retData["gasUsed"] = str(float(rsp["gas_used"])/(10**8))

            self.write(json.dumps(BaseHandler.success_ret_with_data(retData), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("USDP_SendRawTransaction error:{0} in {1}".format(e,get_linenumber()))

class USDP_ListAccounts(BaseHandler):
    @staticmethod
    def addresses():
        from sql import run
        accounts = run('select address from t_usdp_accounts')
        return [account['address'].strip() for account in accounts]

    def get(self):
        rpcconn = USDPProxy(g_IP, g_PORT)
        try:
            data = USDP_ListAccounts.addresses()
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("USDP_ListAccounts error:{0} in {1}".format(e,get_linenumber()))

            
class USDP_GetLatestBlockNumber(BaseHandler):
    @staticmethod
    def latest(rpcconn):
        lastestBlockNum = int(rpcconn.getLastestBlockNumber())
        return lastestBlockNum

    def get(self):
        rpcconn = USDPProxy(g_IP, g_PORT)
        try:
            data = USDP_BlockNumber.latest(rpcconn)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("USDP_BlockNumber error:{0} in {1}".format(e,get_linenumber()))

class USDP_GetTransactionFromBlock(BaseHandler):
    @staticmethod
    def getTransactionFromBlock(rpcconn, nBlockNum):
        data = rpcconn.getBlockByBlockNum(nBlockNum)
        import time
        timeStr = data["block_meta"]["header"]["time"]
        timeStr = timeStr[ : timeStr.rfind('.') ]
        ta = time.strptime(timeStr, "%Y-%m-%dT%H:%M:%S")
        timestamp = int(time.mktime(ta))
        print("timestamp", timestamp)


        retData = []
        txs = data["block"]["txs"]
        if not isinstance(txs, list): return []
        for tx in txs:
            txData = {}
            txData["txid"]  = tx["Hash"]
            txData["from"] = tx["From"]
            txData["to"] = tx["To"]
            txData["amount"] = "%.8f" % (float(tx["Amount"][0]["amount"]) / (10**8))
            txData["timestamp"] = timestamp


            retData.append(txData)
        return retData



    def post(self):
        rpcconn = USDPProxy(g_IP, g_PORT)
        try:
            nBlockNum = self.get_argument("blkNumber")
            data = USDP_GetTransactionFromBlock.getTransactionFromBlock(rpcconn, nBlockNum)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("USDP_GetTransactionFromBlock : error:{0} in {1}".format(e,get_linenumber()))


class USDP_GetAccountInfo(BaseHandler):
    @staticmethod
    def account_info(rpcconn, addr):
        data = rpcconn.getAccountInfo(addr)
        retData = {}
        retData["address"] = data["value"]["address"]
        retData["account_number"] = data["value"]["account_number"]
        retData["sequence"] = data["value"]["sequence"]
        retData["balance"] = data["value"]["coins"][0]["amount"] 
        return retData

    def post(self):
        rpcconn = USDPProxy(g_IP, g_PORT)
        try:
            addr = self.get_argument("address")
            if len(addr) != 43:
                self.write(json.dumps(BaseHandler.error_ret_with_data("arguments error")))
                return
            if addr[ : 5] != "usdp1":
                self.write(json.dumps(BaseHandler.error_ret_with_data("arguments error")))
                return
            data = USDP_GetAccountInfo.account_info(rpcconn, addr)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            if str(e) == "500":
                self.write(json.dumps(BaseHandler.error_ret_with_data("error: not found any info of the account. Due to the account DOT NOT have transactions yet. ")))
            else:
                self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("USDP_GetAccountInfo error:{0} in {1}".format(e,get_linenumber()))




#2019-05-11 yqq
#获取用户充币信息的接口, 直接从数据库中获取交易数据
class USDP_CrawlTxData(BaseHandler):

    def GetTxDataFromDB(self, nBegin, nEnd):

        #增加参数检查
        #print("nBegin , nEnd  type is not int.")
        #if not (isinstance(nBegin, int) and isinstance(nEnd, int)):
        if not (isinstance(nBegin, int) and (isinstance(nEnd, int) or isinstance(nEnd, long) )):
            print("nBegin is not int")
            return []

        
        txRet = []

        import sql
        strSql = """SELECT txdata FROM t_usdp_charge WHERE  height >= {0} and height <= {1} LIMIT 100;""".format(nBegin, nEnd)
        #strSql = """SELECT txdata FROM t_eth_charge WHERE  height >= {0} """.format(nBegin)  #
        #print(strSql)
        sqlRet = sql.run(strSql)
        #print(sqlRet)
        if not isinstance(sqlRet, list):
            return []
        for item in sqlRet:
            txListStr = item["txdata"]
            txList  = json.loads(txListStr)
            txRet.extend(txList)
        return txRet

    #@staticmethod
    def process(self, rpc_connection, nStart):
        txRet =  self.GetTxDataFromDB(nStart, (1<<64) - 1)  #TODO: 如果充币数据量太大, 需要限制每次返回的数量
        return txRet 


    def post(self):
        rpcconn = USDPProxy(g_IP, g_PORT)
        try:
            nStart  = int(self.get_argument("blknumber"))
            data = self.process(rpcconn, nStart)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("USDP_CrawlTxData error:{0} in {1}".format(e,get_linenumber()))

