#coding:utf8

import sys

if sys.version_info < (3, 0):
    print("please use python3")
    raise Exception("please use  python3 !!")


import tornado.ioloop
import tornado.web
import tornado.httpserver
import os.path
from base_handler import BaseHandler
import platform
import tornado.log
from tornado.options import options, define
import logging

from btc.handler import BTC_GetAccount,BTC_GetAccountAddress
from btc.handler import BTC_GetBalance, BTC_GetAccountBalance, BTC_ListAccounts
from btc.handler import BTC_ListUTXO, BTC_CreateRawTransaction,  BTC_SendRawTransaction
from btc.handler import BTC_GetRawTransaction, BTC_ListTransactions, BTC_CrawlTxData
from btc.handler import BTC_CreateRawTransactionEx
from btc.handler import BTC_CreateRawTransactionEx_Collection
from btc.handler import BTC_CollectionQuery
from btc.handler import BTC_EstimateSmartFee


from usdt.handler import uBTC_GetBalance, uBTC_ListUTXO, uBTC_ListAccounts, OMNI_GetBalance 
from usdt.handler import OMNI_CreateRawTransaction, uBTC_CreateRawTransaction,  uBTC_SendRawTransaction
from usdt.handler import OMNI_ListTransactions, OMNI_CrawlTxData
from usdt.handler import OMNI_CollectionQuery
from usdt.handler import OMNI_GetCollectionOnceCount
from usdt.handler import OMNI_CreateRawTransactionEx_Collection

from ltc.handler import BTC_GetAccount as LTC_GetAccount
from ltc.handler import BTC_GetAccountAddress as LTC_GetAccountAddress
from ltc.handler import BTC_GetBalance as LTC_GetBalance
from ltc.handler import BTC_GetAccountBalance as LTC_GetAccountBalance
from ltc.handler import BTC_ListAccounts as LTC_ListAccounts
from ltc.handler import BTC_ListUTXO as LTC_ListUTXO
from ltc.handler import BTC_CreateRawTransaction as LTC_CreateRawTransaction
from ltc.handler import BTC_SendRawTransaction as LTC_SendRawTransaction
from ltc.handler import BTC_GetRawTransaction as LTC_GetRawTransaction
from ltc.handler import BTC_ListTransactions as LTC_ListTransactions
from ltc.handler import BTC_CrawlTxData as LTC_CrawlTxData
from ltc.handler import BTC_CreateRawTransactionEx as LTC_CreateRawTransactionEx
from ltc.handler import BTC_CreateRawTransactionEx_Collection as LTC_CreateRawTransactionEx_Collection
from ltc.handler import BTC_CollectionQuery as LTC_CollectionQuery
from ltc.handler import BTC_EstimateSmartFee as LTC_EstimateSmartFee




from bch.handler import BTC_GetAccount as BCH_GetAccount
from bch.handler import BTC_GetAccountAddress as BCH_GetAccountAddress
from bch.handler import BTC_GetBalance as BCH_GetBalance
from bch.handler import BTC_GetAccountBalance as BCH_GetAccountBalance
from bch.handler import BTC_ListAccounts as BCH_ListAccounts
from bch.handler import BTC_ListUTXO as BCH_ListUTXO
from bch.handler import BTC_CreateRawTransaction as BCH_CreateRawTransaction
from bch.handler import BTC_SendRawTransaction as BCH_SendRawTransaction
from bch.handler import BTC_GetRawTransaction as BCH_GetRawTransaction
from bch.handler import BTC_ListTransactions as BCH_ListTransactions
from bch.handler import BTC_CrawlTxData as BCH_CrawlTxData
from bch.handler import BTC_CreateRawTransactionEx as BCH_CreateRawTransactionEx
from bch.handler import BTC_CreateRawTransactionEx_Collection as BCH_CreateRawTransactionEx_Collection
from bch.handler import BTC_CollectionQuery as BCH_CollectionQuery
from bch.handler import BTC_EstimateSmartFee as BCH_EstimateSmartFee


from bsv.handler import BTC_GetAccount as BSV_GetAccount
from bsv.handler import BTC_GetAccountAddress as BSV_GetAccountAddress
from bsv.handler import BTC_GetBalance as BSV_GetBalance
from bsv.handler import BTC_GetAccountBalance as BSV_GetAccountBalance
from bsv.handler import BTC_ListAccounts as BSV_ListAccounts
from bsv.handler import BTC_ListUTXO as BSV_ListUTXO
from bsv.handler import BTC_CreateRawTransaction as BSV_CreateRawTransaction
from bsv.handler import BTC_SendRawTransaction as BSV_SendRawTransaction
from bsv.handler import BTC_GetRawTransaction as BSV_GetRawTransaction
from bsv.handler import BTC_ListTransactions as BSV_ListTransactions
from bsv.handler import BTC_CrawlTxData as BSV_CrawlTxData
from bsv.handler import BTC_CreateRawTransactionEx as BSV_CreateRawTransactionEx
from bsv.handler import BTC_CreateRawTransactionEx_Collection as BSV_CreateRawTransactionEx_Collection
from bsv.handler import BTC_CollectionQuery as BSV_CollectionQuery
from bsv.handler import BTC_EstimateSmartFee as BSV_EstimateSmartFee


from dash.handler import BTC_GetAccount as DASH_GetAccount
from dash.handler import BTC_GetAccountAddress as DASH_GetAccountAddress
from dash.handler import BTC_GetBalance as DASH_GetBalance
from dash.handler import BTC_GetAccountBalance as DASH_GetAccountBalance
from dash.handler import BTC_ListAccounts as DASH_ListAccounts
from dash.handler import BTC_ListUTXO as DASH_ListUTXO
from dash.handler import BTC_CreateRawTransaction as DASH_CreateRawTransaction
from dash.handler import BTC_SendRawTransaction as DASH_SendRawTransaction
from dash.handler import BTC_GetRawTransaction as DASH_GetRawTransaction
from dash.handler import BTC_ListTransactions as DASH_ListTransactions
from dash.handler import BTC_CrawlTxData as DASH_CrawlTxData
from dash.handler import BTC_CreateRawTransactionEx as DASH_CreateRawTransactionEx
from dash.handler import BTC_CreateRawTransactionEx_Collection as DASH_CreateRawTransactionEx_Collection
from dash.handler import BTC_CollectionQuery as DASH_CollectionQuery
from dash.handler import BTC_EstimateSmartFee as DASH_EstimateSmartFee



# from bsv.handler import BSV_CrawlTxData
# from bch.handler import BCH_CrawlTxData
# from dash.handler import DASH_CrawlTxData

from eth.handler import ETH_ListAccounts,ETH_GetBalance
from eth.handler import  ETH_SendRawTransaction
from eth.handler import ETH_CrawlTxData, ETH_GetTransactionCount
from eth.handler import ETH_GetBlockByNumber
from eth.handler import ETH_BlockNumber
from eth.handler import ETH_CollectionQueryEx
from eth.handler import ETH_GasPrice


from etc.handler import ETH_ListAccounts as ETC_ListAccounts
from etc.handler import ETH_GetBalance as ETC_GetBalance
from etc.handler import ETH_SendRawTransaction as ETC_SendRawTransaction
from etc.handler import ETH_CrawlTxData as ETC_CrawlTxData
from etc.handler import ETH_GetTransactionCount as ETC_GetTransactionCount
from etc.handler import ETH_GetBlockByNumber as ETC_GetBlockByNumber
from etc.handler import ETH_BlockNumber as ETC_BlockNumber
from etc.handler import ETH_CollectionQueryEx  as ETC_CollectionQueryEx


from usdp.handler import  USDP_GetBalance,  USDP_SendRawTransaction 
from usdp.handler import  USDP_CrawlTxData, USDP_GetAccountInfo, USDP_IsValidTx, USDP_CollectionQuery


from htdf.handler import USDP_ListAccounts as HTDF_ListAccounts 
from htdf.handler import USDP_GetBalance as HTDF_GetBalance 
from htdf.handler import USDP_SendRawTransaction as HTDF_SendRawTransaction 
from htdf.handler import USDP_GetLatestBlockNumber as HTDF_GetLatestBlockNumber 
from htdf.handler import USDP_CrawlTxData as  HTDF_CrawlTxData 
from htdf.handler import USDP_GetAccountInfo as HTDF_GetAccountInfo
from htdf.handler import USDP_GetTransactionFromBlock  as HTDF_GetTransactionFromBlock
from htdf.handler import USDP_IsValidTx as  HTDF_IsValidTx  
from htdf.handler import USDP_CollectionQuery as HTDF_CollectionQuery

from het.handler import USDP_ListAccounts as HET_ListAccounts 
from het.handler import USDP_GetBalance as HET_GetBalance 
from het.handler import USDP_SendRawTransaction as HET_SendRawTransaction 
from het.handler import USDP_GetLatestBlockNumber as HET_GetLatestBlockNumber 
from het.handler import USDP_CrawlTxData as  HET_CrawlTxData 
from het.handler import USDP_GetAccountInfo as HET_GetAccountInfo
from het.handler import USDP_GetTransactionFromBlock  as HET_GetTransactionFromBlock
from het.handler import USDP_IsValidTx as  HET_IsValidTx  
from het.handler import USDP_CollectionQuery as HET_CollectionQuery

from xrp.handler import XRP_CrawlTxData
from xrp.handler import XRP_GetAccountInfo
from  xrp.handler import XRP_GetBalance
from xrp.handler import  XRP_Submit
from xrp.handler import XRP_GetTransactionByHash


from eos.handler import  EOS_CrawlTxData
from eos.handler import EOS_GetBalance, EOS_GetAccountInfo, EOS_CreateRawTransaction
from eos.handler import EOS_SendRawtransaction

from xlm.handler import XLM_CrawlTxData, XLM_GetAccountInfo
from xlm.handler import XLM_GetBalance
from xlm.handler import XLM_GetTransactionByHash
from xlm.handler import XLM_SendRawtransaction


from trx.handler import TRX_CrawlTxData
from trx.handler import TRX_CreateRawTransaction
from trx.handler import TRX_GetAccountInfo
from trx.handler import TRX_GetBalance
from trx.handler import TRX_SendRawTransaction
from trx.handler import TRX_CollectionQuery


from xmr.xmr_handler import XMR_CrawlTxData
from xmr.xmr_handler import XMR_Refresh,XMR_ExportTxOutputs,XMR_ImportKeyImages
from xmr.xmr_handler import XMR_CreateRawTransactions,XMR_SendRawTransaction
from xmr.xmr_handler import XMR_GetBalance, XMR_GetAllBalance


class MainHandler(BaseHandler):
    def get(self):
        self.write("pong")
    def post(self):
        self.write("pong")



def make_app():
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/ping", MainHandler),

        ############# BTC #################################
        (r"/btc/getbalance", BTC_GetBalance),
        (r"/btc/getunspents", BTC_ListUTXO),
        (r"/btc/createrawtransaction", BTC_CreateRawTransaction),
        (r"/btc/createrawtransactionex", BTC_CreateRawTransactionEx),
        (r"/btc/createrawtransactionex_collection", BTC_CreateRawTransactionEx_Collection),
        (r"/btc/sendrawtransaction", BTC_SendRawTransaction),
        (r"/btc/listtransactions", BTC_ListTransactions),
        (r"/btc/getrawtransaction", BTC_GetRawTransaction),
        (r"/btc/crawltransactions", BTC_CrawlTxData),
        (r"/btc/listaccounts", BTC_ListAccounts),
        # (r"/btc/calcfee", BTC_CalcFee),
        (r"/btc/collectionquery", BTC_CollectionQuery),
        (r"/btc/calcfee", BTC_EstimateSmartFee),
        ###############################################

        ############ USDT ##############################
        (r"/usdt/getunspents", uBTC_ListUTXO),
        (r"/usdt/btc/getbalance", uBTC_GetBalance),
        (r"/usdt/getbalance", OMNI_GetBalance),
        (r"/usdt/btc/listaccounts", uBTC_ListAccounts),
        (r"/usdt/listtransactions", OMNI_ListTransactions),
        (r"/usdt/crawltransactions", OMNI_CrawlTxData),
        (r"/usdt/createrawtransaction", OMNI_CreateRawTransaction),
        (r"/usdt/btc/createrawtransaction", uBTC_CreateRawTransaction),
        (r"/usdt/sendrawtransaction", uBTC_SendRawTransaction),
        (r"/usdt/collectionquery", OMNI_CollectionQuery),
        (r"/usdt/getcollectiononcecount", OMNI_GetCollectionOnceCount),
        (r"/usdt/createrawtransactionex_collection", OMNI_CreateRawTransactionEx_Collection),
        #####################################################
 		
		############ LTC ##############################
        (r"/ltc/getbalance", LTC_GetBalance),
        (r"/ltc/getunspents", LTC_ListUTXO),
        (r"/ltc/createrawtransaction", LTC_CreateRawTransaction),
        (r"/ltc/createrawtransactionex", LTC_CreateRawTransactionEx),
        (r"/ltc/createrawtransactionex_collection", LTC_CreateRawTransactionEx_Collection),
        (r"/ltc/sendrawtransaction", LTC_SendRawTransaction),
        (r"/ltc/listtransactions", LTC_ListTransactions),
        (r"/ltc/getrawtransaction", LTC_GetRawTransaction),
        (r"/ltc/crawltransactions", LTC_CrawlTxData),
        (r"/ltc/listaccounts", LTC_ListAccounts),
        (r"/ltc/calcfee", LTC_EstimateSmartFee),
        (r"/ltc/collectionquery", LTC_CollectionQuery),
        #####################################################

        ############ BCH ##############################
        (r"/bch/getbalance", BCH_GetBalance),
        (r"/bch/getunspents", BCH_ListUTXO),
        (r"/bch/createrawtransaction", BCH_CreateRawTransaction),
        (r"/bch/createrawtransactionex", BCH_CreateRawTransactionEx),
        (r"/bch/createrawtransactionex_collection", BCH_CreateRawTransactionEx_Collection),
        (r"/bch/sendrawtransaction", BCH_SendRawTransaction),
        (r"/bch/listtransactions", BCH_ListTransactions),
        (r"/bch/getrawtransaction", BCH_GetRawTransaction),
        (r"/bch/crawltransactions", BCH_CrawlTxData),
        (r"/bch/listaccounts", BCH_ListAccounts),
        (r"/bch/calcfee", BCH_EstimateSmartFee),
        (r"/bch/collectionquery", BCH_CollectionQuery),
        #####################################################

        ############ BSV ##############################
        (r"/bsv/getbalance", BSV_GetBalance),
        (r"/bsv/getunspents", BSV_ListUTXO),
        (r"/bsv/createrawtransaction", BSV_CreateRawTransaction),
        (r"/bsv/createrawtransactionex", BSV_CreateRawTransactionEx),
        (r"/bsv/createrawtransactionex_collection", BSV_CreateRawTransactionEx_Collection),
        (r"/bsv/sendrawtransaction", BSV_SendRawTransaction),
        (r"/bsv/listtransactions", BSV_ListTransactions),
        (r"/bsv/getrawtransaction", BSV_GetRawTransaction),
        (r"/bsv/crawltransactions", BSV_CrawlTxData),
        (r"/bsv/listaccounts", BSV_ListAccounts),
        (r"/bsv/calcfee", BSV_EstimateSmartFee),
        (r"/bsv/collectionquery", BSV_CollectionQuery),
        #####################################################



        ############ DASH ##############################
        (r"/dash/getbalance", DASH_GetBalance),
        (r"/dash/getunspents", DASH_ListUTXO),
        (r"/dash/createrawtransaction", DASH_CreateRawTransaction),
        (r"/dash/createrawtransactionex", DASH_CreateRawTransactionEx),
        (r"/dash/createrawtransactionex_collection", DASH_CreateRawTransactionEx_Collection),
        (r"/dash/sendrawtransaction", DASH_SendRawTransaction),
        (r"/dash/listtransactions", DASH_ListTransactions),
        (r"/dash/getrawtransaction", DASH_GetRawTransaction),
        (r"/dash/crawltransactions", DASH_CrawlTxData),
        (r"/dash/listaccounts", DASH_ListAccounts),
        (r"/dash/calcfee", DASH_EstimateSmartFee),
        (r"/dash/collectionquery", DASH_CollectionQuery),
        #####################################################


        ############ ETH ####################################
        (r"/eth/getbalance", ETH_GetBalance),
        (r"/eth/sendrawtransaction", ETH_SendRawTransaction),
        (r"/eth/crawltransactions", ETH_CrawlTxData),
        (r"/eth/gettransactioncount", ETH_GetTransactionCount),
        (r"/eth/getblockbynumber", ETH_GetBlockByNumber),
        (r"/eth/blocknumber", ETH_BlockNumber),
        # (r"/eth/collectionquery", ETH_CollectionQuery),
        (r"/eth/collectionquery", ETH_CollectionQueryEx),
        (r"/eth/gasprice", ETH_GasPrice),
        ####################################################

        ############# ERC20 ###################################
        (r"/yqb/crawltransactions", ETH_CrawlTxData),
        (r"/bjc/crawltransactions", ETH_CrawlTxData),
        (r"/ht/crawltransactions", ETH_CrawlTxData),
        (r"/mbjc/crawltransactions", ETH_CrawlTxData),
        (r"/leo/crawltransactions", ETH_CrawlTxData),
        (r"/bnb/crawltransactions", ETH_CrawlTxData),
        (r"/bei/crawltransactions", ETH_CrawlTxData),
        (r"/spqq/crawltransactions", ETH_CrawlTxData),
        (r"/ecny/crawltransactions", ETH_CrawlTxData),
        (r"/link/crawltransactions", ETH_CrawlTxData),
        (r"/zil/crawltransactions", ETH_CrawlTxData),
        (r"/elf/crawltransactions", ETH_CrawlTxData),
        (r"/xmx/crawltransactions", ETH_CrawlTxData),
        (r"/tnb/crawltransactions", ETH_CrawlTxData),
        (r"/usdt/crawltransactions", ETH_CrawlTxData),

        (r"/erc20-usdt/crawltransactions", ETH_CrawlTxData),
        (r"/omg/crawltransactions", ETH_CrawlTxData),
        (r"/mkr/crawltransactions", ETH_CrawlTxData),
        (r"/loom/crawltransactions", ETH_CrawlTxData),
        (r"/mco/crawltransactions", ETH_CrawlTxData),
        (r"/cvc/crawltransactions", ETH_CrawlTxData),
        (r"/rep/crawltransactions", ETH_CrawlTxData),
        (r"/ctxc/crawltransactions", ETH_CrawlTxData),
        (r"/abt/crawltransactions", ETH_CrawlTxData),
        (r"/ppt/crawltransactions", ETH_CrawlTxData),
        (r"/fsn/crawltransactions", ETH_CrawlTxData),
        (r"/req/crawltransactions", ETH_CrawlTxData),
        (r"/tnt/crawltransactions", ETH_CrawlTxData),

        (r"/lily/crawltransactions", ETH_CrawlTxData),
        (r"/eutd/crawltransactions", ETH_CrawlTxData),

        (r"/ktv/crawltransactions", ETH_CrawlTxData),
        (r"/ajc/crawltransactions", ETH_CrawlTxData),
        ######################################################

        ########## ETC #####################
        (r"/etc/getbalance", ETC_GetBalance),
        (r"/etc/sendrawtransaction", ETC_SendRawTransaction),
        (r"/etc/crawltransactions", ETC_CrawlTxData),
        (r"/etc/gettransactioncount", ETC_GetTransactionCount),
        (r"/etc/getblockbynumber", ETC_GetBlockByNumber),
        (r"/etc/blocknumber", ETC_BlockNumber),
        # (r"/eth/collectionquery", ETH_CollectionQuery),
        (r"/etc/collectionquery", ETC_CollectionQueryEx),
        ##################################################



        #######USDP #################
        (r"/usdp/getbalance", USDP_GetBalance),
        (r"/usdp/sendrawtransaction", USDP_SendRawTransaction),
        (r"/usdp/crawltransactions", USDP_CrawlTxData),
        (r"/usdp/getaccountinfo", USDP_GetAccountInfo),
        (r"/usdp/isvalidtx", USDP_IsValidTx),
        (r"/usdp/collectionquery", USDP_CollectionQuery),
        ############################

        ########HTDF########################
        (r"/htdf/getbalance", HTDF_GetBalance),
        (r"/htdf/sendrawtransaction", HTDF_SendRawTransaction),
        (r"/htdf/crawltransactions", HTDF_CrawlTxData),
        (r"/htdf/getaccountinfo", HTDF_GetAccountInfo),
        (r"/htdf/isvalidtx", HTDF_IsValidTx),
         (r"/htdf/collectionquery", HTDF_CollectionQuery),
        (r"/hrc20-ajc/crawltransactions", HTDF_CrawlTxData),
        (r"/hfh/crawltransactions", HTDF_CrawlTxData),
        (r"/bwc/crawltransactions", HTDF_CrawlTxData),
        (r"/hrc20-usdp/crawltransactions", HTDF_CrawlTxData),
        (r"/hrc20-het/crawltransactions", HTDF_CrawlTxData),
        (r"/hrc20-bei/crawltransactions", HTDF_CrawlTxData),
        (r"/aqc/crawltransactions", HTDF_CrawlTxData),
        (r"/sjc/crawltransactions", HTDF_CrawlTxData),

        (r"/btu/crawltransactions", HTDF_CrawlTxData),
        (r"/svu/crawltransactions", HTDF_CrawlTxData),
        (r"/bkl/crawltransactions", HTDF_CrawlTxData),

        (r"/jxc/crawltransactions", HTDF_CrawlTxData),
        (r"/agg/crawltransactions", HTDF_CrawlTxData),
        (r"/hhg/crawltransactions", HTDF_CrawlTxData),

        (r"/htd/crawltransactions", HTDF_CrawlTxData),
        (r"/kml/crawltransactions", HTDF_CrawlTxData),
        (r"/msl/crawltransactions", HTDF_CrawlTxData),
        (r"/dfq/crawltransactions", HTDF_CrawlTxData),
        (r"/ttb/crawltransactions", HTDF_CrawlTxData),

        ############################

        ########HET########################
        (r"/het/getbalance", HET_GetBalance),
        (r"/het/sendrawtransaction", HET_SendRawTransaction),
        (r"/het/crawltransactions", HET_CrawlTxData),
        (r"/het/getaccountinfo", HET_GetAccountInfo),
        (r"/het/isvalidtx", HET_IsValidTx),
        (r"/het/collectionquery", HET_CollectionQuery),
        ############################


        ########### XRP ########################
        (r"/xrp/crawltransactions", XRP_CrawlTxData),
        (r"/xrp/getaccountinfo", XRP_GetAccountInfo),
        (r"/xrp/getbalance", XRP_GetBalance),
        (r"/xrp/sendrawtransaction", XRP_Submit),
        (r"/xrp/gettransaction", XRP_GetTransactionByHash),


        #########################################


        ############## EOS ######################
        (r"/eos/crawltransactions", EOS_CrawlTxData),
        (r"/eos/getbalance", EOS_GetBalance),
        (r"/eos/getaccountinfo", EOS_GetAccountInfo),
        (r"/eos/createrawtransaction", EOS_CreateRawTransaction),
        (r"/eos/sendrawtransaction", EOS_SendRawtransaction),

        ###############################################

        ########### XLM ############################
        (r"/xlm/crawltransactions", XLM_CrawlTxData),
        (r"/xlm/getaccountinfo", XLM_GetAccountInfo),
        (r"/xlm/getbalance", XLM_GetBalance ),
        (r"/xlm/gettransaction", XLM_GetTransactionByHash ),
        (r"/xlm/sendrawtransaction", XLM_SendRawtransaction ),

        ########################################


        ############ TRX ##############################
        (r"/trx/crawltransactions", TRX_CrawlTxData),
        (r"/trx/createrawtransaction", TRX_CreateRawTransaction),
        (r"/trx/sendrawtransaction", TRX_SendRawTransaction),
        (r"/trx/getbalance", TRX_GetBalance),
        (r"/trx/getaccountinfo", TRX_GetAccountInfo),
        (r"/trx/collectionquery", TRX_CollectionQuery),
        ##############################################


        ############ XMR ##############################
        (r"/xmr/crawltransactions", XMR_CrawlTxData),
        (r"/xmr/auto/refresh", XMR_Refresh),
        (r"/xmr/manual/refresh", XMR_Refresh),
        (r"/xmr/auto/exporttxoutputs", XMR_ExportTxOutputs),
        (r"/xmr/manual/exporttxoutputs", XMR_ExportTxOutputs),
        (r"/xmr/auto/importkeyimages", XMR_ImportKeyImages),
        (r"/xmr/manual/importkeyimages", XMR_ImportKeyImages),
        (r"/xmr/auto/createrawtransactions", XMR_CreateRawTransactions),
        (r"/xmr/manual/createrawtransactions", XMR_CreateRawTransactions),
        (r"/xmr/auto/getbalance", XMR_GetBalance),
        (r"/xmr/manual/getbalance", XMR_GetBalance),
        (r"/xmr/auto/getallbalance", XMR_GetAllBalance),
        (r"/xmr/manual/getallbalance", XMR_GetAllBalance),
        (r"/xmr/auto/sendrawtransaction", XMR_SendRawTransaction),
        (r"/xmr/manual/sendrawtransaction", XMR_SendRawTransaction),
        ##########################################

    ], debug = False
    )
    return application


# 格式化日志输出格式
# 默认是这种的: [I 160807 09:27:17 web:1971] 200 GET / (::1) 7.00ms
# 自定义格式: [2020-02-19 09:38:01,892 执行文件名:执行函数名:执行行数 日志等级] 内容消息
# 常用命令代码
# %(name)s Logger的名字
# %(levelno)s 数字形式的日志级别
# %(levelname)s 文本形式的日志级别
# %(pathname)s 调用日志输出函数的模块的完整路径名，可能没有
# %(filename)s 调用日志输出函数的模块的文件名
# %(module)s 调用日志输出函数的模块名
# %(funcName)s 调用日志输出函数的函数名
# %(lineno)d 调用日志输出函数的语句所在的代码行
# %(created)f 当前时间，用UNIX标准的表示时间的浮 点数表示
# %(relativeCreated)d 输出日志信息时的，自Logger创建以 来的毫秒数
# %(asctime)s 字符串形式的当前时间。默认格式是 “2003-07-08 16:49:45,896”。逗号后面的是毫秒
# %(thread)d 线程ID。可能没有
# %(threadName)s 线程名。可能没有
# %(process)d 进程ID。可能没有
# %(message)s用户输出的消息
class LogFormatter(tornado.log.LogFormatter):
    def __init__(self):
        super(LogFormatter, self).__init__(
            # fmt='%(color)s[%(asctime)s %(filename)s:%(funcName)s:%(lineno)d %(levelname)s]%(end_color)s %(message)s',
            # fmt='%(color)s[%(asctime)s | %(pathname)s | PID %(process)d |func %(funcName)s | line %(lineno)d | %(levelname)s]%(end_color)s %(message)s',
            # fmt='%(color)s[%(asctime)s %(module)s :%(funcName)s:%(lineno)d %(levelname)s]%(end_color)s %(message)s',
            # datefmt= None, #'%Y-%m-%d %H:%M:%S',
            fmt='%(color)s[%(asctime)s |  %(process)d  |  %(levelname)s | %(pathname)s |%(funcName)s:%(lineno)d ]%(end_color)s %(message)s',
            datefmt=""  #设为空, 显示出毫秒
        )

def main():

    tornado.options.define("port", default="9000", help="the port to listen", type=int)

    tornado.options.parse_command_line()  # 启动应用前面的设置项目
    [i.setFormatter(LogFormatter()) for i in logging.getLogger().handlers]

    app = make_app()

    # sslop={
    #        "certfile": os.path.join(os.path.abspath("."), "server.crt"),
    #        "keyfile": os.path.join(os.path.abspath("."), "server.key"),
    # }
    #
    # http_server = tornado.httpserver.HTTPServer(app, decompress_request=True, ssl_options=sslop, no_keep_alive=True)

    http_server = tornado.httpserver.HTTPServer(app, decompress_request=True, no_keep_alive=True)
    http_server.listen( tornado.options.options.port)
    sysstr = platform.system()

    logging.info('tornado listening on port {}...'.format(tornado.options.options.port))
    if (sysstr == "Windows"):
        http_server.start(1)  #使用单进程
    else:
        http_server.start(0)  #使用多进程
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
