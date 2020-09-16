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
from constants import HTDF_IP_ADDR, HTDF_RPC_PORT
import sql
from enum import Enum
from decimal import Decimal
from constants import URL_BLACK_LIST , USER_HASH , WHITE_LIST#黑名单  2019-10-15
import decimal
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 30
from utils import RoundDown
import traceback

g_IP, g_PORT = HTDF_IP_ADDR, HTDF_RPC_PORT

from constants import HRC20_CONTRACT_MAP


g_special_token_list = ['AJC', 'USDP', 'HET', 'BEI']

            
class USDP_GetBalance(BaseHandler):
    @staticmethod
    def get_balance(rpcconn, addr):
        balance = rpcconn.getBalance(addr)
        return balance


    @classmethod
    def get_all_balance(cls, rpcconn : USDPProxy, addr : str) -> dict:
        strhtdfbalance = USDP_GetBalance.get_balance(rpcconn, addr)
        strhtdfbalance = str( RoundDown( Decimal(strhtdfbalance) ) ) if Decimal(strhtdfbalance) > Decimal('0.00000001') else '0.00000000'
        retdata = {'HTDF' : strhtdfbalance}

        for contract_addr in HRC20_CONTRACT_MAP.keys() :
            strbalance =  rpcconn.getHRC20TokenBalance(contract_addr=contract_addr, address=addr)
            strsymbol = rpcconn.getHRC20_symbol(contract_addr=contract_addr)

            if strsymbol.upper() in g_special_token_list:
                strsymbol = 'HRC20-' + strsymbol
            retdata[strsymbol] = str(  strbalance )
        return retdata

    @classmethod
    def get_single_token_balance(cls, rpcconn: USDPProxy, addr: str, token_name: str) -> dict:
        """
        获取 HTDF和token余额,  而不是获取所有 token余额
        :param rpcconn:
        :param addr:
        :return:
        """
        strhtdfbalance = USDP_GetBalance.get_balance(rpcconn, addr)
        strhtdfbalance = str(RoundDown(Decimal(strhtdfbalance))) if Decimal(strhtdfbalance) > Decimal(
            '0.00000001') else '0.00000000'
        retdata = {'HTDF': strhtdfbalance}

        for contract_addr in HRC20_CONTRACT_MAP.keys():
            token_info = HRC20_CONTRACT_MAP[contract_addr]
            if token_info['symbol'] != token_name.upper():
                continue

            strbalance = rpcconn.getHRC20TokenBalance(contract_addr=contract_addr, address=addr)
            strsymbol = rpcconn.getHRC20_symbol(contract_addr=contract_addr)

            if strsymbol.upper() in g_special_token_list:
                strsymbol = 'HRC20-' + strsymbol
            retdata[strsymbol] = str(strbalance)
            break
        return retdata


    def post(self):
        try:
            address = self.get_argument("address")
            if len(address) != 43:
                self.write(json.dumps(BaseHandler.error_ret_with_data("arguments error")))
                return
            rpcconn = USDPProxy(g_IP, g_PORT)
            retdata = USDP_GetBalance.get_all_balance(rpcconn, address)
            self.write(json.dumps(BaseHandler.success_ret_with_data(retdata), default=decimal_default))
        except Exception as e:
            traceback.print_exc()
            self.write(json.dumps(BaseHandler.error_ret_with_data(f"error: {str(e)}")))
            logging.error("USDP_GetBalance error:{}".format(e))

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
            sqlRet = sql.run("select * from t_htdf_broadcast where orderId='{0}';".format(orderId))
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
                                sql.run("delete from t_htdf_broadcast where orderId='{0}';".format(retData['orderId']))
                                bFlag =True #需要重新广播新发来的交易
                                return
                            retData["sure"] = True  #100%确定成功的
                            #print("udpate..")
                            sql.run("update t_htdf_broadcast set sure=1 where orderId='{0}';".format(retData['orderId']))
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
                sql.run("insert into t_htdf_broadcast(orderId,txid,sure) values('{0}','{1}', {2})".format(orderId, rsp["txhash"], 1 if retData['sure'] else 0 ))

            self.write(json.dumps(BaseHandler.success_ret_with_data(retData), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("USDP_SendRawTransaction error:{0} in {1}".format(e,get_linenumber()))

class USDP_ListAccounts(BaseHandler):
    @staticmethod
    def addresses():
        from sql import run
        accounts = run('select address from t_htdf_accounts')
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
        logging.error("timestamp", timestamp)


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
            if len(addr) != 43:
                self.write(json.dumps(BaseHandler.error_ret_with_data("arguments error")))
                return
            if addr[ : 5] != "htdf1":
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






g_mapCachedBlackAddr = {}

import time
#2019-05-11 yqq
#获取用户充币信息的接口, 直接从数据库中获取交易数据
class USDP_CrawlTxData(BaseHandler):
    class CheckCode:
        is_black = "is_black"  # 是黑名单
        is_white = 'is_white'  # 是白名单
        unsure = "unsure"  # 不确定(黑名单监控接口请求不通)

    #黑名单检查
    @staticmethod
    def BlackListCheck(srcaddr):

        #如果源地址在本地白名单, 直接判断为白名单
        if srcaddr in WHITE_LIST:
            return USDP_CrawlTxData.CheckCode.is_white

        import requests
        headers = {'Content-Type' : 'application/json'}
        data = {
            'address' : str(srcaddr).strip(),
            'userhash' : str(USER_HASH).strip()
        }
        rsp = requests.post(url=URL_BLACK_LIST, headers=headers, data=json.dumps(data))
        flag = rsp.json()
        if rsp.status_code  != 200 or (not isinstance(flag, bool)):
            return USDP_CrawlTxData.CheckCode.unsure
        if isinstance(flag, bool) and flag == False:
            return USDP_CrawlTxData.CheckCode.is_white
        return USDP_CrawlTxData.CheckCode.is_black


    def GetTxDataFromDB(self, nBegin : int, nEnd : int,  symbol : str) -> list:
        txRet = []

        if symbol.upper() == 'HTDF':
            strSql = """SELECT txdata FROM t_htdf_charge WHERE  height >= {0} and height <= {1} LIMIT 500;""".format(
                nBegin, nEnd)
            sqlRet = sql.run(strSql)

            if not isinstance(sqlRet, list):
                return []
            for item in sqlRet:
                txListStr = item["txdata"]
                txList = json.loads(txListStr)
                txRet.extend(txList)

            # 如果没有  symbol字段则加上 symbol 字段
            for item in txRet:
                if 'symbol' not in item:
                    item['symbol'] = 'HTDF'

            return txRet

        else: # HRC20
            # TODO:  将 t_htdf_charge 和 tb_hrc20_deposit 表结构重构, 合并为一张表, 删除t_htdf_charge
            strsql = f"""select * from tb_hrc20_deposit WHERE `symbol`='{symbol}' and `block_number`>={nBegin} and `block_number`<={nEnd} LIMIT 1000;"""
            logging.info(strsql)
            sqlret = sql.run(strsql)


            if not isinstance(sqlret, list):
                return txRet

            for item in sqlret:
                tx = {}
                tx['symbol'] = item['symbol']
                tx["txid"] = item['txid']
                tx["from"] = item["from"]
                tx["to"] = item["to"]
                # tx["nonce"] = item['nonce']
                tx["blocktime"] = item['block_time']
                tx["confirmations"] = item['confirmations']
                tx["blockNumber"] = item['block_number']
                tx["value"] = item['value']

                if item['symbol'].upper() in g_special_token_list:
                    tx['symbol'] = 'HRC20-' + item['symbol'].upper()

                txRet.append(tx)

            return txRet

        pass






    #@staticmethod
    def process(self, nStart : int, symbol : str):
        start = nStart - 3000
        start = start if start >= 0 else 0
        txRet =  self.GetTxDataFromDB( start, (1<<64) - 1, symbol)  #TODO: 如果充币数据量太大, 需要限制每次返回的数量
        for i in range(len(txRet)):
            srcaddr = txRet[i]['from']

            #如果是之前没有缓存过, 则重新请求
            #如果之前请求失败, 则重新请求
            # if srcaddr not in g_mapCachedBlackAddr  \
            #         or g_mapCachedBlackAddr[srcaddr] == USDP_CrawlTxData.CheckCode.unsure:
            #     flag = USDP_CrawlTxData.BlackListCheck( srcaddr )
            #     g_mapCachedBlackAddr[srcaddr] = flag
            # txRet[i]['srcAddrFlag']  = g_mapCachedBlackAddr[srcaddr]

            txRet[i]['srcAddrFlag']  = 'is_white'


        return txRet


    def post(self):
        try:
            logging.info('URI: {}'.format(self.request.uri))
            strURI = self.request.uri
            symbol = str(strURI[strURI.find('/', 0) + 1:  strURI.rfind('/')])  # 类似:    /hrc20-ajc/crawltransactions
            symbol = symbol.upper().strip()
            symbol = symbol.replace('HRC20-', '')  #如果有 HRC20- 字样的 则去掉
            assert  len(symbol) < 20

            nStart  = int(self.get_argument("blknumber"))  #必须进行类型转换,  防止sql注入
            data = self.process(nStart, symbol=symbol)
            logging.info(data)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("USDP_CrawlTxData error:{0} in {1}".format(e,get_linenumber()))


#归集查询接口
class USDP_CollectionQuery(BaseHandler):

    def proccess(self, rpcconn):

        #1.从t_htdf_active_addr获取所有的地址
        strSql = f"""SELECT address FROM t_htdf_active_addrs WHERE `balance` > 0.001 ORDER BY `balance` DESC LIMIT 100;""";
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
                strSql = """DELETE FROM t_htdf_active_addrs WHERE address='{0}';""".format(strAddr)
                logging.info("sql: {}".format(strSql))
                sqlRet = sql.run(strSql)
                continue
            retData.append( retInfo )
        


        #对返回数据进行排序
        sortedRet = sorted(retData, key=lambda keys:Decimal(keys['balance']), reverse=True)

        #3.返回数据
        return sortedRet


    def proccess_HRC20(self, rpcconn, symbol):
        # 1.从t_hrc20_active_addr获取所有的地址
        strSql = f"""SELECT address FROM tb_hrc20_active_addrs WHERE `symbol`='{symbol}' and `balance` > 0.001 ORDER BY `balance` DESC LIMIT 50;""";
        sqlRet = sql.run(strSql)
        addrs = []
        for item in sqlRet:
            if "address" in item:
                addrs.append(item["address"])

        #2.获取每个地址的信息(  account_number, sequence, balances{htdf_balance, hrc20_token_balance }
        retdata = []
        for address in addrs:

            # balances = USDP_GetBalance.get_all_balance(rpcconn=rpcconn, addr=address)
            balances = USDP_GetBalance.get_single_token_balance(rpcconn=rpcconn, addr=address, token_name=symbol)

            assert  isinstance(balances, dict)


            token_symbol = symbol.upper() #if symbol.upper() != 'AJC' else  'HRC20-AJC'
            if symbol.upper() in g_special_token_list:
                token_symbol = 'HRC20-' + token_symbol

            if Decimal( balances[token_symbol] ) < 0.00001:
                logging.info( f" {address} balance of {symbol} is too small,  skipped . " )
                continue

            #如果一个账户尚未激活(即从未有过htdf交易) , 但有 HRC20 代币的余额
            if  Decimal( balances['HTDF'] ) < 0.21:
                acct_info = {
                    'address' : str(address).strip(),
                    'account_number' : '0',
                    'sequence' : '0',
                    'balances' : balances
                }
            else:
                htdf_acct_info = USDP_GetAccountInfo.account_info(rpcconn, address)
                if not htdf_acct_info:  # 如果账户一毛钱不剩, 返回None
                    pass

                acct_info = {
                    'address': htdf_acct_info['address'],
                    'account_number': htdf_acct_info['account_number'],
                    'sequence': htdf_acct_info['sequence'],
                    'balances': balances
                }


            retdata.append(acct_info)

        return  retdata


    def get(self):

        try:
            symbol = self.get_argument("symbol")
        except :
            logging.warning('no symbol arg, default is htdf')
            symbol = "htdf"
            pass

        rpcconn = USDPProxy(g_IP, g_PORT)
        try:
            token_full_name = symbol.upper()

            symbol = token_full_name.replace('HRC20-', '')
            if not symbol.isalpha() : #防止sql注入
                raise  Exception("invalid symbol, must token symbol")

            if symbol.upper() == 'HTDF':
                retData = self.proccess(rpcconn)
            elif symbol  in [ symb['symbol']  for symb in HRC20_CONTRACT_MAP.values() ]:
                retData = self.proccess_HRC20(rpcconn, symbol)
            else:
                raise Exception(f'invalid symbol `{symbol}`')
            self.write(json.dumps(BaseHandler.success_ret_with_data(retData), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error(" USDP_CollectionQuery error:{0} in {1}".format(e,get_linenumber()))
            

    def post(self):
        self.get()
















