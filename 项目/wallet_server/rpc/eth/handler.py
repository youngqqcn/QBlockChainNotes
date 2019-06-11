#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 14:30:38 2019
@author: junying
"""
import json

from base_handler import BaseHandler
from utils import decimal_default,str_to_decimal,get_linenumber
from .proxy import EthereumProxy
#from constants import ETH_IP_ADDR,ETH_RPC_PORT,ETH_DEFAULT_GAS_PRICE,ETH_BLK_BUFFER_SIZE
from constants import ETH_IP_ADDR,ETH_RPC_PORT,ETH_BLK_BUFFER_SIZE #,ETH_DEFAULT_GAS_PRICE,

ip_addr, port = ETH_IP_ADDR,ETH_RPC_PORT
#default_gas = 21000
#default_gasprice = ETH_DEFAULT_GAS_PRICE

            
class ETH_GetBalance(BaseHandler):
    @staticmethod
    def get_balance(rpc_connection,addr):
        balance = rpc_connection.eth_getBalance(addr)
        #return balance/float(10**18)
        return balance

    def post(self):
        rpc_connection = EthereumProxy(ip_addr, port)
        try:
            address = self.get_argument("address")
            if len(address) != 42:
                self.write(json.dumps(BaseHandler.error_ret_with_data("arguments error")))
                return
            balance = ETH_GetBalance.get_balance(rpc_connection,address)
            self.write(json.dumps(BaseHandler.success_ret_with_data(str(balance)), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("ETH_GetBalance error:{0} in {1}".format(e,get_linenumber()))
           


#class ETH_GasPrice(BaseHandler):
#    def get(self):
#        rpc_connection = EthereumProxy(ip_addr, port)
#        try:
#            data = rpc_connection.eth_gasPrice()
#            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
#        except Exception as e:
#            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
#            print("ETH_GasPrice error:{0} in {1}".format(e,get_linenumber()))
            
class ETH_PendingTransactions(BaseHandler):
    def get(self):
        rpc_connection = EthereumProxy(ip_addr, port)
        try:
            data = rpc_connection.eth_pendingTransactions()
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("ETH_PendingTransactions error:{0} in {1}".format(e,get_linenumber()))


class ETH_SendRawTransaction(BaseHandler):
    def post(self):
        rpc_connection = EthereumProxy(ip_addr, port)
        try:
            data = str(self.get_argument("data"))
            # 0x checking
            rlpdata = "0x" + data if "0x" not in data else data
            # sending raw transaction
            rsp = rpc_connection.eth_sendRawTransaction(rlpdata)
            self.write(json.dumps(BaseHandler.success_ret_with_data(rsp), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("ETH_SendRawTransaction error:{0} in {1}".format(e,get_linenumber()))

class ETH_ListAccounts(BaseHandler):
    @staticmethod
    def addresses():
        from sql import run
        accounts = run('select address from t_eth_accounts')
        return [account['address'].strip() for account in accounts]

    def get(self):
        rpc_connection = EthereumProxy(ip_addr, port)
        try:
            data = ETH_ListAccounts.addresses()
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("ETH_Accounts error:{0} in {1}".format(e,get_linenumber()))
            
class ETH_BlockNumber(BaseHandler):
    @staticmethod
    def latest(rpc_connection):
        lastestBlockNum = int(rpc_connection.eth_blockNumber())
        return lastestBlockNum

    def get(self):
        rpc_connection = EthereumProxy(ip_addr, port)
        try:
            data = ETH_BlockNumber.latest(rpc_connection)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("ETH_BlockNumber error:{0} in {1}".format(e,get_linenumber()))

class ETH_GetBlockTransactionCount(BaseHandler):
    @staticmethod
    def fromGetBlock(rpc_connection,blknumber):
        blkheader = rpc_connection.eth_getBlockByNumber(blknumber)
        return len(blkheader['transactions']) if blkheader else 0

    @staticmethod
    def process(rpc_connection,blknumber):
        blknumber = rpc_connection.eth_getBlockTransactionCountByNumber(blknumber)
        return int(blknumber) if blknumber else 0

    def get(self):
        rpc_connection = EthereumProxy(ip_addr, port)
        try:
            blknumber = int(self.get_argument("blknumber")) if self.get_argument("blknumber") else int(ETH_BlockNumber.latest(rpc_connection))
            data =  ETH_GetBlockTransactionCount.fromGetBlock(rpc_connection,blknumber)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("ETH_GetBlockTransactionCount error:{0} in {1}".format(e,get_linenumber()))

class ETH_GetTransactionFromBlock(BaseHandler):
    @staticmethod
    def process(rpc_connection,blknumber,txindex):
        txdata =  rpc_connection.eth_getTransactionByBlockNumberAndIndex(blknumber,txindex)
        blockData  = rpc_connection.eth_getBlockByNumber(blknumber)
        txdata["blocktime"] = blockData["timestamp"] if blockData and "timestamp" in blockData else 0
        txdata["confirmations"] =  ETH_BlockNumber.latest(rpc_connection) - blknumber
        txdata["blockNumber"] = blknumber
        from utils import filtered,alterkeyname
        retData = filtered(alterkeyname(txdata,'hash','txid'),["confirmations", "blocktime", "blockNumber","nonce","txid","from","to","value","gas","gasPrice"]) if txdata else False
        import decimal
        from decimal import Decimal
        decimal.getcontext().prec = 50
        for key in ["nonce", "gas", "value", "gasPrice", "blocktime"]:
            if "0x" in retData[key]: retData[key] = str(int(retData[key], 16))

            #only convert "value" to ether, DO NOT convert "gas" "gasprice" to ether!!!!  by yqq 2019-04-29
            if key in ["value"]: retData[key] = "%.8f" % (float(retData[key]) / (10**18 )) #set precision for 8. adapt exchange configurations , 2019-04-29 by yqq
            #if key in ["gas", "value", "gasPrice"]: retData[key] = str ((decimal.Decimal(retData[key]) / decimal.Decimal(10**18)).quantize(Decimal('0.000000000000000000')))
        return retData

    def get(self):
        rpc_connection = EthereumProxy(ip_addr, port)
        try:
            blknumber = int(self.get_argument("blknumber")) if self.get_argument("blknumber") else int(ETH_BlockNumber.latest(rpc_connection))
            txindex = int(self.get_argument("txindex")) if self.get_argument("txindex") else 0
            ret = ETH_GetTransactionFromBlock.process(rpc_connection,blknumber,txindex)
            if not ret:
                self.write(json.dumps(BaseHandler.error_ret_with_data("no corresponding transaction or block body not found!!!")))
                return
            self.write(json.dumps(BaseHandler.success_ret_with_data(ret), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("ETH_GetTransactionFromBlock error:{0} in {1}".format(e,get_linenumber()))


class ETH_GetBlockTransactions(BaseHandler):
    @staticmethod
    def process(rpc_connection,blknumber,txcount):
        txlist = []
        for index in range(txcount):
            txdata = ETH_GetTransactionFromBlock.process(rpc_connection,blknumber,index)
            if not txdata:
                break
            if any(txdata[address] in ETH_ListAccounts.addresses() for address in ['to','from']):
                txlist.append(txdata)
        return txlist

    def post(self):
        rpc_connection = EthereumProxy(ip_addr, port)
        try:
            blknumber = int(self.get_argument("blknumber")) if self.get_argument("blknumber") else ETH_BlockNumber.latest(rpc_connection)
            txcount = ETH_GetBlockTransactionCount.fromGetBlock(rpc_connection,blknumber)
            data = ETH_GetBlockTransactions.process(rpc_connection,blknumber,txcount)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("ETH_GetBlockTransactions error:{0} in {1}".format(e,get_linenumber()))



#2019-05-01 yqq
#获取用户充币信息的接口, 直接从数据库中获取交易数据
#不再临时扫描区块
class ETH_CrawlTxData(BaseHandler):

    def GetTxDataFromDB(self, nBegin, nEnd):
        if not (isinstance(nBegin, int) and (isinstance(nEnd, int) or isinstance(nEnd, long) )):
            #print(type(nBegin))
            #print(type(nEnd))
            print("nBegin or nEnd is not int type.")
            return []
        
        txRet = []

        import sql
        strSql = """SELECT txdata FROM t_eth_charge WHERE  height >= {0} and height <= {1} LIMIT 100;""".format(nBegin, nEnd)
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
        txRet =  self.GetTxDataFromDB(nStart, (1<<64) - 1)
        return txRet 


    def post(self):
        rpc_connection = EthereumProxy(ip_addr, port)
        try:
            nStart  = int(self.get_argument("blknumber"))
            data = self.process(rpc_connection, nStart)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("ETH_CrawlTxData error:{0} in {1}".format(e,get_linenumber()))


class ETH_GetTransactionCount(BaseHandler):
    def post(self):
        rpc_connection = EthereumProxy(ip_addr, port)
        try:
            address = self.get_argument("address")
            nonce = rpc_connection.eth_getTransactionCount(address)
            self.write(json.dumps(BaseHandler.success_ret_with_data(str(nonce)), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("ETH_GetTransactionCount error:{0} in {1}".format(e,get_linenumber()))

class ETH_GetBlockByNumber(BaseHandler):
    def get(self):
        rpc_connection = EthereumProxy(ip_addr, port)
        try:
            block_number = str(self.get_argument("number"))
            block_number = int(block_number,16) if '0x' in block_number else int(block_number)
            tx_infos = rpc_connection.eth_getBlockByNumber(block_number)
            self.write(json.dumps(BaseHandler.success_ret_with_data(tx_infos), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("ETH_GetBlockByNumber Error:{0} in {1}".format(e,get_linenumber()))

class ETH_GetTransactionByHash(BaseHandler):
    def post(self):
        rpc_connection = EthereumProxy(ip_addr, port)
        try:
            tx_hash = self.get_argument("tx_hash")#?????not ready
            tx_info = rpc_connection.eth_getTransactionByHash(tx_hash)
            self.write(json.dumps(BaseHandler.success_ret_with_data(tx_info), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("ETH_GetTransactionByHash error:{0} in {1}".format(e,get_linenumber()))
