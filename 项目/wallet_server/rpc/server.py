#coding:utf8
import tornado.ioloop
import tornado.web
import tornado.httpserver
from base_handler import BaseHandler

from btc.handler import BTC_GetAccount,BTC_GetAccountAddress
from btc.handler import BTC_GetBalance, BTC_GetAccountBalance, BTC_ListAccounts
from btc.handler import BTC_ListUTXO, BTC_CreateRawTransaction,  BTC_SendRawTransaction
from btc.handler import BTC_GetRawTransaction, BTC_ListTransActions, BTC_CrawlTxData
from btc.handler import BTC_CreateRawTransactionEx

from usdt.handler import uBTC_GetBalance, uBTC_ListUTXO, uBTC_ListAccounts, OMNI_GetBalance 
from usdt.handler import OMNI_CreateRawTransaction, uBTC_CreateRawTransaction,  uBTC_SendRawTransaction
from usdt.handler import OMNI_ListTransActions, OMNI_CrawlTxData

from eth.handler import ETH_ListAccounts,ETH_GetBalance
from eth.handler import  ETH_SendRawTransaction
from eth.handler import ETH_CrawlTxData, ETH_GetTransactionCount
from eth.handler import ETH_GetBlockByNumber
from eth.handler import ETH_BlockNumber


from usdp.handler import  USDP_GetBalance,  USDP_SendRawTransaction 
from usdp.handler import  USDP_CrawlTxData, USDP_GetAccountInfo


from htdf.handler import USDP_ListAccounts as HTDF_ListAccounts 
from htdf.handler import USDP_GetBalance as HTDF_GetBalance 
from htdf.handler import USDP_SendRawTransaction as HTDF_SendRawTransaction 
from htdf.handler import USDP_GetLatestBlockNumber as HTDF_GetLatestBlockNumber 
from htdf.handler import  USDP_CrawlTxData as  HTDF_CrawlTxData 
from htdf.handler import  USDP_GetAccountInfo as HTDF_GetAccountInfo
from htdf.handler import  USDP_GetTransactionFromBlock  as HTDF_GetTransactionFromBlock


class MainHandler(BaseHandler):
    def get(self):
        self.write("bad request.")
    def post(self):
        self.write("bad request.")

def make_app():
    application = tornado.web.Application([
        (r"/", MainHandler),


        ############# BTC #################################
        (r"/btc/getbalance", BTC_GetBalance),
        (r"/btc/getunspents", BTC_ListUTXO),
        (r"/btc/createrawtransaction", BTC_CreateRawTransaction),
        (r"/btc/createrawtransactionex", BTC_CreateRawTransactionEx),
        (r"/btc/sendrawtransaction", BTC_SendRawTransaction),
        (r"/btc/listtransactions", BTC_ListTransActions),
        (r"/btc/getrawtransaction", BTC_GetRawTransaction),
        (r"/btc/crawltransactions", BTC_CrawlTxData),
        (r"/btc/listaccounts", BTC_ListAccounts),
        ###############################################

        ############ USDT ##############################
        (r"/usdt/getunspents", uBTC_ListUTXO),
        (r"/usdt/btc/getbalance", uBTC_GetBalance),
        (r"/usdt/getbalance", OMNI_GetBalance),
        (r"/usdt/btc/listaccounts", uBTC_ListAccounts),
        (r"/usdt/listtransactions", OMNI_ListTransActions),
        (r"/usdt/crawltransactions", OMNI_CrawlTxData),
        (r"/usdt/createrawtransaction", OMNI_CreateRawTransaction),
        (r"/usdt/btc/createrawtransaction", uBTC_CreateRawTransaction),
        (r"/usdt/sendrawtransaction", uBTC_SendRawTransaction),
        #####################################################

        ############ ETH ####################################
        (r"/eth/getbalance", ETH_GetBalance),
        (r"/eth/sendrawtransaction", ETH_SendRawTransaction),
        (r"/eth/crawltransactions", ETH_CrawlTxData),
        (r"/eth/gettransactioncount", ETH_GetTransactionCount),
        (r"/eth/getblockbynumber", ETH_GetBlockByNumber),
        (r"/eth/blocknumber", ETH_BlockNumber),
        ####################################################

        #######USDP #################
        (r"/usdp/getbalance", USDP_GetBalance),
        (r"/usdp/sendrawtransaction", USDP_SendRawTransaction),
        (r"/usdp/crawltransactions", USDP_CrawlTxData),
        (r"/usdp/getaccountinfo", USDP_GetAccountInfo),
        ############################

        ########HTDF########################
        (r"/htdf/getbalance", HTDF_GetBalance),
        (r"/htdf/sendrawtransaction", HTDF_SendRawTransaction),
        (r"/htdf/crawltransactions", HTDF_CrawlTxData),
        (r"/htdf/getaccountinfo", HTDF_GetAccountInfo),
        ############################

    ], debug = False 
    )
    return application

def main():
    from constants import WALLET_API_PORT
    print('tornado running...')
    app = make_app()
    http_server = tornado.httpserver.HTTPServer(app, decompress_request=True)
    http_server.listen(WALLET_API_PORT)
    http_server.start(1)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
