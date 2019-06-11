#coding:utf8
"""
Created on Thu Mar 15 14:30:38 2019
@author: junying
"""

import json
from utils import decimal_default,get_linenumber
from base_handler import BaseHandler
from .proxy import AuthServiceProxy
from constants import BTC_RPC_URL

class BTC_GetAccount(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-junying-20180325
        try:
            commands = [["getaccount",self.get_argument("address")]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetAccount error:{0} in {1}".format(e,get_linenumber()))

class BTC_GetAccountAddress(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-junying-20180325
        try:
            commands = [["getaccountaddress",self.get_argument("account")]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetAccoutAddress error:{0} in {1}".format(e,get_linenumber()))
            
class BTC_GetAccountBalance(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-junying-20180325
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
            print("BTC_GetAccountBalance error:{0} in {1}".format(e,get_linenumber()))

          
#class BTC_ListAccounts(BaseHandler):    
#    def get(self):
#        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-junying-20180325
#        data = None
#        try:
#            minconf = int(self.get_argument("minconf")) if not self.get_argument("minconf") == "" else 0
#            commands = [["listaccounts",minconf]]
#            data = btc_rpc_connection.batch_(commands)
#            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
#        except Exception as e:
#            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
#            print("BTC_ListAccounts error:{0} in {1}".format(e,get_linenumber()))

          
####################################################################################################################
# Cold Wallet ######################################################################################################
####################################################################################################################

from utils import encode,decode,calcFee

class BTC_GetBalance(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-junying-20180325
        try:
            addr = self.get_argument("address")
            data = BTC_ListUTXO.utxo(btc_rpc_connection,addr)
            if not data: 
                self.write(json.dumps(BaseHandler.error_ret_with_data("0")))
                return
            from utils import accumulate
            self.write(json.dumps(BaseHandler.success_ret_with_data(accumulate(data)), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetBalance error:{0} in {1}".format(e,get_linenumber()))

class BTC_ListUTXO(BaseHandler):
    @staticmethod
    def utxo(rpcconn, addr, minconf=0, maxconf=9999999):
        commands = [["listunspent", minconf, maxconf, [addr], True]]
        #print("commands:  "),
        #print(commands)
        return rpcconn.batch_(commands)[0]

    def post(self):

        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)# todo-junying-20180325
        data = None
        try:
            minconf = int(self.get_argument("minconf")) if not self.get_argument("minconf") == "" else 0
            maxconf = int(self.get_argument("maxconf")) if not self.get_argument("maxconf") == "" else 9999999
            addr = self.get_argument("address")
            data = BTC_ListUTXO.utxo(btc_rpc_connection,addr,minconf,maxconf)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetUTXO error:{0} in {1}".format(e,get_linenumber()))

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# 1 to 1 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 8                     #use decimal and set precision to solve  'invalid amount' error

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
            for utxo in [item for item in utxos if int(item["confirmations"]) >= 0 and float(item["amount"]) > 0.00001  ]:
                if nSum> Decimal(str(amount)): break
                selected.append(utxo)
                nSum += Decimal(str((utxo["amount"])))
            return selected, nSum

        selected, nSum = UtxoFilter(utxos, amount)
        # check if enough
        from utils import calcFee

        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        fee = calcFee(len(selected))
        if nSum < fee + amount:
            return False,"budget not enough"
            #return False,0   #需测试!!!
        # make augmentations
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
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-junying-20190310
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
            print("BTC_CreatRawTransaction error:{0} in {1}".format(e,get_linenumber()))

class BTC_SendRawTransaction(BaseHandler):
    def post(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-junying-20190310
        try:
            rawdata = self.get_argument("rawdata") 
            if not rawdata: return
            commands = [["sendrawtransaction",rawdata]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_SendRawTransaction error:{0} in {1}".format(e,get_linenumber()))

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# N to N @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 8    

class BTC_CreateRawTransactionEx(BaseHandler):
    @staticmethod
    def genearateInParam(rpcconn,src,dest):
        utxos,gross,amount = [],Decimal('0'),sum(dest.values())
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
            from utils import calcFee
            redundant = gross - calcFee(len(utxos),len(dest.keys())+1) - amount
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
    def process(rpcconn,src,dest):
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

    def get_argument_ex(self,str):
        from utils import json2dict
        str2dict = json2dict(self.request.body)
        return str2dict[str] if str in str2dict.keys() else False
    
    def post(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-junying-20190310
        try:
            src = self.get_argument_ex("src") 
            dest = self.get_argument_ex("dest") 
            ret, rsp = BTC_CreateRawTransactionEx.process(btc_rpc_connection,src,dest)
            if not ret: self.write(json.dumps(BaseHandler.error_ret_with_data(rsp))); return 
            self.write(json.dumps(BaseHandler.success_ret_with_data(rsp), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_CreateRawTransactionEx error:{0} in {1}".format(e,get_linenumber()))


class BTC_ListAccounts(BaseHandler):
    @staticmethod
    def addresses():
        from sql import run
        accounts = run('select * from t_btc_address')  #TODO:后期数据量大的时候, 使用redis进行缓存地址
        return [account['address'] for account in accounts]

    def get(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)
        try:
            data = BTC_ListAccounts.addresses()
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_ListAccounts error:{0} in {1}".format(e,get_linenumber()))



g_exUserAddrs = BTC_ListAccounts.addresses() #使用全局变量保存交易所用户BTC地址 2019-06-01
class BTC_ListTransActions(BaseHandler):
    @staticmethod
    def blktimes(rpc_connection,account="*",tx_counts=10):
        commands = [["listtransactions",account,tx_counts]]
        data = rpc_connection.batch_(commands)
        if len(data) == 0: return []
        return [item['blocktime'] for item in data[0] if "blocktime" in item][::-1]  #fix bug:only return those txs  which be  writen into blockchain   @yqq 2019-03-21 

    @staticmethod
    def process(rpc_connection,account="*",tx_counts=10,skips=0,include_watchonly=True): #add 'include_watchonly' to include those address's transactions which not import private key into the wallet. #yqq 2019-03-26
        commands = [["listtransactions",account,tx_counts,skips, include_watchonly]]
        data = rpc_connection.batch_(commands)
        if len(data) == 0: return []
        txs = [item for item in data[0] if "blocktime" in item and item["category"] == "receive"] #fix bug:only return those txs  which be writen into blockchain   @yqq 2019-03-21
        from utils import filtered
        return [filtered(item,["address","category","amount","confirmations","txid","blocktime"]) for item in txs][::-1]

    def get(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-junying-20190315
        try:
            account = self.get_argument("account") if self.get_argument("account") else "*"
            tx_counts = int(self.get_argument("count")) if self.get_argument("count") else 10
            skips = int(self.get_argument("skips")) if self.get_argument("skips") else 0
            data = BTC_ListTransActions.process(btc_rpc_connection,account,tx_counts,skips)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_ListTransActions error:{0} in {1}".format(e,get_linenumber()))

class BTC_CrawlTxData(BaseHandler):
    @staticmethod
    def process(rpc_connection, nblktime):

        #exUserAddrs = BTC_ListAccounts.addresses()
        #print(exUserAddrs)
        if len(g_exUserAddrs) == 0:
            return []
        txs = BTC_ListTransActions.process(rpc_connection, '*', 100000000)
        retTxs = []
        for tx in txs:
            #if int(tx['blocktime'] >= nblktime) and tx["address"].strip() in exUserAddrs:
            if int(tx['blocktime'] >= nblktime) and tx["address"].strip() in g_exUserAddrs:
                retTxs.append(tx)
        return retTxs

    def post(self):
        rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-junying-20190316
        try:
            lastscannedblktime = int(str(self.get_argument("blocktime")))
            data = BTC_CrawlTxData.process(rpc_connection,lastscannedblktime)
            for i in range(len(data)): 
                data[i]["amount"] = str(data[i]["amount"])  #convert to str to avoid bug
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_CrawlTxData error:{0} in {1}".format(e,get_linenumber()))

####################################################################################################################
# Block Monitoring #################################################################################################
####################################################################################################################

class BTC_GetBlockCount(BaseHandler):
    @staticmethod
    def process(rpcconn):
        commands = [["getblockcount"]]
        return int(rpcconn.batch_(commands))

    def get(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-junying-20190310
        try:
            blknumber = BTC_GetBlockCount.process(btc_rpc_connection)
            self.write(json.dumps(BaseHandler.success_ret_with_data(blknumber), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetBlockCount error:{0} in {1}".format(e,get_linenumber()))

class BTC_GetBlockHash(BaseHandler):
    @staticmethod
    def process(rpcconn,blknumber):
        commands = [["getblockhash",blknumber]]
        return rpcconn.batch_(commands)

    def get(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-junying-20190310
        try:
            blknumber = self.get_argument("blknumber") if self.get_argument("blknumber") else BTC_GetBlockCount.process(btc_rpc_connection)
            data = BTC_GetBlockHash.process(btc_rpc_connection,blknumber)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetBlockHash error:{0} in {1}".format(e,get_linenumber()))

class BTC_DecodeRawTransaction(BaseHandler):
    def post(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-junying-20180325
        try:
            commands = [["decoderawtransaction",self.get_argument("rawdata")]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetTransaction error:{0} in {1}".format(e,get_linenumber()))

class BTC_GetRawTransaction(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-junying-20180325
        try:
            commands = [["getrawtransaction",self.get_argument("txid"),True]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetTransaction error:{0} in {1}".format(e,get_linenumber()))

class BTC_GetBlock(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(BTC_RPC_URL)#todo-junying-20190310
        try:
            blkhash = self.get_argument("blkhash") if self.get_argument("blkhash") else BTC_GetBlockCount.process(btc_rpc_connection)
            commands = [["getblock"]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            print("BTC_GetBlockHash error:{0} in {1}".format(e,get_linenumber()))
