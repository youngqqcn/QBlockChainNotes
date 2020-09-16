#coding:utf8
#2019-03
#authors :  yqq , junying
import logging

import json
from utils import decimal_default,get_linenumber
from base_handler import BaseHandler
from .proxy import AuthServiceProxy
from constants import OMNI_RPC_URL,OMNI_PROPERTY_ID,OMNI_TRANSACTION_FEE,OMNI_TRANSACTION_RECIPIENT_GAIN

# from utils import encode,decode,calcFee
from btc.handler import BTC_EstimateSmartFee
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 8    

class uBTC_GetAccountAddress(BaseHandler):
    @staticmethod
    def addresses():
        from sql import run
        accounts = run('select * from t_btc_address')  #TODO:后期数据量大的时候, 使用redis进行缓存地址
        return [account['address'] for account in accounts]

    def get(self):
        omni_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)
        try:
            commands = [["getaccountaddress",self.get_argument("account")]]
            data = omni_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("uBTC_GetAccountAddress error:{0} in {1}".format(e,get_linenumber()))

g_exUserAddrs = uBTC_GetAccountAddress.addresses() #使用全局变量保存交易所用户BTC地址 2019-06-01



class uBTC_ListAccounts(BaseHandler):    
    def get(self):
        btc_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)
        data = None
        try:
            minconf = int(self.get_argument("minconf")) if not self.get_argument("minconf") == "" else 1
            commands = [["listaccounts",minconf]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("uBTC_ListAccounts error:{0} in {1}".format(e,get_linenumber()))

class uBTC_ListUTXO(BaseHandler):

    @staticmethod
    def utxo(rpcconn, addr, minconf=0, maxconf=9999999):
        commands = [["listunspent", minconf, maxconf, [addr] ]]
        return rpcconn.batch_(commands)[0]

    def post(self):
        omni_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)
        try:
            minconf = int(self.get_argument("minconf")) #if not self.get_argument("minconf") == "" else 1
            maxconf = int(self.get_argument("maxconf")) #if not self.get_argument("maxconf") == "" else 9999999
            data = uBTC_ListUTXO.utxo(omni_rpc_connection,self.get_argument("address"),minconf,maxconf)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("uBTC_ListUTXO error:{0} in {1}".format(e,get_linenumber()))


class uBTC_GetBalance(BaseHandler):
    def get(self):
        omni_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)
        try:
            
            addr =  self.get_argument("address")
            #print("addr" + str(addr))
            data = uBTC_ListUTXO.utxo(omni_rpc_connection, self.get_argument("address"), 0, 99999 )
            if not data:
                self.write(json.dumps(BaseHandler.error_ret_with_data("utxo no available")))
                return
            from utils import accumulate
            self.write(json.dumps(BaseHandler.success_ret_with_data('%.8f' % accumulate(data)), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("uBTC_GetBalance error:{0} in {1}".format(e,get_linenumber()))

class uBTC_CreateRawTransaction(BaseHandler):
    def post(self):
        btc_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)
        try:
            from_addr = str(self.get_argument("from")) 
            to_addr = str(self.get_argument("to")) 
            amount = float(self.get_argument("amount"))
            from btc.handler import BTC_CreateRawTransaction
            ret, rsp = BTC_CreateRawTransaction.process(btc_rpc_connection,from_addr,to_addr,amount)
            if not ret:
                self.write(json.dumps(BaseHandler.error_ret_with_data(rsp)))
                return 
            self.write(json.dumps(BaseHandler.success_ret_with_data(rsp), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("uBTC_CreateRawTransaction error:{0} in {1}".format(e,get_linenumber()))

class uBTC_SendRawTransaction(BaseHandler):
    def post(self):
        btc_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)
        try:
            commands = [["sendrawtransaction",self.get_argument("rawdata")]]
            data = btc_rpc_connection.batch_(commands)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("uBTC_SendRawTransaction error:{0} in {1}".format(e,get_linenumber()))


class OMNI_GetBalance(BaseHandler):
    def get(self):
        omni_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)
        try:
            commands = [["omni_getbalance", self.get_argument("address"), OMNI_PROPERTY_ID]]
            data = omni_rpc_connection.batch_(commands)[0]['balance']  #直接获取可用余额, 不考虑冻结金额
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("OMNI_GetBalance error:{0} in {1}".format(e,get_linenumber()))
           



class OMNI_CreateRawTransaction(BaseHandler):
    @staticmethod
    def omni_createpayload_simplesend(omni_rpc_connection,amount):
        commands = [["omni_createpayload_simplesend",OMNI_PROPERTY_ID, amount]]
        rsp = omni_rpc_connection.batch_(commands)
        return rsp[0]

    @staticmethod
    def createrawtransaction(omni_rpc_connection,utxos,remain={}):
        commands = [["createrawtransaction",utxos,remain]]
        rsp = omni_rpc_connection.batch_(commands)
        return rsp[0]

    @staticmethod
    def omni_createrawtx_opreturn(omni_rpc_connection,rawdata1,rawdata2):
        commands = [["omni_createrawtx_opreturn",rawdata1,rawdata2]]
        rsp = omni_rpc_connection.batch_(commands)
        return rsp[0]

    @staticmethod
    def omni_createrawtx_reference(omni_rpc_connection,rawdata,toaddress):
        commands = [["omni_createrawtx_reference",rawdata,toaddress]]
        rsp = omni_rpc_connection.batch_(commands)
        return rsp[0]

    @staticmethod
    def omni_createrawtx_change(omni_rpc_connection,rawdata,utxos,fromaddress,fee):
        commands = [["omni_createrawtx_change",rawdata,utxos,fromaddress,fee]]
        rsp = omni_rpc_connection.batch_(commands)
        return rsp[0]

    @staticmethod
    def omni_getbalance(rpccon, strAddr):
        commands = [["omni_getbalance", strAddr, OMNI_PROPERTY_ID]] # usdt: 31 testnet-usdt:2
        data = rpccon.batch_(commands)
        if not data: return '%.8f' % 0.0
        strBalance = str(data[0]['balance'])
        return strBalance

    def get_argument_ex(self, str):
        str2dict = json.loads(self.request.body)
        return str2dict[str] if str in str2dict.keys() else False

    def post(self):
        rpcconn = AuthServiceProxy(OMNI_RPC_URL)
        try:
            lstSrcAddrs = self.get_argument_ex("src") 
            lstMapDstAddrs = self.get_argument_ex("dst")

            #参数检查
            if not isinstance(lstSrcAddrs, list):
                self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % ("src must be json list"))))
                return
            if not isinstance(lstMapDstAddrs, list):
                self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % ("dst must be json list"))))
                return

            if len(lstSrcAddrs) == 0:
                self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % ("src is empty"))))
                return

            if len(lstMapDstAddrs) == 0:
                self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % ("dst is empty"))))
                return

            strSrcAddr = lstSrcAddrs[0].strip()

            #获取支付手续费地址(目的地址)的utxo集(最小是0.0001 + 0.00000546)
            def chooseUTXO(rpcconn, addr):
                utxos = uBTC_ListUTXO.utxo(rpcconn, addr, 0)
                utxosRet = []
                for utxo in utxos:
                    nAmount = utxo['amount']
                    if nAmount >= 0.0001 + 0.00000546: utxosRet.append(utxo)  
                return utxosRet

            payFeeUtxos = chooseUTXO(rpcconn, strSrcAddr)
            import copy
            tmpPayFeeUtxos = copy.deepcopy(payFeeUtxos) 

            #1.判断UTXO数量是否足够
            if len(tmpPayFeeUtxos) < len(lstMapDstAddrs):
                self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % ("src have not enough UTXO"))))
                return

            #2.判断src地址USDT余额是否够
            strSrcBalance = OMNI_CreateRawTransaction.omni_getbalance(rpcconn, strSrcAddr)
            dSrcBalance = Decimal(strSrcBalance)
            
            dTxSum = Decimal('0.0') #需要转出的总金额
            for mapItem in lstMapDstAddrs:
                amount = mapItem['amount']
                if Decimal(str(amount)) <= Decimal('0.0'):
                    self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % ("src UTXO illegal"))))
                    return
                dTxSum += Decimal(str(amount))

            if dSrcBalance < dTxSum:
                self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % ("src address have not enough USDT balance"))))
                return

            retRawTxs = []

            #3.找零地址必须是src地址
            for mapItem in lstMapDstAddrs:
                strDstAddr = mapItem['addr']
                strUsdtAmount = mapItem['amount']
                strOrderId = mapItem['orderId'] #添加orderId区分不同提币订单, 原样返回

                def getMinUtxo(tmpUtxos):
                    nTmpMin = 1<<32
                    minUTXO = None
                    for utxo in tmpUtxos:
                        if  utxo['amount'] < nTmpMin:
                            nTmpMin = utxo['amount']
                            minUTXO = utxo
                    return minUTXO
                
                #关于这个utxo的金额,应该是    
                minPayFeeUtxo = getMinUtxo(tmpPayFeeUtxos) #获取最小的utxo
                tmpPayFeeUtxos.remove(minPayFeeUtxo)
                
                logging.info( "tmpPayFeeUtxos : {}".format( tmpPayFeeUtxos))

                from utils import filtered
                vin = []
                vin.append( filtered( minPayFeeUtxo ,  ["txid","vout"]) )
                vout = {}  #先填空即可

                # createrawtransaction  创建btc交易作为负载交易
                rawtx1 = OMNI_CreateRawTransactionEx_Collection.createrawtransaction(rpcconn, vin, vout)
                logging.info( "rawtx1 : {}".format( rawtx1))

                # omni_createpayload_simplesend  创建usdt交易
                rawtx2 = OMNI_CreateRawTransactionEx_Collection.omni_createpayload_simplesend(rpcconn, strUsdtAmount)
                logging.info( "rawtx2: {}".format( rawtx2))

                # omni_createrawtx_opreturn  将usdt交易绑定到btc交易上
                rawtx3 = OMNI_CreateRawTransactionEx_Collection.omni_createrawtx_opreturn(rpcconn, rawtx1, rawtx2 )
                logging.info("rawtx3 : {}".format( rawtx3))

                # omni_createrawtx_reference 添加usdt接收地址
                rawtx4 = OMNI_CreateRawTransactionEx_Collection.omni_createrawtx_reference(rpcconn, rawtx3, strDstAddr)
                logging.info("rawtx4: {}".format( rawtx4))


                # omni_createrawtx_change 添加找零地址和手续费,  注意: 字段名时 'value' 不是 'amount'
                vin = []
                vin.append( {'txid':minPayFeeUtxo['txid'],  \
                            "vout":minPayFeeUtxo['vout'], \
                            "scriptPubKey":minPayFeeUtxo['scriptPubKey'],\
                            "value": '%.8f'%minPayFeeUtxo['amount'] } ) 

                logging.info("vin : {}".format( vin))

                vout = {}

                nLeft = minPayFeeUtxo['amount'] - Decimal('0.0001') - Decimal('0.00000546')
                if nLeft < 0.0001:
                    logging.info("use all")
                    strFee = '%.8f' % (minPayFeeUtxo['amount'] - Decimal('0.00000546'))#全部用掉
                    vout[strDstAddr] = '0.00000546'
                else:
                    logging.info("use 0.00001000")
                    strFee = '0.00010000'
                    vout[strDstAddr] = '0.00000546'
                    vout[strSrcAddr] = '%.8f' % nLeft  #找零地址
                    logging.info('vout {0}'.format(vout))
                


                # 找零地址必须是src地址
                rawtx5  = OMNI_CreateRawTransactionEx_Collection.omni_createrawtx_change(rpcconn, rawtx4, vin, strSrcAddr, str(strFee))
                logging.info("rawtx5: {}".format( rawtx5))

                retRawTxs.append({"orderId":strOrderId, "hex": rawtx5, "utxos":[minPayFeeUtxo], "txout":vout, \
                        "txFee":strFee, "tokenAmount":strUsdtAmount, "tokenId":OMNI_PROPERTY_ID})

            self.write(json.dumps(BaseHandler.success_ret_with_data( retRawTxs ), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("OMNI_CreateRawTransaction error:{0} in {1}".format(e,get_linenumber()))


class OMNI_ListTransactions(BaseHandler):
    @staticmethod
    def blknumbers(rpc_connection,account="*",tx_counts=10):
        commands = [["omni_listtransactions",account,tx_counts]]
        data = rpc_connection.batch_(commands)
        return [item['block'] for item in data[0] if "block" in item]

    @staticmethod
    def process(rpc_connection,account="*",tx_counts=10000,skips=0):

        commands = [["omni_listtransactions", account, tx_counts, skips]]
        data = rpc_connection.batch_(commands)
        #print("----------")
        #print(data)
        #print("----------")
        from utils import filtered
        keys = ["txid","sendingaddress","referenceaddress","amount","propertyid","blocktime","confirmations","block"]
        retData =[]
        for item in data[0]:
            if "referenceaddress" not in item : continue
            if item["referenceaddress"].strip() not in g_exUserAddrs: 
                #print( item["referenceaddress"].strip() )
                continue
            
            if int(str(item["type_int"])) != 0: continue  # simple-send   
            if not bool(item["valid"]):   #防止假交易   2019-06-13 yqq
                logging.warning("%s is invalid usdt deposit tx" % item["txid"])
                continue

            #print("%s is valid tx" % item["txid"])
            if ":18332" in OMNI_RPC_URL:  #测试网
                if int(str(item["propertyid"])) != 2: continue    #  2 for USDT testnet
            elif ":8332" in OMNI_RPC_URL: #主网
                if int(str(item["propertyid"])) != 31: continue  #  31  for USDT mainnet 
            else:
                return []
            retData.append(item)
        return  [filtered(item, keys) for item in retData]


    def get(self):
        omni_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)
        try:
            address = self.get_argument("address") if self.get_argument("address") else "*"
            tx_counts = int(self.get_argument("count")) if self.get_argument("count") else 10
            skips = int(self.get_argument("skips")) if self.get_argument("skips") else 0
            data = OMNI_ListTransactions.process(omni_rpc_connection, address, tx_counts, skips)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("OMNI_ListTransActions error:{0} in {1}".format(e,get_linenumber()))

class OMNI_CrawlTxData(BaseHandler):
    @staticmethod
    def process(rpc_connection, nBlkNumber):
        count = 10000000
        txs = OMNI_ListTransactions.process(rpc_connection, '*', count)
        retTxs = [ tx for tx in txs  if int(str(tx['block'])) >= nBlkNumber-200 ]
        return retTxs 

    def post(self):
        omni_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)
        try:
            blknumber = int(self.get_argument("blknumber"))
            if blknumber < 0: self.write(json.dumps(BaseHandler.error_ret_with_data("error: illegal arg `blknumber`, must be positive number." )))
            data = OMNI_CrawlTxData.process(omni_rpc_connection,blknumber)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("OMNI_ListTransactions error:{0} in {1}".format(e,get_linenumber()))


class uBTC_GetBlockCount(BaseHandler):
    def get(self):
        btc_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)
        try:
            from btc.handler import BTC_GetBlockCount
            lastblknumber = BTC_GetBlockCount.process(btc_rpc_connection)
            self.write(json.dumps(BaseHandler.success_ret_with_data(lastblknumber), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("BTC_GetBlockCount error:{0} in {1}".format(e,get_linenumber()))

class OMNI_GetTransaction(BaseHandler):
    @staticmethod
    def process(rpc_connection,txid):
        commands = [["omi_gettransaction",txid]]
        transaction = rpc_connection.batch_(commands)
        from utils import filtered
        return filtered(transaction,["txid","sendingaddress","referenceaddress","amount","propertyid","blocktime","confirmations","block"])

    def post(self):
        btc_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)
        try:
            data = OMNI_GetTransaction.process(btc_rpc_connection,self.get_argument("txid"))
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("BTC_GetTransaction error:{0} in {1}".format(e,get_linenumber()))

class OMNI_ListBlockTransActions(BaseHandler):
    @staticmethod
    def process(rpc_connection,blknumber):
        commands = [["omni_listblocktransactions",blknumber]]
        txhashes = rpc_connection.batch_(commands)
        transactions = []
        for txhash in txhashes:
            transactions.append(OMNI_GetTransaction.process(rpc_connection,txhash))
        return transactions

    def post(self):
        btc_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)
        try:
            data = OMNI_ListBlockTransActions.process(btc_rpc_connection,self.get_argument("blknumber"))
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("BTC_GetTransaction error:{0} in {1}".format(e,get_linenumber()))



class OMNI_CollectionQuery(BaseHandler):

    @staticmethod
    def process(rpcconn, lstAddrs=[]):
        if True:
            commands = [["listunspent", 1, 99999999, lstAddrs]]
            lstUtxos = rpcconn.batch_(commands)[0]
            mapRet = {}
            usdtAddrs = [] #set()
            for utxo in lstUtxos:
                strAddr = utxo['address'].strip() 
                nAmount = utxo['amount']
                if strAddr not in g_exUserAddrs : continue
                if  strAddr not in usdtAddrs: 
                    #print('addr')
                    usdtAddrs.append(strAddr)

            for strAddr in usdtAddrs:
                #查询usdt地址里面usdt余额
                commands = [["omni_getbalance", strAddr, OMNI_PROPERTY_ID]] # usdt: 31 testnet-usdt:2
                data = rpcconn.batch_(commands)
                #print(data)
                if not data: mapRet[strAddr] = "%.8f" % 0
                strBalance = str(data[0]['balance'])
                if float(strBalance) > 0.00001:
                    mapRet[strAddr] = str(data[0]['balance'])
            return mapRet



    def get(self):
        rpcconn = AuthServiceProxy(OMNI_RPC_URL)
        try:
            mapRet = OMNI_CollectionQuery.process(rpcconn, [])
            self.write(json.dumps(BaseHandler.success_ret_with_data(mapRet), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("OMNI_CollectionQuery error:{0} in {1}".format(e, get_linenumber()))
        pass


#获取一次批量归集的数量
class OMNI_GetCollectionOnceCount(BaseHandler):

    @staticmethod
    def process(rpcconn, addr, minconf):
        utxos = uBTC_ListUTXO.utxo(rpcconn, addr, minconf)
        utxosRet = []
        for utxo in utxos:
            nAmount = utxo['amount']
            if nAmount > 0.0001: utxosRet.append(utxo)
        return utxosRet

    def get(self):
        try:
            rpcconn = AuthServiceProxy(OMNI_RPC_URL)
            txFeeAddr = self.get_argument("payfee_address")
            utxos = OMNI_GetCollectionOnceCount.process(rpcconn, txFeeAddr, 0)
            nCount = len(utxos)
            self.write(json.dumps(BaseHandler.success_ret_with_data(nCount), default=decimal_default))   
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s. " % e)))




class OMNI_CreateRawTransactionEx_Collection(BaseHandler):
    @staticmethod
    def omni_createpayload_simplesend(omni_rpc_connection,amount):
        commands = [["omni_createpayload_simplesend", OMNI_PROPERTY_ID, amount]]
        rsp = omni_rpc_connection.batch_(commands)
        return rsp[0]

    @staticmethod
    def createrawtransaction(omni_rpc_connection,utxos,remain={}):
        commands = [["createrawtransaction",utxos,remain]]
        rsp = omni_rpc_connection.batch_(commands)
        return rsp[0]

    @staticmethod
    def omni_createrawtx_opreturn(omni_rpc_connection,rawdata1,rawdata2):
        commands = [["omni_createrawtx_opreturn",rawdata1,rawdata2]]
        rsp = omni_rpc_connection.batch_(commands)
        return rsp[0]

    @staticmethod
    def omni_createrawtx_reference(omni_rpc_connection,rawdata,toaddress):
        commands = [["omni_createrawtx_reference",rawdata,toaddress]]
        rsp = omni_rpc_connection.batch_(commands)
        return rsp[0]

    @staticmethod
    def omni_createrawtx_change(omni_rpc_connection,rawdata,utxos,fromaddress,fee):
        commands = [["omni_createrawtx_change",rawdata,utxos,fromaddress,fee]]
        rsp = omni_rpc_connection.batch_(commands)
        return rsp[0]


    @staticmethod
    def omni_getbalance(rpcconn, strAddr):
        commands = [["omni_getbalance", strAddr, OMNI_PROPERTY_ID]] # usdt: 31 testnet-usdt:2
        data = rpcconn.batch_(commands)
        if not data: return '%.8f' % 0.0
        strBalance = str(data[0]['balance'])
        return strBalance


    def get_argument_ex(self, str):
        str2dict = json.loads(self.request.body)
        return str2dict[str] if str in str2dict.keys() else False

    def post(self):
        omni_rpc_connection = AuthServiceProxy(OMNI_RPC_URL)
        rpcconn = omni_rpc_connection 
        try:
            # get arguments
            src = self.get_argument_ex("src") 
            dest = self.get_argument_ex("dest")
            
            if not isinstance(src, list):
                self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % ("src must be json list"))))
                return
            if not isinstance(dest, list):
                self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % ("dest must be json list"))))
                return

            mapUsdtAmount = OMNI_CollectionQuery.process(rpcconn, src)
            strDstAddr = dest[0]

            #获取支付手续费地址(目的地址)的utxo集(最小是0.0001)
            payFeeUtxos = OMNI_GetCollectionOnceCount.process(rpcconn, strDstAddr, 0)
            import copy
            tmpPayFeeUtxos = copy.deepcopy(payFeeUtxos) 
            
            logging.info("payFeeUtxos : {}".format( payFeeUtxos))


            results = []     
            for strSrcAddr, strUsdtAmount in mapUsdtAmount.items():
                if len(tmpPayFeeUtxos) == 0:
                    break

                def getMinUtxo(tmpUtxos):
                    nTmpMin = 1<<32
                    minUTXO = None
                    for utxo in tmpUtxos:
                        if  utxo['amount'] < nTmpMin:
                            nTmpMin = utxo['amount']
                            minUTXO = utxo
                    return minUTXO

                #选择发送usdt的地址的一个utxo(最小的utxo , 一般是0.00000546)
                tmpUtxos = uBTC_ListUTXO.utxo(rpcconn, strSrcAddr, 1, 999999999)
                minUsdtSenderUtxo = getMinUtxo(tmpUtxos)

                logging.info( "min utxo:{}".format(minUsdtSenderUtxo ))

                #选择一个支付手续费的utxo(tmpPayFeeUtxos剩下最小的)
                minPayFeeUtxo = getMinUtxo(tmpPayFeeUtxos)
                logging.info( "min pay fee utxo:{}".format(minPayFeeUtxo ))

                tmpPayFeeUtxos.remove(minPayFeeUtxo)  #删除这个utxo, 防止双花错误

                logging.info("tmpPayFeeUtxos  : {}".format( tmpPayFeeUtxos))
                #return


                from utils import filtered
                vin = []
                vin.append( filtered(minUsdtSenderUtxo,  ["txid","vout"]) ) #必须把发送USDT的地址放在第一个
                vin.append( filtered( minPayFeeUtxo ,  ["txid","vout"]) )
                vout = {}  #先填空即可

                # createrawtransaction  创建btc交易作为负载交易
                rawtx1 = OMNI_CreateRawTransactionEx_Collection.createrawtransaction(rpcconn, vin, vout)
                logging.info("rawtx1: {}".format( rawtx1))

                # omni_createpayload_simplesend  创建usdt交易
                rawtx2 = OMNI_CreateRawTransactionEx_Collection.omni_createpayload_simplesend(rpcconn, strUsdtAmount)
                logging.info("rawtx2: {}".format( rawtx2))

                # omni_createrawtx_opreturn  将usdt交易绑定到btc交易上
                rawtx3 = OMNI_CreateRawTransactionEx_Collection.omni_createrawtx_opreturn(rpcconn, rawtx1, rawtx2 )
                logging.info("rawtx3: {}".format( rawtx3))
                #return

                # omni_createrawtx_reference 添加usdt接收地址
                rawtx4 = OMNI_CreateRawTransactionEx_Collection.omni_createrawtx_reference(rpcconn, rawtx3, strDstAddr)
                logging.info("rawtx4 : {}".format( rawtx4))

                # omni_createrawtx_change 添加找零地址和手续费,  注意: 字段名时 'value' 不是 'amount'
                vin = []
                vin.append( {'txid':minUsdtSenderUtxo['txid'], \
                             "vout":minUsdtSenderUtxo['vout'],\
                             "scriptPubKey":minUsdtSenderUtxo['scriptPubKey'], \
                            "value": '%.8f'%minUsdtSenderUtxo['amount']} ) 

                vin.append( {'txid':minPayFeeUtxo['txid'], \
                            "vout":minPayFeeUtxo['vout'], \
                            "scriptPubKey":minPayFeeUtxo['scriptPubKey'],\
                            "value": '%.8f'%minPayFeeUtxo['amount'] } ) 

                logging.info("vin : {}".format( vin))

                vout = {}
                nLeft = (minUsdtSenderUtxo['amount'] + minPayFeeUtxo['amount']) - Decimal('0.0001') 
                if nLeft < 0.0001:
                    #全部用掉
                    strFee = '%.8f' % minPayFeeUtxo['amount'] 
                    vout[strDstAddr] = '0.00000546'
                else:
                    #strFee = '%.8f' % minPayFeeUtxo['amount'] 
                    strFee = '0.00010000'
                    vout[strDstAddr] = '%.8f' % nLeft



                rawtx5  = OMNI_CreateRawTransactionEx_Collection.omni_createrawtx_change(rpcconn, rawtx4, vin, strDstAddr, str(strFee))
                logging.info("rawtx5: {}".format( rawtx5))

                results.append({"hex": rawtx5, "utxos":[minUsdtSenderUtxo, minPayFeeUtxo], "txout":vout, "txFee":strFee, "tokenAmount":strUsdtAmount, "tokenId":OMNI_PROPERTY_ID})
                
            logging.info("results:{}".format( results))

            self.write(json.dumps(BaseHandler.success_ret_with_data(results), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("OMNI_CreateRawTransactionEx_Collection error:{0} in {1}".format(e,get_linenumber()))











