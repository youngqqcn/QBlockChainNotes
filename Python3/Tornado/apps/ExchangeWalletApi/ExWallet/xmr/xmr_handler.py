#!coding:utf8

#author:yqq
#date:2020/3/26 0026 14:26
#description:



import logging
from base_handler import BaseHandler
from utils import decimal_default, get_linenumber
import json
import sql

from utils import is_hex_str
import decimal
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 30
from utils import RoundDown



import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


from xmr.xmr_proxy import XMR_Proxy

from constants import XMR_RPC_HTTPS_ENABLE, XMR_WALLET_RPC_HOST, XMR_WALLET_RPC_PORT_MANUAL, XMR_WALLET_RPC_PORT_AUTO
from constants import  XMR_PRIV_VIEW_KEY  , XMR_MASTER_ADDR

XMR_RPC_PROTOCOL = 'https' if XMR_RPC_HTTPS_ENABLE else 'http'




#WalletRPC       cold/hot wallet     Handler
#---------------------------------------------------------
#getbalance           hot            TODO : 似乎并不能获取真正的余额
#refresh              hot            XMR_Refresh
#export_outputs       hot            XMR_ExportTxOutputs
#import_outputs       cold
#export_key_images    cold
#import_key_image     hot            XMR_ImportKeyImages
#transfer             hot            XMR_CreateRawTransaction
#sign_transfer        cold
#submit_transfer      hot            XMR_SendRawTransaction



class XMR_Refresh(BaseHandler):
    """
    刷新
    """
    def post(self):
        try:
            port = XMR_WALLET_RPC_PORT_MANUAL if 'manual' in self.request.uri else  XMR_WALLET_RPC_PORT_AUTO

            rpc = XMR_Proxy(
                protocol= XMR_RPC_PROTOCOL,
                host=XMR_WALLET_RPC_HOST,
                port=port,
                verify_ssl_certs=False
            )

            retdata = rpc.refresh()
            self.write(json.dumps(BaseHandler.success_ret_with_data(retdata), default=decimal_default))
            pass
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("XMR_Refresh error:{0} in {1}".format(e, get_linenumber()))
        pass

    def get(self):
        self.post()


class  XMR_GetBalance(BaseHandler):
    """
    TODO: 这个接口并不能获取可用余额, 必须导入导入签名后的key_images才能看到
    """

    def post(self):
        try:
            port = XMR_WALLET_RPC_PORT_MANUAL if 'manual' in self.request.uri else XMR_WALLET_RPC_PORT_AUTO
            rpc = XMR_Proxy(
                protocol=XMR_RPC_PROTOCOL,
                host=XMR_WALLET_RPC_HOST,
                port=port,
                verify_ssl_certs=False
            )

            balance = rpc.balances()

            retdata =  str( balance['balance'] ) #包括 unlocked_balance

            self.write(json.dumps(BaseHandler.success_ret_with_data(retdata), default=decimal_default))
            pass
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("XMR_GetBalance error:{0} in {1}".format(e, get_linenumber()))
        pass

    def get(self):
        self.post()


class  XMR_GetAllBalance(BaseHandler):
    """
    TODO: 这个接口并不能获取可用余额, 必须导入导入签名后的key_images才能看到
    """

    def post(self):
        try:
            port = XMR_WALLET_RPC_PORT_MANUAL if 'manual' in self.request.uri else XMR_WALLET_RPC_PORT_AUTO

            rpc = XMR_Proxy(
                protocol=XMR_RPC_PROTOCOL,
                host=XMR_WALLET_RPC_HOST,
                port=port,
                verify_ssl_certs=False
            )

            balance = rpc.balances()

            retdata =   balance #str(balance)

            self.write(json.dumps(BaseHandler.success_ret_with_data(retdata), default=decimal_default))
            pass
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("XMR_GetBalance error:{0} in {1}".format(e, get_linenumber()))
        pass

    def get(self):
        self.post()



class XMR_ExportTxOutputs(BaseHandler):
    """
    导出交易输出
    """
    def post(self):
        try:
            port = XMR_WALLET_RPC_PORT_MANUAL if 'manual' in self.request.uri else XMR_WALLET_RPC_PORT_AUTO

            rpc = XMR_Proxy(
                protocol=XMR_RPC_PROTOCOL,
                host=XMR_WALLET_RPC_HOST,
                port=port,
                verify_ssl_certs=False
            )

            #刷新
            rpc.refresh()

            retdata = rpc.export_outputs() #rpc.raw_request('export_outputs')
            logging.info(f'outputs: {retdata}')
            self.write(json.dumps(BaseHandler.success_ret_with_data(retdata), default=decimal_default))
            pass
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("XMR_ExportTxOutputs error:{0} in {1}".format(e, get_linenumber()))
        pass

    def get(self):
        self.post()


class XMR_ImportKeyImages(BaseHandler):
    """
    导入 key_image   钱包才能确定那些 TXO 是花费过的  那些是没花费过的
    """
    def post(self):
        try:

            port = XMR_WALLET_RPC_PORT_MANUAL if 'manual' in self.request.uri else XMR_WALLET_RPC_PORT_AUTO

            key_images = self.get_argument_from_json('signed_key_images')

            rpc = XMR_Proxy(
                protocol=XMR_RPC_PROTOCOL,
                host=XMR_WALLET_RPC_HOST,
                port=port,
                verify_ssl_certs=False
            )

            rsp = rpc.import_key_images(key_images=key_images)

            #获取可用余额
            balances = rpc.balances()
            retdata = dict( rsp , **balances)

            self.write(json.dumps(BaseHandler.success_ret_with_data(retdata), default=decimal_default))
            pass
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("XMR_ImportKeyImages error:{0} in {1}".format(e, get_linenumber()))
        pass

    def get(self):
        self.post()




class XMR_CreateRawTransactions(BaseHandler):
    """
    创建交易, 可以有多个接收者
    """
    def post(self):
        try:
            dsts = self.get_argument_from_json('destinations')
            assert  isinstance( dsts , list) , "destinations must be list, eg:[{'address':'addr', 'amount':0.123}]]"

            port = XMR_WALLET_RPC_PORT_MANUAL if 'manual' in self.request.uri else XMR_WALLET_RPC_PORT_AUTO

            rpc = XMR_Proxy(
                protocol=XMR_RPC_PROTOCOL,
                host=XMR_WALLET_RPC_HOST,
                port=port,
                verify_ssl_certs=False
            )

            rawtxs = rpc.transfer(destinations= dsts)
            assert isinstance(rawtxs, dict), 'rawtxs is not dict'

            retdata = rawtxs
            logging.info(f'retdata: {retdata}')
            self.write(json.dumps(BaseHandler.success_ret_with_data(retdata), default=decimal_default))
            pass
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("XMR_CreateRawTransaction error:{0} in {1}".format(str(e), get_linenumber()))
        pass

    def get(self):
        self.post()


class XMR_SendRawTransaction(BaseHandler):
    """
    广播交易
    """
    def post(self):
        try:
            signed_tx_hex = self.get_argument_from_json('signed_tx_hex')

            port = XMR_WALLET_RPC_PORT_MANUAL if 'manual' in self.request.uri else XMR_WALLET_RPC_PORT_AUTO

            rpc = XMR_Proxy(
                protocol=XMR_RPC_PROTOCOL,
                host=XMR_WALLET_RPC_HOST,
                port=port,
                verify_ssl_certs=False
            )

            retdata = rpc.submit_transfer(signed_tx_hex=signed_tx_hex)
            logging.info(f'submit_transfer response: {retdata}')
            self.write(json.dumps(BaseHandler.success_ret_with_data(retdata), default=decimal_default))
            pass
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("XMR_SendRawTransaction error:{0} in {1}".format(e, get_linenumber()))
        pass

    def get(self):
        self.post()





class XMR_CrawlTxData(BaseHandler):

    def _get_deposit_txs_from_db(self, startblk, endblk= (1<<64) - 1) -> list:

        try:

            assert isinstance(startblk, int) and isinstance(endblk, int)  , 'startblk or endblk type error'

            rettxs = []
            strsql = f"""SELECT * FROM tb_xmr_deposit  WHERE  `block_number`>={startblk} and `block_number`<={endblk}; """
            logging.info("sql  : {}".format(strsql))
            res = sql.run(strsql)

            if not isinstance(res, list):
                return []

            for item in res:
                tx = {}
                tx['symbol'] = 'XMR'
                tx["txid"] = item['txid']
                tx["to"] = item["dst_addr"]
                tx["value"] = item['amount']
                tx["from"] = 'unknown' #item["src_addr"]
                tx['blockNumber'] = item['block_number']
                tx["blocktime"] = item['timestamp']
                tx["confirmations"] = item['confirmations']

                #增加view key 用于后期验证交易用
                tx['viewkey'] = XMR_PRIV_VIEW_KEY

                rettxs.append(tx)

            return rettxs
        except Exception as e:
            logging.error("_get_deposit_txs_from_db(nBegin, nEnd): {}".format( e))
            return []


    def post(self):
        try:
            blocknum = self.get_argument("blknumber")
            assert  str(blocknum).isalnum() , "invalid `blknumber`"

            nblocknum = int(self.get_argument("blknumber"))
            nblocknum  = nblocknum - 100 if nblocknum > 10000 else 0

            data = self._get_deposit_txs_from_db(startblk=nblocknum)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("XMR_CrawlTxData error:{0} in {1}".format(e, get_linenumber()))
        pass

    def get(self):
        self.post()





