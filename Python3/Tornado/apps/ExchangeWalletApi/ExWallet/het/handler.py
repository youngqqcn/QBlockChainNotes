#coding:utf8

"""
author: yqq
date: 2019-05-11 20:26
descriptions: USDP处理
"""
import logging
import json

from base_handler import BaseHandler
from utils import decimal_default,get_linenumber
from .proxy import USDPProxy
from constants import HET_IP_ADDR, HET_RPC_PORT
import sql
import decimal
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 30
from utils import  RoundDown

g_IP, g_PORT = HET_IP_ADDR, HET_RPC_PORT

            
class USDP_GetBalance(BaseHandler):
    @staticmethod
    def get_balance(rpcconn, addr):
        balance = rpcconn.getBalance(addr)
        return balance

    def post(self):
        rpcconn = USDPProxy(g_IP, g_PORT)
        try:
            address = self.get_argument("address")
            if len(address) != 41:
                self.write(json.dumps(BaseHandler.error_ret_with_data("arguments error")))
                return
            balance = USDP_GetBalance.get_balance(rpcconn, address)
            self.write(json.dumps(BaseHandler.success_ret_with_data(str(balance)), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("USDP_GetBalance error:{0} in {1}".format(e,get_linenumber()))

    def get(self):
        self.post()




#1.交易数据完全相同的两笔交易同时广播, 第一笔成功, 第二笔广播失败, HTTP-500 , 
#    {"error":"broadcast_tx_sync: Response error: RPC error -32603 - Internal error: Tx already exists in cache"}
#
#2.交易from, to, amount, sequence相同,  memo不同 的两笔交易同时广播,  第一笔广播成功, 第二笔失败, HTTP200
#  {"height":"0","txhash":"DFBCB4155DEBAD0DDFA61FA648BC065B1B70267126309D514B43C5DD22301EDD",
#   "code":4,"raw_log":"{\"codespace\":\"sdk\",\"code\":4,
#   \"message\":\"signature verification failed; verify correct account sequence and chain-id\"}"}
#
#3.如果转账金额与账户余额一样, 同样广播成功, 但是是无效交易
#    {"height":"0","txhash":"C2915385AE548F3F5680C12D3679D6C2BFA7A5C04FEAA2DBB2BDD12C40293EC5"}
#
#4.广播带上 orderId 防止交易重发
#    如果上一笔广播失败,想要重新发起一笔新的交易,是否直接返回数据库存的txid? 
#
#5.如果通过 /transaction/txid  这个接口查询交易, 如果txid不存在会返回 HTTP500
#
#6.如果sequence不对, 广播失败 , HTTP500
#{"height":"0","txhash":"150AAD45FF1637EE52A07A0961DBD6FC8F1A71017E458E743C27F6865DDC86F9",
# "code":4,"raw_log":"{\"codespace\":\"sdk\",\"code\":4,\"message\":\"signature verification failed; 
# verify correct account sequence and chain-id\"}"}
#
#7./transaction/txid 接口返回的是上链的交易数据[成功, 失败(金额不足) ]
#
#8.关于哪些交易能上链
#     8.0  完全正确的交易数据 (能成功的交易)
#     8.1  from, to,  fee , sequence, signature 都正确   amount不足 
#           例如: 406e9608bca45d67847a9e3f237f36818346daefc93ba0f300ed6b1b6ae8795c
#     

class USDP_SendRawTransaction(BaseHandler):
    def post(self):
        rpcconn = USDPProxy(g_IP, g_PORT)
        try:
            rawtx = str(self.get_argument("tx"))
            orderId = str(self.get_argument("orderId") )
            if len(rawtx) < 40 :
                self.write(json.dumps(BaseHandler.error_ret_with_data("arguments error: invalid `tx`")))
                return
            
            if not orderId.isdigit() or len(orderId) < 5:
                self.write(json.dumps(BaseHandler.error_ret_with_data("arguments error: invalid `orderId`")))
                return


            bFlag = False  #是否广播的标志

            import sql 
            sqlRet = sql.run("select * from t_het_broadcast where orderId='{0}';".format(orderId))
            retData = {}
            retData["orderId"] = orderId
            #如果此笔订单已经存在,调用 /transaction/txid  这个接口查询交易是否成功,若成功直接返回txid,若失败重新广播?
            if len(sqlRet) == 0:
                bFlag = True  #新的订单
            if len(sqlRet) > 0: 
                retData["txid"] = sqlRet[0]["txid"] 
                retData["sure"] = True if 1 == sqlRet[0]["sure"] else False
                # print("------------------")
                # print(sqlRet)
                #print(retData)
                # print("------------------")
                if not retData['sure']:
                    # print("is false")
                    nTry = 20
                    import time
                    for i in range(nTry):
                        time.sleep(1)
                        try:
                            bSuccess, strMsg = rpcconn.getTxValidInfo(retData['txid'])
                            if not bSuccess:
                                #100%确定 此前的交易已经失败, 则需要重新广播此笔交易
                                sql.run("delete from t_het_broadcast where orderId='{0}';".format(retData['orderId']))
                                bFlag =True #需要重新广播新发来的交易
                                return
                            retData["sure"] = True  #100%确定成功的
                            #print("udpate..")
                            sql.run("update t_het_broadcast set sure=1 where orderId='{0}';".format(retData['orderId']))
                            break
                        except Exception as e:
                            #20s 后依然在链上获取不到交易信息, 可能是链挂了?
                            logging.error(e)
                            if  i ==  nTry - 1:  retData["sure"] = False #不确定的
                            continue
   
            if bFlag :
                rsp = rpcconn.sendRawTransaction(rawtx)
                if "code" in rsp and "raw_log" in rsp:  #HTTP200 sequence不对
                    strErrMsg =  json.dumps(rsp['raw_log'])
                    self.write(json.dumps(BaseHandler.success_ret_with_data(strErrMsg), default=decimal_default))        
                    return
                retData["txid"] = rsp["txhash"]

                nTry = 20
                import time
                for i in range(nTry):
                    time.sleep(1)
                    try:
                        bSuccess, strMsg = rpcconn.getTxValidInfo(retData['txid'])
                        if not bSuccess:
                            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%strMsg)))
                            return
                        retData["sure"] = True  #100%确定成功的
                        break
                    except Exception as e:
                        #20s 后依然在链上获取不到交易信息, 可能是链挂了?
                        if  i ==  nTry - 1:  retData["sure"] = False #不确定的
                        continue
                sql.run("insert into t_het_broadcast(orderId,txid,sure) values('{0}','{1}', {2})".format(orderId, rsp["txhash"], 1 if retData['sure'] else 0 ))

            self.write(json.dumps(BaseHandler.success_ret_with_data(retData), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("USDP_SendRawTransaction error:{0} in {1}".format(e,get_linenumber()))

class USDP_ListAccounts(BaseHandler):
    @staticmethod
    def addresses():
        from sql import run
        accounts = run('select address from t_het_accounts')
        return [account['address'].strip() for account in accounts]

    def get(self):
        rpcconn = USDPProxy(g_IP, g_PORT)
        try:
            data = USDP_ListAccounts.addresses()
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("USDP_ListAccounts error:{0} in {1}".format(e,get_linenumber()))

            
class USDP_GetLatestBlockNumber(BaseHandler):
    @staticmethod
    def latest(rpcconn):
        lastestBlockNum = int(rpcconn.getLastestBlockNumber())
        return lastestBlockNum

    def get(self):
        pass

class USDP_IsValidTx(BaseHandler):

    @staticmethod
    def isValidTx(rpccon, strTxid):
        return rpccon.isValidTx(strTxid)

    def post(self):
        rpcconn = USDPProxy(g_IP, g_PORT)
        try:
            strTxid = str(self.get_argument("txid")).strip()
            if len(strTxid) != 64:
                self.write(json.dumps(BaseHandler.error_ret_with_data("txid is invalid.")))
                return
            bValid = USDP_IsValidTx.isValidTx(rpcconn, strTxid)
            self.write(json.dumps(BaseHandler.success_ret_with_data(bValid), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            pass




class USDP_GetTransactionFromBlock(BaseHandler):
    

    @staticmethod
    def getTransactionFromBlock(rpcconn, nBlockNum):
        data = rpcconn.getBlockByBlockNum(nBlockNum)
        import time
        timeStr = data["block_meta"]["header"]["time"]
        timeStr = timeStr[ : timeStr.rfind('.') ]
        ta = time.strptime(timeStr, "%Y-%m-%dT%H:%M:%S")
        timestamp = int(time.mktime(ta))
        # print("timestamp", timestamp)


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
            logging.error("USDP_GetTransactionFromBlock : error:{0} in {1}".format(e,get_linenumber()))


class USDP_GetAccountInfo(BaseHandler):
    @staticmethod
    def account_info(rpcconn, addr):
        data = rpcconn.getAccountInfo(addr)
        if not data["value"]["coins"]: return None  #一毛钱都不剩, coins字段为 null 转为Python对象后是None
        logging.info("data is : {}" .format( data))
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
            if len(addr) != 41:
                self.write(json.dumps(BaseHandler.error_ret_with_data("arguments error")))
                return
            if addr[ : 3] != "0x1":
                self.write(json.dumps(BaseHandler.error_ret_with_data("arguments error")))
                return
            data = USDP_GetAccountInfo.account_info(rpcconn, addr)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            if str(e) == "500":
                self.write(json.dumps(BaseHandler.error_ret_with_data("error: not found any info of the account. Due to the account DOT NOT have transactions yet. ")))
            else:
                self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("USDP_GetAccountInfo error:{0} in {1}".format(e,get_linenumber()))




#2019-05-11 yqq
#获取用户充币信息的接口, 直接从数据库中获取交易数据
class USDP_CrawlTxData(BaseHandler):

    def GetTxDataFromDB(self, nBegin, nEnd):
        txRet = []

        import sql
        strSql = """SELECT txdata FROM t_het_charge WHERE  height >= {0} and height <= {1} LIMIT 500;""".format(nBegin, nEnd)
        sqlRet = sql.run(strSql)

        if not isinstance(sqlRet, list):
            return []
        for item in sqlRet:
            txListStr = item["txdata"]
            txList  = json.loads(txListStr)
            txRet.extend(txList)
        return txRet

    #@staticmethod
    def process(self, rpc_connection, nStart):
        txRet =  self.GetTxDataFromDB(nStart - 3000, (1<<64) - 1)  #TODO: 如果充币数据量太大, 需要限制每次返回的数量
        return txRet 


    def post(self):
        rpcconn = USDPProxy(g_IP, g_PORT)
        try:
            nStart  = int(self.get_argument("blknumber")) #防止sql注入
            data = self.process(rpcconn, nStart)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("USDP_CrawlTxData error:{0} in {1}".format(e,get_linenumber()))


#归集查询接口
class USDP_CollectionQuery(BaseHandler):

    def proccess(self, rpcconn):

        #1.从t_usdp_active_addr获取所有的地址 
        strSql = """SELECT address FROM t_het_active_addrs WHERE `balance` > 0.001 ORDER BY `balance` DESC LIMIT 100;""";
        sqlRet = sql.run(strSql)
        addrs = []
        for item in sqlRet:
            if "address" in item: 
                addrs.append(item["address"])

        #2.实时获取所有地址的账户信息( addr, balance, account_no, sequence )
        retData = []
        for strAddr in addrs: 
            retInfo = USDP_GetAccountInfo.account_info(rpcconn, strAddr)  
            if not retInfo : #如果账户一毛钱不剩, 返回None
                strSql = """DELETE FROM t_het_active_addrs WHERE address='{0}';""".format(strAddr)
                logging.info("sql: {}".format(strSql))
                sqlRet = sql.run(strSql)
                continue

            #防止HET 归集数量太大, 导致归集失败
            if Decimal(retInfo['balance']) > Decimal('100000000.0'):
                retInfo['balance'] = '%.8f' % RoundDown( Decimal(retInfo['balance']) - Decimal('0.5432') )
            retData.append( retInfo )


        #对返回数据进行排序

        sortedRet = sorted(retData, key=lambda keys: Decimal(keys['balance']), reverse=True)

        #3.返回数据
        return sortedRet


    def get(self):
        rpcconn = USDPProxy(g_IP, g_PORT)
        try:
            retData = self.proccess(rpcconn)
            self.write(json.dumps(BaseHandler.success_ret_with_data(retData), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error(" USDP_CollectionQuery error:{0} in {1}".format(e,get_linenumber()))
            

















