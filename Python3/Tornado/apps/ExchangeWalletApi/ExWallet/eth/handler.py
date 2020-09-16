#coding:utf8

import logging
import json
from base_handler import BaseHandler
from utils import decimal_default,get_linenumber
from utils import RoundDown
from .proxy import EthereumProxy
from constants import ETH_IP_ADDR,ETH_RPC_PORT,ETH_BLK_BUFFER_SIZE
import  sql

from constants import ERC20_CONTRACTS_MAP   #ERC20合约地址


#设置精度 
import decimal
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 30

ip_addr, port = ETH_IP_ADDR,ETH_RPC_PORT


class ETH_GetBalance(BaseHandler):
    @staticmethod
    def get_balance(rpc_connection,addr,   block="latest"):
        balance = rpc_connection.eth_getBalance(addr, block)
        #return balance/float(10**18)
        return balance

    @classmethod
    def get_all_balance(cls, rpcconn, addr, symbol='', block='latest'):

        str_eth_balance = rpcconn.eth_getBalance(addr, block)
        dbalance = Decimal(str_eth_balance) / Decimal(10**18)
        dbalance =  RoundDown(dbalance)
        retData = {}
        retData['ETH'] = "%.8f" % dbalance

        if symbol.upper() == 'ETH':
            pass
        elif len(symbol) == 0:
            # 检查代币余额
            for contract_addr in ERC20_CONTRACTS_MAP.values():
                strSymbol = rpcconn.eth_erc20_symbol(contract_addr)
                strBalance = rpcconn.eth_erc20_balanceOf(contract_addr, addr, True)
                retData[strSymbol] = strBalance
        else:
            contract_addr = ERC20_CONTRACTS_MAP[symbol] if symbol != 'ERC20-USDT' else ERC20_CONTRACTS_MAP['USDT']
            strSymbol = rpcconn.eth_erc20_symbol(contract_addr)
            strBalance = rpcconn.eth_erc20_balanceOf(contract_addr, addr, True)
            retData[strSymbol] = strBalance

        if 'USDT' in retData:
            retData['ERC20-USDT'] = retData['USDT']
            del (retData['USDT'])

        return retData

    def post(self):
        rpcconn = EthereumProxy(ip_addr, port)
        try:
            address = self.get_argument("address")
            if len(address) != 42:
                self.write(json.dumps(BaseHandler.error_ret_with_data("arguments error")))
                return

            # symbol = self.get_argument('symbol')
            # print("symbol:{}".format(symbol))

            # balance = ETH_GetBalance.get_balance(rpc_connection,address)
            data = ETH_GetBalance.get_all_balance(rpcconn, address)
            self.write(json.dumps(BaseHandler.success_ret_with_data( data ), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("ETH_GetBalance error:{0} in {1}".format(e,get_linenumber()))
           
            
class ETH_PendingTransactions(BaseHandler):
    def get(self):
        rpc_connection = EthereumProxy(ip_addr, port)
        try:
            data = rpc_connection.eth_pendingTransactions()
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("ETH_PendingTransactions error:{0} in {1}".format(e,get_linenumber()))


class ETH_SendRawTransaction(BaseHandler):

    def get_order_from_db(self, order_id):
        import sql
        sqlRet = sql.run("select * from tb_eth_broadcast where order_id='{0}';".format(order_id))
        if len(sqlRet) == 0: return (False, "")
        txid = sqlRet[0]['txid']
        return (True, txid)

    def insert_txid_into_db(self, order_id, txid):
        import sql
        strSql = """insert into tb_eth_broadcast(order_id, txid) values('{}','{}');""".format(order_id, txid)
        logging.info('sql: {}'.format(strSql))
        sqlRet = sql.run(strSql)

    def post(self):
        rpc_connection = EthereumProxy(ip_addr, port)
        try:
            data = str(self.get_argument("data"))
            order_id = str(self.get_argument('orderId'))
            flag, txid = self.get_order_from_db(order_id)
            if flag: #如果是已经广播过的则不再广播
                rspData = {'txid':txid, 'orderId':order_id}
                self.write(json.dumps(BaseHandler.success_ret_with_data(rspData), default=decimal_default))
                return

            # 0x checking
            rlpdata = "0x" + data if "0x" not in data else data
            # sending raw transaction
            txid = rpc_connection.eth_sendRawTransaction(rlpdata)
            self.insert_txid_into_db(order_id, txid)
            rspData = {'txid':txid, 'orderId':order_id}
            self.write(json.dumps(BaseHandler.success_ret_with_data(rspData), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("ETH_SendRawTransaction error:{0} in {1}".format(e,get_linenumber()))

class ETH_ListAccounts(BaseHandler):
    @staticmethod
    def addresses():
        from sql import run
        accounts = run("""select address from t_eth_accounts;""")
        return [account['address'].strip() for account in accounts]

    def get(self):
        try:
            data = ETH_ListAccounts.addresses()
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("ETH_Accounts error:{0} in {1}".format(e,get_linenumber()))
            
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
            logging.error("ETH_BlockNumber error:{0} in {1}".format(e,get_linenumber()))

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
            logging.error("ETH_GetBlockTransactionCount error:{0} in {1}".format(e,get_linenumber()))

class ETH_GetTransactionFromBlock(BaseHandler):
    @staticmethod
    def process(rpc_connection,blknumber,txindex):
        txdata =  rpc_connection.eth_getTransactionByBlockNumberAndIndex(blknumber,txindex)
        blockData  = rpc_connection.eth_getBlockByNumber(blknumber)
        txdata["blocktime"] = blockData["timestamp"] if blockData and "timestamp" in blockData else 0
        txdata["confirmations"] =  ETH_BlockNumber.latest(rpc_connection) - blknumber
        txdata["blockNumber"] = blknumber
        from utils import filtered,alterkeyname
        retData = filtered(alterkeyname(txdata,'hash','txid'),["confirmations", "blocktime",
                 "blockNumber","nonce","txid","from","to","value","gas","gasPrice"]) if txdata else False

        for key in ["nonce", "gas", "value", "gasPrice", "blocktime"]:
            if "0x" in retData[key]: retData[key] = str(int(retData[key], 16))
            getcontext().prec = 30
            dValue = RoundDown(Decimal(retData[key]) / Decimal(10**18 ))
            if key in ["value"]: retData[key] = "%.8f" % dValue

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
            logging.error("ETH_GetTransactionFromBlock error:{0} in {1}".format(e,get_linenumber()))


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
            logging.error("ETH_GetBlockTransactions error:{0} in {1}".format(e,get_linenumber()))



#2019-05-01 yqq
#获取用户充币信息的接口, 直接从数据库中获取交易数据
#不再临时扫描区块
class ETH_CrawlTxData(BaseHandler):

    def GetTxDataFromDB(self, nBegin, nEnd, symbol='ETH'):

        try:
            if not (isinstance(nBegin, int) and isinstance(nEnd, int)  ):
                logging.error("nBegin or nEnd is not int type.")
                return []

            txRet = []

            # strSql = """SELECT txdata FROM t_eth_charge WHERE  height >= {0} and height <= {1};""".format(nBegin, nEnd)
            strSql = """SELECT * FROM tb_eth_series_deposit  WHERE symbol='{}' and block_number>={} and block_number<={}; """.format(symbol, nBegin, nEnd)
            logging.info("sql  : {}".format(strSql))

            #print(strSql)
            sqlRet = sql.run(strSql)
            # print(sqlRet)

            if not isinstance(sqlRet, list):
                return []
            for item in sqlRet:
                tx = {}
                tx['symbol'] = item['symbol']
                tx["txid"] = item['txid']
                tx["from"] = item["from"]
                tx["to"] = item["to"]
                tx["nonce"] = item['nonce']
                tx["blocktime"] = item['block_time']
                tx["confirmations"] = item['confirmations']
                tx["blockNumber"] = item['block_number']
                tx["value"] = item['value']


                if symbol == 'USDT': tx['symbol'] = 'ERC20-USDT'

                txRet.append(tx)
            return txRet
        except Exception as e:
            logging.error("GetTxDataInfoDB(nBegin, nEnd, symbol):{}".format( e))
            return []
        pass

    #@staticmethod
    def process(self,  nStart, symbol='ETH'):
        txRet =  self.GetTxDataFromDB(nStart, (1<<64) - 1, symbol)
        return txRet 


    def post(self):
        try:
            logging.info('URI: {}'.format( self.request.uri) )
            strURI = self.request.uri
            symbol = strURI [ strURI.find('/', 0) + 1 :  strURI.rfind('/') ]  # 类似:    /link/crawltransactions
            if symbol.upper() == 'ERC20-USDT': symbol = 'USDT'

            symbol = symbol.upper()
            # print("symbol:{}".format(symbol))

            nStart  = int(self.get_argument("blknumber"))
            data = self.process(nStart, symbol)
            logging.info('data : {}'.format(data))
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("ETH_CrawlTxData error:{0} in {1}".format(e,get_linenumber()))

    def get(self):
        self.post()


class ETH_GetTransactionCount(BaseHandler):
    def post(self):
        rpc_connection = EthereumProxy(ip_addr, port)
        try:
            address = self.get_argument("address")
            nonce = rpc_connection.eth_getTransactionCount(address, "pending") #获取最新nonce值, 不需要加1
            self.write(json.dumps(BaseHandler.success_ret_with_data(str(nonce)), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("ETH_GetTransactionCount error:{0} in {1}".format(e,get_linenumber()))

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
            logging.error("ETH_GetBlockByNumber Error:{0} in {1}".format(e,get_linenumber()))

class ETH_GetTransactionByHash(BaseHandler):
    def post(self):
        rpc_connection = EthereumProxy(ip_addr, port)
        try:
            tx_hash = self.get_argument("tx_hash")
            tx_info = rpc_connection.eth_getTransactionByHash(tx_hash)
            self.write(json.dumps(BaseHandler.success_ret_with_data(tx_info), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("ETH_GetTransactionByHash error:{0} in {1}".format(e,get_linenumber()))




class ETH_CollectionQueryEx(BaseHandler):

    def QueryBalanceAndNonce(self, rpcconn, addrs, symbol):

        retList = []
        for addr in addrs:
            all_balance = ETH_GetBalance.get_all_balance(rpcconn, addr, symbol,"latest")
            logging.info(all_balance)

            if len(all_balance) > 0 and Decimal(all_balance[symbol]) < 0.001:
                logging.info("skip : {}".format(all_balance))
                continue

            nNonce = rpcconn.eth_getTransactionCount(addr, "pending")  # 获取最新nonce值, 不需要加1
            # nNonce = rpcconn.eth_getTransactionCount(addr, "latest")  # 获取最新nonce值, 不需要加1
            retList.append({'address': addr, 'balances': all_balance, 'nonce': nNonce})
        return retList

    def proccess(self, rpcconn , symbol):
        #1.从t_eth_active_addr 表中获取所有活跃地址,按照余额排序
        strSql = """SELECT  address FROM tb_eth_series_active_addrs WHERE `symbol`='{}' AND `balance` > 0.0001 ORDER BY `balance` DESC LIMIT 100;""".format(symbol)
        sqlRet = sql.run(strSql)
        addrs = []
        for item in sqlRet:
            if "address" in item:
                if item['address'] not in addrs: addrs.append(item["address"])
        #2.遍历所有地址, 实时查询地址余额
        tmpSymbol = 'ERC20-USDT' if symbol == 'USDT' else symbol
        return self.QueryBalanceAndNonce(rpcconn, addrs, tmpSymbol)
        #3.返回数据

    def get(self):
        try:
            symbol = self.get_argument("symbol")
        except :
            logging.warning('no symbol arg, default is eth')
            symbol = "eth"
            pass

        rpcconn =  EthereumProxy(ip_addr, port)
        try:
            if symbol.upper() == 'ERC20-USDT':
                symbol = 'USDT'
            elif not symbol.isalpha() : #防止sql注入
                raise  Exception("invalid symbol, must token symbol")

            symbol = symbol.upper()
            if symbol != 'ETH' and symbol not in ERC20_CONTRACTS_MAP.keys():
                retData = []
            else:
                retData = self.proccess(rpcconn, symbol)  #从活跃地址表中获取地址信息
            self.write(json.dumps(BaseHandler.success_ret_with_data(retData), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error(" ETH_CollectionQueryEx error:{0} in {1}".format(e,get_linenumber()))





class ETH_GasPrice(BaseHandler):
    """
    2020-08-18 yqq 新增  实现动态手续费
    """

    def get(self):
        try:
            # rpcconn =  EthereumProxy(ip_addr, port)
            rpcconn =  EthereumProxy(ip_addr, 8545)  #DEBUG
            gas_price = rpcconn.eth_gasPrice()
            self.write(json.dumps(BaseHandler.success_ret_with_data(str(gas_price)), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error(" ETH_CollectionQueryEx error:{0} in {1}".format(e,get_linenumber()))





