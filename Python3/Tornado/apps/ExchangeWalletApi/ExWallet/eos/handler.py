#!coding:utf8

#author:yqq
#date:2019/12/26 0026 17:28
#description: EOS 相关的handler


import logging
import eospy
import eospy.keys
import pytz
import json
import sql
import  re
from base_handler import BaseHandler
from utils import decimal_default, get_linenumber
from eospy.types import Transaction
from eos.proxy import EosProxy

from constants import EOS_PUBLIC_API_URL

from utils import is_hex_str
import decimal
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 30
from utils import RoundDown

from constants import  HTTP_TIMEOUT_SECS


class EOS_GetBalance(BaseHandler):
    """
    获取账户余额(可用余额, 不包含抵押资产)
    """

    @staticmethod
    def process(account_name : str):
        cleos = EosProxy(url= EOS_PUBLIC_API_URL )
        retdata  = cleos.get_currency_balance(account_name, timeout=HTTP_TIMEOUT_SECS)

        #如果账户的EOS余额为 0 ,  返回的是空数组
        if len(retdata) == 0:
            strbalance = '0.0000'
        else:
            strbalance = str(retdata[0]).replace('EOS', '').replace(' ', '')
        return strbalance

    def post(self):
        try:
            address = self.get_argument("address")

            matches = re.findall(r'^[1-5a-z]{12}$', address)
            if not matches or len(matches) == 0:
                raise  Exception(" address is illegal ")

            data = EOS_GetBalance.process( account_name= address)
            self.write(json.dumps(BaseHandler.success_ret_with_data( data ), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("EOS_GetBalance():{}".format( e))

        pass


    def get(self):
        self.post()


class EOS_GetAccountInfo(BaseHandler):
    """
    获取账户信息
    """

    @staticmethod
    def is_valid_acc_name(account_name : str) -> bool:
        matches = re.findall(r'^[1-5a-z]{12}$', account_name)
        if not matches or len(matches) == 0:
            return False
        return True

    @staticmethod
    def process(account_name : str):
        cleos = EosProxy(url=EOS_PUBLIC_API_URL)
        retdata = cleos.get_account(acct_name=account_name, timeout=HTTP_TIMEOUT_SECS)
        return retdata


    def post(self):
        try:
            address = self.get_argument("address")

            if not EOS_GetAccountInfo.is_valid_acc_name(address):
                raise  Exception(" address is illegal ")

            data = EOS_GetAccountInfo.process( account_name= address)
            self.write(json.dumps(BaseHandler.success_ret_with_data( data ), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("EOS_GetBalance(): {}".format( e))

        pass

    def get(self):
        self.post()


class EOS_CreateRawTransaction(BaseHandler):
    """
    创建交易
    """

    @staticmethod
    def process(str_src_acct : str, str_dst_acct : str , str_amount : str, str_memo : str):
        cleos = EosProxy(url=EOS_PUBLIC_API_URL)

        arguments = {
            "from": str_src_acct, #"yangqingqin1",  # sender
            "to": str_dst_acct ,  #"hetbitesteos",  # receiver
            "quantity": str_amount + ' EOS' , #'0.5023 EOS', 必须为 4位小数, 不能多,不能少 # In EOS
            "memo": str_memo  #"10029432",
        }

        payload = {
            "account": "eosio.token",
            "name": "transfer",
            "authorization": [{
                "actor": str_src_acct,  #"yangqingqin1",
                "permission": "active",
            }],
        }

        # Converting payload to binary
        data = cleos.abi_json_to_bin(payload['account'], payload['name'], arguments, timeout=HTTP_TIMEOUT_SECS)
        # Inserting payload binary form as "data" field in original payload
        payload['data'] = data['binargs']
        # final transaction formed
        trx = {"actions": [payload]}
        import datetime as dt
        # trx['expiration'] = str((dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))
        trx['expiration'] = str((dt.datetime.utcnow() + dt.timedelta(seconds=60 * 60)).replace(tzinfo=pytz.UTC))

        # print(json.dumps(trx))

        # key = eospy.keys.EOSKey('5JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw')

        # resp = ce.push_transaction(trx, key, broadcast=False)
        # print(resp)

        chain_info, lib_info = cleos.get_chain_lib_info(timeout=HTTP_TIMEOUT_SECS)
        rawtx = Transaction(trx, chain_info, lib_info)
        encoded = rawtx.encode()
        # print("encode: {}".format(encoded))
        from eospy.utils import sig_digest
        digest = sig_digest(rawtx.encode(), chain_info['chain_id'])
        # print("digest: {}".format(digest))


        from eospy.types import EOSEncoder
        final_trx = {
            'compression': 'none',
            'transaction': rawtx.__dict__,
            'signatures': [],
        }

        retdata = {
            'raw_trx_json_str' : json.dumps(final_trx, cls=EOSEncoder),
            'digest' : digest
        }

        return  retdata



    def post(self):
        try:
            src_acct = self.get_argument("src_acct")
            dst_acct = self.get_argument("dst_acct")
            stramount = self.get_argument("amount")
            strmemo = self.get_argument("memo")

            src_acct = src_acct.strip()
            dst_acct = dst_acct.strip()
            stramount = stramount.strip()
            strmemo = strmemo.strip()

            if not EOS_GetAccountInfo.is_valid_acc_name(src_acct) \
                    or not EOS_GetAccountInfo.is_valid_acc_name(dst_acct):
                raise Exception(" src_acct or dst_acct is illegal ")

            if not isinstance(stramount, str) or Decimal(stramount) < Decimal('0.0001'):
                raise Exception(" amount is illegal ")

            if len(strmemo) > 20:
                raise Exception(" memo is too long")

            #直接截断,  不能使用  '%.4f' % Decimal('xxxx.xxxxxxx') , 因为会四舍五入
            decmlfmtamount = Decimal(stramount).quantize(Decimal("0.0000"), getattr(decimal, 'ROUND_DOWN'))
            strfmtamount = str(decmlfmtamount)


            data = EOS_CreateRawTransaction.process(src_acct, dst_acct, strfmtamount, strmemo)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))

        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("EOS_CreateRawTransaction():{}".format(e))
        pass

    def get(self):
        self.post()


class EOS_SendRawtransaction(BaseHandler):
    """
    广播交易
    """

    def get_order_from_db(self, order_id):
        import sql
        sqlRet = sql.run("select * from tb_eos_broadcast where order_id='{0}';".format(order_id))
        if len(sqlRet) == 0: return (False, "", {})
        txid = sqlRet[0]['txid']
        tx_json = json.loads( sqlRet[0]['tx_json'] )
        return (True, txid, tx_json)

    def insert_txid_into_db(self, order_id, txid, tx_json_str):
        import sql
        strSql = """insert into tb_eos_broadcast(order_id, txid, tx_json) values('{}','{}', '{}');""".format(order_id, txid, tx_json_str)
        logging.info('sql: {}'.format(strSql))
        sqlRet = sql.run(strSql)



    def post(self):
        try:
            cleos = EosProxy(url=EOS_PUBLIC_API_URL)

            signed_trx = self.get_argument_from_json("data")
            order_id = self.get_argument_from_json("orderId")

            is_exist, txid, tx_json = self.get_order_from_db(order_id)
            if is_exist:
                self.write(json.dumps(BaseHandler.success_ret_with_data(tx_json), default=decimal_default))
                return

            #如果没有广播过, 则进行广播
            data = cleos.sendrawtransaction(data=signed_trx, timeout=HTTP_TIMEOUT_SECS)

            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))

            #如果广播成功, 则写入数据库
            if data['processed']['error_code'] == None and data['processed']['except'] == None \
                and data['processed']['receipt']['status'] == 'executed':
                self.insert_txid_into_db(order_id=order_id, txid= data['transaction_id'], tx_json_str=json.dumps(data) )

        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("EOS_CreateRawTransaction():{}".format( e))

        pass

    def get(self):
        self.post()





class EOS_CrawlTxData(BaseHandler):


    def _GetTxDataFromDB(self, n_start_block_num : int, symbol='EOS' ):

        strsql = """SELECT * FROM tb_eos_deposit  WHERE symbol='{}' and block_number>={} LIMIT 100;"""\
                    .format(symbol, n_start_block_num)
        logging.info("sql  : {}".format(strsql))

        sqlret = sql.run(strsql)

        if not isinstance(sqlret, list):
            return  []

        ret_trxs = []
        for trx in sqlret:
            tx = {}
            tx['symbol'] = symbol
            tx['txid'] = trx['txid']
            tx['from'] = trx['src_account']
            tx['to'] = trx['dst_account']
            tx['value'] = trx['amount']
            tx['memo'] = trx['memo']
            tx['confirmations'] = trx['confirmations']
            tx['blockNumber'] = trx['block_number']
            tx['blocktime'] = trx['timestamp']

            ret_trxs.append( tx )

        return ret_trxs


    def post(self):

        try:
            n_block_start  = int(self.get_argument("blknumber"))
            data = self._GetTxDataFromDB(n_block_start)
            logging.info('data : {}'.format(data))
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s"%e)))
            logging.error("EOS_CrawlTxData error:{0} in {1}".format(e,get_linenumber()))

        pass


    def get(self):
        self.post()



#TODO: 增加判断 EOS资源的接口, 判断资源是否能够满足交易需求;
#TODO: 如果资源不满足交易需求, 会出现什么问题?