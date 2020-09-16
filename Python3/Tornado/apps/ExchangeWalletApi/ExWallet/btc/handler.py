#coding:utf8
#authors :  yqq

import logging
import json
from utils import decimal_default,get_linenumber
from base_handler import BaseHandler
from .proxy import AuthServiceProxy

import traceback

#设置精度 
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 8

from constants import BTC_RPC_URL as RPC_URL
STR_ADDRESS_TABLE = "t_btc_address"



class BTC_ListAccounts(BaseHandler):
    @staticmethod
    def addresses():
        from sql import run
        accounts = run("""select * from {};""".format(STR_ADDRESS_TABLE))  #TODO:后期数据量大的时候, 使用redis进行缓存地址
        return [account['address'] for account in accounts]


    def get(self):
        try:
            data = BTC_ListAccounts.addresses()
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("BTC_ListAccounts error:{0} in {1}".format(e,get_linenumber()))

g_exUserAddrs = BTC_ListAccounts.addresses() #使用全局变量保存交易所用户BTC地址 2019-06-01



class BTC_GetAccount(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(RPC_URL)
        try:
            commands = [["getaccount",self.get_argument("address")]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("BTC_GetAccount error:{0} in {1}".format(e,get_linenumber()))

class BTC_GetAccountAddress(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(RPC_URL)
        try:
            commands = [["getaccountaddress",self.get_argument("account")]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("BTC_GetAccoutAddress error:{0} in {1}".format(e,get_linenumber()))
            
class BTC_GetAccountBalance(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(RPC_URL)
        try:
            account = self.get_argument("account").decode("utf-8")
            if account is None or len(account) == 0:
                self.write(json.dumps(BaseHandler.error_ret()))
                return 
            commands = [["getbalance", account]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("BTC_GetAccountBalance error:{0} in {1}".format(e,get_linenumber()))


class BTC_GetBalance(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(RPC_URL)
        try:
            addr = self.get_argument("address")
            data = BTC_ListUTXO.utxo(btc_rpc_connection,addr)
            if not data: 
                self.write(json.dumps(BaseHandler.error_ret_with_data("0")))
                return
            from utils import accumulate
            self.write(json.dumps(BaseHandler.success_ret_with_data('%.8f' % accumulate(data)), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("BTC_GetBalance error:{0} in {1}".format(e,get_linenumber()))

class BTC_ListUTXO(BaseHandler):
    @staticmethod
    def utxo(rpcconn, addr, minconf=1, maxconf=9999999):
        commands = [["listunspent", minconf, maxconf, [addr], True]]
        return rpcconn.batch_(commands)[0]

    def post(self):

        btc_rpc_connection = AuthServiceProxy(RPC_URL)
        data = None
        try:
            minconf = int(self.get_argument("minconf")) if not self.get_argument("minconf") == "" else 1
            maxconf = int(self.get_argument("maxconf")) if not self.get_argument("maxconf") == "" else 9999999
            addr = self.get_argument("address")
            data = BTC_ListUTXO.utxo(btc_rpc_connection,addr,minconf,maxconf)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("BTC_GetUTXO error:{0} in {1}".format(e,get_linenumber()))




class BTC_EstimateSmartFee(BaseHandler):

    @staticmethod
    def process(rpcconn, nConfTarget=2, strEstimateMode='ECONOMICAL'):
        commands = [["estimatesmartfee", nConfTarget, strEstimateMode ]]
        data = rpcconn.batch_(commands)
        if len(data) > 0:
            return data[0]['feerate'] * 100000000 / 1000    # satoshi/Byte  即 in satoshis per byte
        return 20

    @staticmethod
    def calcFee(rpcconn, nIn=1, nOut = 2):
        from decimal import Decimal
        from decimal import getcontext
        getcontext().prec = 8

        rate = BTC_EstimateSmartFee.process(rpcconn)
        rate  = "%.8f" % (rate / Decimal(100000000.0))
        return Decimal(str((148 * nIn + 34 * nOut + 10))) * Decimal(rate)


    def get(self):
        try:
            rpcconn = AuthServiceProxy(RPC_URL)
            data = BTC_EstimateSmartFee.calcFee(rpcconn)
            data = '%.8f' % data
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("BTC_EstimateSmartFee error:{0} in {1}".format(e, get_linenumber()))

        pass

class BTC_CreateRawTransaction(BaseHandler):

    @staticmethod
    def process(rpcconn,from_addr,to_addr,amount):
        #utxos
        utxos = BTC_ListUTXO.utxo(rpcconn,from_addr)
        #print(utxos)

        def UtxoFilter(utxos, amount):
            selected = []
            from decimal import Decimal    
            nSum = Decimal('0')

            #最小输入utxo金额 :  148 * rate    其中rate是 1000字节 所需的btc数量
            nFee = Decimal('0.0')
            for utxo in [item for item in utxos if int(item["confirmations"]) >= 1 and float(item["amount"]) > 0.0003  ]:
                selected.append(utxo)
                nSum += Decimal(str((utxo["amount"])))
                if nSum > Decimal(str(amount)):
                    nFee = BTC_EstimateSmartFee.calcFee(rpcconn, len(selected), 2)
                    if nSum > nFee + amount:
                        break
            return selected, nSum, nFee

        selected, nSum , fee = UtxoFilter(utxos, amount)
        # check if enough
        # from utils import calcFee

        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        # fee =  BTC_EstimateSmartFee.calcFee(rpcconn, len(selected), 2)
        if nSum < fee + amount:
            return False,"budget not enough"
            #return False,0   #需测试!!!

        from utils import filtered
        param_in = [filtered(item,["txid","vout"]) for item in selected]
        param_out = {to_addr:amount, from_addr: nSum - amount - fee}
        #print("--------------param_out-------------")
        #print("fee" + str(fee))
        #print(param_in)
        #print(param_out)
        #print("--------------param_out-------------")
        # create raw transaction
        commands = [["createrawtransaction",param_in,param_out]]
        return True, {"hex":rpcconn.batch_(commands), "utxos":selected, "txout":param_out}

    def post(self):
        btc_rpc_connection = AuthServiceProxy(RPC_URL)
        try:
            from_addr = self.get_argument("from") 
            to_addr = self.get_argument("to") 
            #amount = float(self.get_argument("amount"))
            from decimal import Decimal
            amount = Decimal(str(self.get_argument("amount")))
            ret, rsp = BTC_CreateRawTransaction.process(btc_rpc_connection,from_addr,to_addr,amount)
            if not ret:
                self.write(json.dumps(BaseHandler.error_ret_with_data(rsp)))
                return 
            self.write(json.dumps(BaseHandler.success_ret_with_data(rsp), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("BTC_CreatRawTransaction error:{0} in {1}".format(e,get_linenumber()))

class BTC_SendRawTransaction(BaseHandler):
    def post(self):
        btc_rpc_connection = AuthServiceProxy(RPC_URL)
        try:
            rawdata = self.get_argument("rawdata") 
            if not rawdata: return
            commands = [["sendrawtransaction",rawdata]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("BTC_SendRawTransaction error:{0} in {1}".format(e,get_linenumber()))


class BTC_CreateRawTransactionEx(BaseHandler):
    @staticmethod
    def genearateInParam(rpcconn, src, dest):
        utxos,gross,amount = [],Decimal('0'),sum(dest.values())
        redundant = 0
        for addr in src:
            # utxos
            all = BTC_ListUTXO.utxo(rpcconn,addr)
            # recommend
            from utils import recommended
            selected,aggregate = recommended(all,amount)
            # process
            utxos += selected
            gross += aggregate
            # check if enough
            redundant = gross - BTC_EstimateSmartFee.calcFee(rpcconn, len(utxos), len(dest.keys())+1) - amount
            if redundant > 0:
                return True,utxos,redundant
        return False,utxos,redundant
    
    @staticmethod
    def generateOutParam(dest):
        param_out = {}
        for key,value in dest.items():
            param_out[key] = Decimal(value) if isinstance(value, str) else Decimal(str(value))
        return param_out
        
    @staticmethod
    def process(rpcconn, src, dest ):
        # preprocess
        param_out = BTC_CreateRawTransactionEx.generateOutParam(dest)
        ret,utxos,redundant = BTC_CreateRawTransactionEx.genearateInParam(rpcconn,src,param_out)
        if not ret: return False, "budget not enough"
        # param_out refinement
        param_out[src[0]] = redundant if src[0] not in param_out.keys() else param_out[src[0]] + redundant
        #print(param_out)
        # param_in refinement
        from utils import filtered
        param_in = [filtered(item,["txid","vout"]) for item in utxos]
        #print(param_in)
        return True, {"hex":rpcconn.batch_([["createrawtransaction",param_in,param_out]]),"utxos":utxos, "txout":param_out}

    def get_argument_ex(self, str):
        from utils import json2dict
        str2dict = json2dict(self.request.body)
        return str2dict[str] if str in str2dict.keys() else False
    
    def post(self):
        btc_rpc_connection = AuthServiceProxy(RPC_URL)
        try: 
            src = self.get_argument_ex("src") 
            dest = self.get_argument_ex("dest") 
            if not isinstance(src, list):
                self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % ("src must be json list"))))
                return
            if not isinstance(dest, dict):
                self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % ("dest must be json object"))))
                return
            
            ret, rsp = BTC_CreateRawTransactionEx.process(btc_rpc_connection, src, dest)
            if not ret: 
                self.write(json.dumps(BaseHandler.error_ret_with_data(rsp)))
                return 
            self.write(json.dumps(BaseHandler.success_ret_with_data(rsp), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("BTC_CreateRawTransactionEx error:{0} in {1}".format(e,get_linenumber()))




class BTC_CreateRawTransactionEx_Collection(BaseHandler):

    @staticmethod
    def makeParams( rpcconn, lstSrc, lstDest):

        if len(lstSrc) == 1 and lstSrc[0].strip() == "*":
            lstSrcAddrs = g_exUserAddrs
        else:
            lstSrcAddrs = lstSrc

        utxos, nSum = [], Decimal('0')
        txAmount, fTxFee = 0, 0
        #for addr in lstSrc:
        if isinstance(lstSrc, list):
            # bitcoin-cli -conf=/root/.bitcoin/bitcoin-test.conf listunspent 0 9999999 '[]' true '{ "minimumAmount": 0.005 }'
            commands = [["listunspent", 1, 99999999, [], True, {'minimumAmount':0.0003}]]
            lstUtxos = rpcconn.batch_(commands)[0]
            # print(len(lstUtxos))
            for utxo in lstUtxos:
                if utxo['address'].strip() in lstSrcAddrs:
                    utxos.append(utxo)
                    nSum += Decimal(str((utxo["amount"])))

            fTxFee = BTC_EstimateSmartFee.calcFee(rpcconn, len(utxos), len(lstDest))
            txAmount = nSum - fTxFee  #实际转账金额
            if txAmount <= 0.0003:  #实际转账金额太小 
                return False, None, 0, 0
        return True, utxos, txAmount , fTxFee
    
        
    @staticmethod
    def process(rpcconn, lstSrc, lstDest):

        #lstSrcAddrs = []
        bRet, utxos, txAmount, fTxFee = BTC_CreateRawTransactionEx_Collection.makeParams(rpcconn, lstSrc, lstDest)
        if not bRet: 
            return False, "collection amount is too small!"
        
        strDst = lstDest[0]
        vout = {strDst : txAmount}

        from utils import filtered
        vin = [filtered(item,["txid","vout"]) for item in utxos]

        strHex =  rpcconn.batch_([["createrawtransaction", vin, vout]]) 
          
        return True, {"hex": strHex, "utxos":utxos, "txout":vout, "txFee":fTxFee}

    def get_argument_ex(self, str):
        from utils import json2dict
        str2dict = json2dict(self.request.body)
        return str2dict[str] if str in str2dict.keys() else False
    
    def post(self):
        btc_rpc_connection = AuthServiceProxy(RPC_URL)
        try:
            src = self.get_argument_ex("src") 
            dest = self.get_argument_ex("dest") 
            if not isinstance(src, list):
                self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % ("src must be json list"))))
                return
            if not isinstance(dest, list):
                self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % ("dest must be json list"))))
                return
            ret, rsp = BTC_CreateRawTransactionEx_Collection.process(btc_rpc_connection, src, dest)
            if not ret: 
                self.write(json.dumps(BaseHandler.error_ret_with_data(rsp)))
                return 
            self.write(json.dumps(BaseHandler.success_ret_with_data(rsp), default=decimal_default))
        except Exception as e:
            # traceback.print_exc()
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("BTC_CreateRawTransactionEx error:{0} in {1}".format(e,get_linenumber()))

#查询需要归集的地址余额
class BTC_CollectionQuery(BaseHandler):

    def get(self):
        rpcconn = AuthServiceProxy(RPC_URL)

        try:
            commands = [["listunspent", 1, 99999999, [], True, {'minimumAmount':0.0003}]]
            lstUtxos = rpcconn.batch_(commands)[0]
            mapRet = {}
            for utxo in lstUtxos:
                strAddr = utxo['address'].strip() 
                if strAddr not in g_exUserAddrs : continue
                if strAddr not in mapRet:
                    mapRet[strAddr] = Decimal("0.0")
                nAmount = utxo['amount']
                mapRet[strAddr] = str( nAmount + Decimal( mapRet[strAddr]) )
            self.write(json.dumps(BaseHandler.success_ret_with_data(mapRet), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("BTC_CollectionQuery error:{0} in {1}".format(e, get_linenumber()))
            


class BTC_ListTransactions(BaseHandler):
    @staticmethod
    def blktimes(rpc_connection,account="*",tx_counts=10):
        commands = [["listtransactions",account,tx_counts]]
        data = rpc_connection.batch_(commands)
        if len(data) == 0: return []
        
        #fix bug:only return those txs  which be  writen into blockchain   @yqq 2019-03-21 
        return [item['blocktime'] for item in data[0] if "blocktime" in item][::-1]  

    #add 'include_watchonly' to include those address's transactions 
    # which not import private key into the wallet. #yqq 2019-03-26
    @staticmethod
    def process(rpc_connection,account="*",tx_counts=10,skips=0,include_watchonly=True): 
        commands = [["listtransactions",account,tx_counts,skips, include_watchonly]]
        data = rpc_connection.batch_(commands)
        if len(data) == 0: return []
        
        #fix bug:only return those txs  which be writen into blockchain   @yqq 2019-03-21
        txs = [item for item in data[0] if "blocktime" in item and item["category"] == "receive"] 
        from utils import filtered
        return [filtered(item,["address","category","amount","confirmations","txid","blocktime"]) for item in txs][::-1]

    def get(self):
        btc_rpc_connection = AuthServiceProxy(RPC_URL)
        try:
            account = self.get_argument("account") if self.get_argument("account") else "*"
            tx_counts = int(self.get_argument("count")) if self.get_argument("count") else 10
            skips = int(self.get_argument("skips")) if self.get_argument("skips") else 0
            data = BTC_ListTransactions.process(btc_rpc_connection,account,tx_counts,skips)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("BTC_ListTransActions error:{0} in {1}".format(e,get_linenumber()))

class BTC_CrawlTxData(BaseHandler):
    @staticmethod
    def process(rpc_connection, nblktime):
        if len(g_exUserAddrs) == 0:
            return []
        txs = BTC_ListTransactions.process(rpc_connection, '*', 100000000)
        retTxs = []
        for tx in txs:
            if int(str(tx['blocktime'])) >= nblktime and tx["address"].strip() in g_exUserAddrs:
                retTxs.append(tx)
        return retTxs

    def post(self):
        rpc_connection = AuthServiceProxy(RPC_URL)
        try:
            lastscannedblktime = int(str(self.get_argument("blocktime")))
            data = BTC_CrawlTxData.process(rpc_connection,lastscannedblktime)
            for i in range(len(data)): 
                data[i]["amount"] = str(data[i]["amount"])  #convert to str to avoid bug
            # logging.info("data : {}".format(data))
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            # print("BTC_CrawlTxData error:{0} in {1}".format(e,get_linenumber()))
            logging.error("BTC_CrawlTxData error:{0} in {1}".format(e,get_linenumber()))

class BTC_GetBlockCount(BaseHandler):
    @staticmethod
    def process(rpcconn):
        commands = [["getblockcount"]]
        return int(rpcconn.batch_(commands))

    def get(self):
        btc_rpc_connection = AuthServiceProxy(RPC_URL)
        try:
            blknumber = BTC_GetBlockCount.process(btc_rpc_connection)
            self.write(json.dumps(BaseHandler.success_ret_with_data(blknumber), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("BTC_GetBlockCount error:{0} in {1}".format(e,get_linenumber()))

class BTC_GetBlockHash(BaseHandler):
    @staticmethod
    def process(rpcconn,blknumber):
        commands = [["getblockhash",blknumber]]
        return rpcconn.batch_(commands)

    def get(self):
        btc_rpc_connection = AuthServiceProxy(RPC_URL)
        try:
            blknumber = self.get_argument("blknumber") if self.get_argument("blknumber") else BTC_GetBlockCount.process(btc_rpc_connection)
            data = BTC_GetBlockHash.process(btc_rpc_connection,blknumber)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("BTC_GetBlockHash error:{0} in {1}".format(e,get_linenumber()))

class BTC_DecodeRawTransaction(BaseHandler):
    def post(self):
        btc_rpc_connection = AuthServiceProxy(RPC_URL)
        try:
            commands = [["decoderawtransaction",self.get_argument("rawdata")]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("BTC_GetTransaction error:{0} in {1}".format(e,get_linenumber()))

class BTC_GetRawTransaction(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(RPC_URL)
        try:
            commands = [["getrawtransaction",self.get_argument("txid"),True]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("BTC_GetTransaction error:{0} in {1}".format(e,get_linenumber()))

class BTC_GetBlock(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(RPC_URL)
        try:
            blkhash = self.get_argument("blkhash") if self.get_argument("blkhash") else BTC_GetBlockCount.process(btc_rpc_connection)
            commands = [["getblock"]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("BTC_GetBlockHash error:{0} in {1}".format(e,get_linenumber()))
