#!coding:utf8

#author:yqq
#date:2020/2/7 0007 14:03
#description:  XLM接口


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
from pprint import  pprint


from .proxy import XLMProxy

from constants import XLM_RPC_HOST
from .proxy import NotFoundError




class XLM_GetAccountInfo(BaseHandler):

    @classmethod
    def process(cls, address : str) -> dict:

        # server = Server("https://horizon-testnet.stellar.org")
        # public_key = "GDTIZ3P6L33OZE3B437ZPX5KAS7APTGUMUTS34TXX6Z5BHD7IAABZDJZ"
        # account = server.accounts().account_id(public_key).call()

        api = XLMProxy(rpc_host_url=XLM_RPC_HOST)
        try:
            rsp = api.get_account_info(straccount=address)
        except NotFoundError:
            return {
                'balance': '0.0000000',
                'sequence': '0',
                'account': address,
                'active': False
            }


        balance = '0.0000000'
        for each_balance in rsp['balances']:
            if each_balance['asset_type'] == 'native':
                balance = each_balance['balance']

        sequence = rsp['sequence']

        return  {
            'balance' : balance,
            'sequence' : sequence,
            'account': address,
            'active':True
        }




    def post(self):

        try:
            address = self.get_argument("address")
            if len(address) != 56 :
                raise Exception("invalid address, must be 56 byte")
            data = XLM_GetAccountInfo.process(address=address)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("XLM_GetAccountInfo():", e)

        pass

    def get(self):
        self.post()
        pass


class  XLM_GetBalance(BaseHandler):

    def post(self):

        try:
            address = self.get_argument("address")
            data = XLM_GetAccountInfo.process(address=address)
            balance =  data['balance']
            self.write(json.dumps(BaseHandler.success_ret_with_data(balance), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.info("XLM_GetAccountInfo(): {}".format( e))


    def get(self):
        self.post()



class XLM_GetTransactionByHash(BaseHandler):


    def process(self, txhash : str) -> dict:

        api = XLMProxy(rpc_host_url=XLM_RPC_HOST)
        rsp = api.get_transaction(trx_hash=txhash)
        return rsp



    def post(self):

        try:
            txid = self.get_argument('txid')
            if not is_hex_str(txid):
                errmsg = "invalid `txid`"
                self.write(json.dumps(BaseHandler.success_ret_with_data(errmsg), default=decimal_default))
                return

            data = self.process(txhash=txid)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("XLM_GetTransactionByHash error:{0} in {1}".format(e, get_linenumber()))
            pass



    def get(self):
        self.post()




class XLM_SendRawtransaction(BaseHandler):


    def get_order_from_db(self, order_id):
        import sql
        sqlRet = sql.run("select * from tb_xlm_broadcast where order_id='{0}';".format(order_id))
        if len(sqlRet) == 0: return (False, "")
        txid = sqlRet[0]['txid']
        return (True, txid)

    def insert_txid_into_db(self, order_id, txid):
        import sql
        strSql = """insert into tb_xlm_broadcast(order_id, txid) values('{}','{}');""".format(order_id, txid)
        logging.info('sql: {}'.format(strSql))
        sqlRet = sql.run(strSql)

    def process(self, order_id : str, tx_xdr_blob : str):
        tx_xdr = tx_xdr_blob.replace(' ', '')

        logging.info(f'{tx_xdr_blob}')
        logging.info(f'raw len {len(tx_xdr_blob)} ')
        logging.info(f'replace space len = {len(tx_xdr)}')
        logging.info("tx_xdr: {}".format( tx_xdr))

        api = XLMProxy(rpc_host_url=XLM_RPC_HOST)
        rsp = api.sendrawtrnasaction(tx_xdr_data=tx_xdr, istestnet= ('testnet' in XLM_RPC_HOST))
        # pprint(rsp)
        logging.info("rsp : {}".format(rsp))
        retinfo = {}
        retinfo['order_id'] = order_id
        retinfo['txid'] = rsp['hash']
        retinfo['msg'] = 'success' #信息

        self.insert_txid_into_db(order_id=order_id, txid= retinfo['txid'])

        return retinfo



    def post(self):

        try:

            tx_blob = self.get_argument_from_json("data")
            order_id = self.get_argument_from_json("orderId")


            #对参数格式进行严格判断, 防止sql注入
            if not str(order_id).isalnum() :
                self.write(json.dumps(BaseHandler.success_ret_with_data("invalid `orderId`"), default=decimal_default))
                pass
            if not is_hex_str(tx_blob) or len(tx_blob) < 32:
                self.write(json.dumps(BaseHandler.success_ret_with_data("invalid `data`"), default=decimal_default))
                return

            is_exist, txid = self.get_order_from_db(order_id=order_id)
            if is_exist:
                retinfo = {}
                retinfo['order_id'] = order_id
                retinfo['txid'] = txid
                retinfo['msg'] = "warning: This order has already successed. DO NOT proccess withdraw-order repeatedly!"  # 信息
                self.write(json.dumps(BaseHandler.success_ret_with_data(retinfo), default=decimal_default))
                return

            data = self.process(order_id, tx_xdr_blob=tx_blob)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("XLM_Submit(): {}".format( e))


    def get(self):
        self.post()



class XLM_CrawlTxData(BaseHandler):

    def _GetDepositTxDataFromDB(self, starttime, endtime= (1<<64) - 1) -> list:

        try:
            if not (isinstance(starttime, int) and isinstance(endtime, int)):
                logging.error("nBegin or nEnd is not int type.")
                return []

            txRet = []

            strSql = f"""SELECT * FROM tb_xlm_deposit  WHERE  `timestamp`>={starttime} and `timestamp`<={endtime}; """
            logging.info("sql  : {}".format(strSql))

            # print(strSql)
            sqlRet = sql.run(strSql)
            logging.info(sqlRet)

            if not isinstance(sqlRet, list):
                return []

            for item in sqlRet:
                tx = {}
                tx['symbol'] = item['symbol']
                tx["txid"] = item['txid']
                tx["from"] = item["src_account"]
                tx["to"] = item["dst_account"] + '_' + item['memo']  #由地址和memo拼接, 非法的memo已经在scanner中处理后再存库
                tx['memo'] = item['memo']
                tx["blocktime"] = item['timestamp']
                tx["confirmations"] = item['confirmations']
                tx["value"] = item['amount']


                txRet.append(tx)
            return txRet
        except Exception as e:
            logging.error("GetTxDataInfoDB(nBegin, nEnd):", e)
            return []


    def post(self):
        try:
            starttime = int(self.get_argument("blocktime"))  # 防止sql注入
            if not str(starttime).isalnum():
                errmsg = "invalid `blocktime`"
                self.write(json.dumps(BaseHandler.success_ret_with_data(errmsg), default=decimal_default))
                return

            data = self._GetDepositTxDataFromDB(starttime)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("XLM_CrawlTxData error:{0} in {1}".format(e, get_linenumber()))
        pass

    def get(self):
        self.post()