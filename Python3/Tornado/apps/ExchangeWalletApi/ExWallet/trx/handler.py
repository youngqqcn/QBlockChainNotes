#!coding:utf8

#author:yqq
#date:2020/2/20 0020 17:29
#description:  TRX   接口



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

from tronapi import Tron
from tronapi.trx import  Trx
import logging
from pprint import pprint
import hashlib
from binascii import unhexlify, hexlify

TRON_RPC_URL = 'https://api.trongrid.io'



class  TRX_SendRawTransaction(BaseHandler):

    def get_order_from_db(self, order_id):
        import sql
        sqlRet = sql.run("select * from tb_trx_broadcast where order_id='{0}';".format(order_id))
        if len(sqlRet) == 0: return (False, "", {})
        txid = sqlRet[0]['txid']
        tx_json = json.loads( sqlRet[0]['tx_json'] )
        return (True, txid, tx_json)

    def insert_txid_into_db(self, order_id, txid, tx_json_str):
        import sql
        strSql = """insert into tb_trx_broadcast(order_id, txid, tx_json) values('{}','{}', '{}');""".format(order_id, txid, tx_json_str)
        logging.info('sql: {}'.format(strSql))
        sqlRet = sql.run(strSql)

    def post(self):


        trx = Trx( Tron(full_node=TRON_RPC_URL, solidity_node=TRON_RPC_URL, event_server=TRON_RPC_URL) )

        try:
            signed_trx = self.get_argument_from_json("data")
            order_id = self.get_argument_from_json("orderId")

            is_exist, txid, tx_json = self.get_order_from_db(order_id)
            if is_exist:
                self.write(json.dumps(BaseHandler.success_ret_with_data(tx_json), default=decimal_default))
                return

            signed_trx_jsonobj = json.loads(signed_trx)
            ret  =  trx.broadcast(signed_trx_jsonobj)

            if 'result' in ret and ret['result'] == True:
                self.write(json.dumps(BaseHandler.success_ret_with_data(ret), default=decimal_default))

                #如果广播成功, 则插入数据库
                if ret['result'] == True:
                    self.insert_txid_into_db(order_id=order_id, txid=ret['transaction']['txID'], tx_json_str=json.dumps(ret))
            else:
                errmsg = json.dumps(ret)
                self.write(json.dumps(BaseHandler.error_ret_with_data(errmsg)))


        except Exception as e:
            logging.error("TRX_SendRawTransaction: {}".format(e))
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))

        pass

    def get(self):
        self.post()
        pass



class  TRX_CreateRawTransaction(BaseHandler):


    @staticmethod
    def my_encode_int64(num: int) -> str:
        """
        将 int64 按照  protobuf 的编码方式编码
        :param num: 输入的  int64
        :return: 编码后的十六进制字符串
        """


        # num = 1583290890000
        assert num > 0

        # 原码字符
        raw = bin(num)[2:]
        logging.info(f"原码: {raw}")

        # 补码, 因为只处理正数, 所以 补码和原码相同
        complement = raw
        logging.info(f'补码: {complement}')

        # 如果长度不是7的倍数, 则补0凑齐
        tmp_complement = complement
        if len(complement) % 7 != 0:
            tmp_complement = '0' * (7 - (len(complement) % 7)) + complement

        logging.info(f'补0后的补码: {tmp_complement}')

        # 7位组 , 正序
        seven_bit_array = []
        i = len(tmp_complement) - 1
        tmp = ''
        while i >= 0:
            tmp = tmp_complement[i] + tmp
            if i % 7 == 0:
                seven_bit_array.append(tmp)
                tmp = ''
            i -= 1

        logging.info(f'正序7位组: { seven_bit_array[::-1] }')
        logging.info(f'反序后7位组: {seven_bit_array}')

        # 加上 MSB, 标识位
        added_msb_seven_bit_array = []
        for i in range(0, len(seven_bit_array)):

            # 如果是最后一个7位组, 则 MSB标识位是 0,  否则 MSB标识位是 1
            if i == len(seven_bit_array) - 1:
                added_msb_seven_bit_array.append('0' + seven_bit_array[i])
            else:
                added_msb_seven_bit_array.append('1' + seven_bit_array[i])

        logging.info(f'加上MSB标识位的7位组: {added_msb_seven_bit_array}')

        # 最终的 二进制字符串形式
        binstr = ''.join(added_msb_seven_bit_array)
        logging.info(f'最终二进制形式:{binstr}')

        # 十六进制字符串形式
        hexstr = hex(int(binstr, 2))
        logging.info(f'十六进制字符串形式: {hexstr}')

        return hexstr[2:]


    def modify_expiration(self, tx : dict):
        """
        改变 tx['raw_data']['expiration']
        同时也要修改   raw_data_hex , 和  txID

        :param tx:  (引用传入)传入传出参数
        :return:
        """

        old_expiration_hex = TRX_CreateRawTransaction.my_encode_int64(tx['raw_data']['expiration'])

        # 改变 raw_data.expiration,  增加一个小时
        tx['raw_data']['expiration'] += 3600 * 1000

        new_expiration_hex = TRX_CreateRawTransaction.my_encode_int64(tx['raw_data']['expiration'])

        # 也要改变  raw_data_hex 中相应的字段
        raw_data_hex = str(tx['raw_data_hex'])

        new_raw_data_hex = raw_data_hex.replace(old_expiration_hex, new_expiration_hex)

        # old_txid = hashlib.sha256(unhexlify(tx['raw_data_hex'])).hexdigest()

        new_txid = hashlib.sha256(unhexlify(new_raw_data_hex)).hexdigest()

        # if old_txid == tx['txID']:
            # logger.info('txid 比对成功!')
            # pass
        # else:
        #     pass
        #     logger.info('txid比对失败!')

        tx['txID'] = new_txid

        pass



    def post(self):
        try:

            trx = Trx(Tron(full_node=TRON_RPC_URL, solidity_node=TRON_RPC_URL, event_server=TRON_RPC_URL))

            src_acct = self.get_argument("src_acct")
            dst_acct = self.get_argument("dst_acct")
            stramount = self.get_argument("amount")

            src_acct = src_acct.strip()
            dst_acct = dst_acct.strip()
            stramount = stramount.strip()


            if len(src_acct) != 34 or (not str(src_acct).startswith('T') ):
                raise Exception("invalid src address")

            if len(dst_acct) != 34 or (not str(dst_acct).startswith('T') ):
                raise Exception("invalid dst address")

            amount = float(stramount)


            tx = trx.tron.transaction_builder.send_transaction(
                to=dst_acct,
                amount= amount,
                account=src_acct
            )

            self.modify_expiration(tx)

            tx['signature'] = ['this_is_placeholder_for_signature']

            rsp_data = {
                'raw_trx_json_str' : json.dumps(tx),
                'digest' : tx['txID']
            }

            logging.info(f'{rsp_data}')

            self.write(json.dumps(BaseHandler.success_ret_with_data(rsp_data), default=decimal_default))

            pass
        except Exception as e:
            logging.error("TRX_CreateRawTransaction: {}".format(e))
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))

        pass

    def get(self):
        self.post()





class TRX_CrawlTxData(BaseHandler):

    def _GetDepositTxDataFromDB(self, startblock, endblock = (1<<64) - 1) -> list:

        try:
            if not (isinstance(startblock, int) and isinstance(endblock, int)):
                logging.error("nBegin or nEnd is not int type.")
                return []

            txRet = []

            startblock = startblock - 100 if startblock > 100 else  0

            strSql = """SELECT * FROM tb_trx_deposit  WHERE  `block_number`>={} and `block_number`<={}; """.format( startblock, endblock)
            logging.info("sql  : {}".format(strSql))

            # print(strSql)
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
                tx["blocktime"] = item['timestamp']
                tx['blockNumber'] = item['block_number']
                tx["confirmations"] = item['confirmations']
                tx["value"] = item['amount']


                txRet.append(tx)
            return txRet
        except Exception as e:
            logging.error("GetTxDataInfoDB(nBegin, nEnd): {}".format( e))
            return []


    def post(self):
        try:
            startblock = int(self.get_argument("blknumber"))  # 防止sql注入
            if not str(startblock).isnumeric():
                errmsg = "invalid `startblock`"
                self.write(json.dumps(BaseHandler.success_ret_with_data(errmsg), default=decimal_default))
                return

            data = self._GetDepositTxDataFromDB(startblock)
            self.write(json.dumps(BaseHandler.success_ret_with_data(data), default=decimal_default))
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("error:{0} in {1}".format(e, get_linenumber()))
        pass


    def get(self):
        self.post()



class  TRX_GetAccountInfo(BaseHandler):

    def post(self):

        try:

            address = self.get_argument("address")

            if len(address) != 34 or (not str(address).startswith('T') ):
                raise Exception("invalid address")



            trx = Trx(Tron(full_node=TRON_RPC_URL, solidity_node=TRON_RPC_URL, event_server=TRON_RPC_URL))

            account_info  = trx.get_account(address=address)

            if 'balance' in account_info:
                decBalance = Decimal(account_info['balance']) / Decimal('1000000')
                fmtBalance = decBalance.quantize(Decimal("0.000000"), getattr(decimal, 'ROUND_DOWN'))
            else:
                fmtBalance = '0.000000'

            is_active = 'create_time' in account_info  #账户是否已经激活

            rsp_data = {
                'address' : address,
                'balance' : str(fmtBalance),
                'active'  :  is_active
                #其他代币资产信息可以根据资产id进行获取, 如TRC20-USDT , 此是后话
            }

            logging.info(f'{rsp_data}')

            self.write(json.dumps(BaseHandler.success_ret_with_data(rsp_data), default=decimal_default))

            pass
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("error:{0} in {1}".format(e, get_linenumber()))

    def get(self):
        self.post()
        pass


class  TRX_GetBalance(BaseHandler):

    def post(self):

        try:

            address = self.get_argument("address")


            if len(address) != 34 or (not str(address).startswith('T') ):
                raise Exception("invalid address")

            trx = Trx(Tron(full_node=TRON_RPC_URL, solidity_node=TRON_RPC_URL, event_server=TRON_RPC_URL))

            account_info  = trx.get_account(address=address)

            if 'balance' in account_info:
                decBalance = Decimal(account_info['balance']) / Decimal('1000000')
                fmtBalance = str( decBalance.quantize(Decimal("0.000000"), getattr(decimal, 'ROUND_DOWN')) )
            else:
                fmtBalance = '0.000000'


            self.write(json.dumps(BaseHandler.success_ret_with_data(fmtBalance), default=decimal_default))

            pass
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error("error:{0} in {1}".format(e, get_linenumber()))

    def get(self):
        self.post()
        pass



class TRX_CollectionQuery(BaseHandler):





    def process(self, symbol : str = 'TRX') -> list:

        #每次只查部分地址, 以防http超时
        strSql = f"""SELECT  address FROM tb_trx_active_addrs WHERE `symbol`='{symbol}' AND `balance` >= 1 ORDER BY `balance` DESC LIMIT 25;"""
        sqlRet = sql.run(strSql)



        addrs = []
        for item in sqlRet:
            if "address" in item:
                if item['address'] not in addrs: addrs.append(item["address"])

        trx = Trx(Tron(full_node=TRON_RPC_URL, solidity_node=TRON_RPC_URL, event_server=TRON_RPC_URL))


        retList = []

        for addr in addrs:
            account_info = trx.get_account(address=addr)
            if 'balance' in account_info:
                decBalance = Decimal(account_info['balance']) / Decimal('1000000')
                fmtBalance = decBalance.quantize(Decimal("0.000000"), getattr(decimal, 'ROUND_DOWN'))
            else:
                fmtBalance = '0.000000'

            if Decimal(fmtBalance) < Decimal( '1.0' ):
                logging.info(f"{addr}'s balance({fmtBalance}) is less than 1.0TRX,  skip it.")
                continue

            retList.append({'address': addr, 'balance': str(fmtBalance) , 'symbol' : symbol})

        return retList


    def post(self):
        try:
            # symbol = self.get_argument('symbol')
            # if str(symbol) not in ['TRX', 'TRC20-USDT']:
            #     raise Exception("invalid symbol")

            retdata = self.process(symbol='TRX')
            self.write(json.dumps(BaseHandler.success_ret_with_data(retdata), default=decimal_default))
            pass
        except Exception as e:
            self.write(json.dumps(BaseHandler.error_ret_with_data("error: %s" % e)))
            logging.error(" TRX_CollectionQuery error:{0} in {1}".format(e, get_linenumber()))

    def get(self):
        self.post()



