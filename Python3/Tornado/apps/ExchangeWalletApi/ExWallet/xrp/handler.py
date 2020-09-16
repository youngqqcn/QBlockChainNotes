#author: yqq
#date : 2019-12

import logging
from base_handler import BaseHandler
from utils import decimal_default, get_linenumber
import json
from xrp.ripple_proxy import RippleProxy
# from .proxy import USDPProxy
from constants import  XRP_RIPPLED_PUBLIC_API_URL
from constants import  XRP_RIPPLED_PUBLIC_API_PORT
import sql

from utils import is_hex_str

import decimal
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 30
from utils import RoundDown




class XRP_GetAccountInfo(BaseHandler):
    """
    获取账户信息
    """

    @staticmethod
    def process(address : str):
        api = RippleProxy(host=XRP_RIPPLED_PUBLIC_API_URL, port=XRP_RIPPLED_PUBLIC_API_PORT)
        rsp = api.get_account_info(address=address)
        retinfo = {}
        retinfo['account'] = rsp['account_data']['Account']
        retinfo['sequence'] = rsp['account_data']['Sequence']
        balance =  '%.8f' % RoundDown(Decimal( rsp['account_data']['Balance'] ) / Decimal(10 ** 6))  # 防止假充值
        retinfo['balance'] = balance
        return retinfo

    def post(self):
        try:
            address = self.get_argument("address")
            data = XRP_GetAccountInfo.process(address=address)
            self.write(json.dumps(BaseHandler.success_ret_with_data( data ), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("XRP_GetAccountInfo():", e)

    def get(self):
        self.post()



class  XRP_GetBalance(BaseHandler):

    def post(self):

        try:
            address = self.get_argument("address")
            data = XRP_GetAccountInfo.process(address=address)
            balance = data['balance']
            self.write(json.dumps(BaseHandler.success_ret_with_data(balance), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("XRP_GetBalance():", e)


    def get(self):
        self.post()


class XRP_Submit(BaseHandler):


    def get_order_from_db(self, order_id):
        import sql
        sqlRet = sql.run("select * from tb_xrp_broadcast where order_id='{0}';".format(order_id))
        if len(sqlRet) == 0: return (False, "", {})
        txid = sqlRet[0]['txid']
        tx_json = json.loads( sqlRet[0]['tx_json'] )
        return (True, txid, tx_json)

    def insert_txid_into_db(self, order_id, txid, tx_json_str):
        import sql
        strSql = """insert into tb_xrp_broadcast(order_id, txid, tx_json) values('{}','{}', '{}');""".format(order_id, txid, tx_json_str)
        logging.info('sql: {}'.format(strSql))
        sqlRet = sql.run(strSql)

    def process(self, order_id, tx_blob):
        api = RippleProxy(host=XRP_RIPPLED_PUBLIC_API_URL, port=XRP_RIPPLED_PUBLIC_API_PORT)
        rsp = api.submit(tx_blob=tx_blob)
        retinfo = {}
        retinfo['order_id'] = order_id
        retinfo['txid'] = rsp['tx_json']['hash']
        retinfo['tx_success'] = True if rsp['engine_result'] == 'tesSUCCESS' else False
        retinfo['req_status'] = True if rsp['status'] == 'success' else False
        retinfo['code'] =  rsp['engine_result_code']   #0:成功   非零: 失败
        retinfo['msg'] = rsp['engine_result_message']  #信息
        retinfo['tx_json'] = rsp['tx_json'] #交易详情


        if retinfo['req_status'] and retinfo['tx_success']  and  0 == retinfo['code']:
            self.insert_txid_into_db(order_id=order_id, txid= retinfo['txid'], tx_json_str= json.dumps( rsp['tx_json']) )

        return retinfo



    def post(self):

        try:
            tx_blob = self.get_argument("data")
            order_id = self.get_argument("orderId")

            #对参数格式进行严格判断, 防止sql注入
            if not str(order_id).isalnum() :
                self.write(json.dumps(BaseHandler.success_ret_with_data("invalid `orderId`"), default=decimal_default))
                pass
            if not is_hex_str(tx_blob) or len(tx_blob) < 32:
                self.write(json.dumps(BaseHandler.success_ret_with_data("invalid `data`"), default=decimal_default))
                return

            is_exist, txid , tx_json = self.get_order_from_db(order_id=order_id)
            if is_exist:
                retinfo = {}
                retinfo['order_id'] = order_id
                retinfo['txid'] = txid
                retinfo['tx_success'] = True
                retinfo['req_status'] = True
                retinfo['code'] = 0  # 0:成功   非零: 失败
                retinfo['msg'] = "warning: This order has already successed. DO NOT proccess withdraw-order repeatedly!"  # 信息
                retinfo['tx_json'] = tx_json # rsp['tx_json']  # 交易详情
                self.write(json.dumps(BaseHandler.success_ret_with_data(retinfo), default=decimal_default))
                return

            data = self.process(order_id, tx_blob=tx_blob)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("XRP_Submit():{}".format( e))


    def get(self):
        self.post()






class XRP_CrawlTxData(BaseHandler):

    def _GetDepositTxDataFromDB(self, starttime, endtime= (1<<64) - 1) -> list:

        try:
            if not (isinstance(starttime, int) and isinstance(endtime, int)):
                logging.error("nBegin or nEnd is not int type.")
                return []

            txRet = []

            # strSql = """SELECT txdata FROM t_eth_charge WHERE  height >= {0} and height <= {1};""".format(nBegin, nEnd)
            strSql = """SELECT * FROM tb_xrp_deposit  WHERE  `timestamp`>={} and `timestamp`<={}; """.format( starttime, endtime)
            logging.info("sql  : {}".format(strSql))

            # print(strSql)
            sqlRet = sql.run(strSql)
            # print(sqlRet)

            if not isinstance(sqlRet, list):
                return []

            for item in sqlRet:
                tx = {}
                tx['currency'] = 'XRP'
                tx["txid"] = item['txid']
                tx["from"] = item["src_addr"]
                tx["to"] = item["dst_addr"] + '_' + item['destination_tag']  #由地址和tag拼接
                tx['source_tag'] = item['source_tag']
                tx['destination_tag'] = item['destination_tag']
                tx["sequence"] = item['sequence']
                tx["blocktime"] = item['timestamp']
                tx["confirmations"] = item['confirmations']
                tx["ledger_index"] = item['ledger_index']
                tx["value"] = item['delivered_amount']


                txRet.append(tx)
            return txRet
        except Exception as e:
            logging.error("GetTxDataInfoDB(nBegin, nEnd): {}".format( e))
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
            logging.error("XRP_CrawlTxData error:{0} in {1}".format(e, get_linenumber()))
        pass

    def get(self):
        self.post()


class XRP_GetTransactionByHash(BaseHandler):


    def process(self, txhash : str) -> dict:

        api = RippleProxy(host=XRP_RIPPLED_PUBLIC_API_URL, port=XRP_RIPPLED_PUBLIC_API_PORT)
        rsp = api.get_transaction_by_hash(tx_hash=txhash)
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
            logging.error("XRP_GetTransactionByHash error:{0} in {1}".format(e, get_linenumber()))
            pass



    def get(self):
        self.post()

