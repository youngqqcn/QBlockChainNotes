#!coding:utf8

#author:yqq
#date:2020/3/25 0025 15:50
#description:
#


import sys

if sys.version_info < (3, 0):
    print("please use python3")
    raise Exception("please use  python3 !!")

sys.path.append('.')
sys.path.append('..')
import logging

import time
from time import sleep
from datetime import datetime
import sql
from dateutil import parser

import decimal
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 30
from utils import RoundDown
from utils import RoundDown
from pprint import pprint
from utils import  timestamp_parse

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from monero.wallet import Wallet
from monero.wallet import keccak_256
from monero.wallet import ed25519, const, address, base58
from monero.address import BaseAddress, Address, SubAddress
from monero.seed import Seed
from monero.transaction import IncomingPayment, OutgoingPayment, Transaction, PaymentFilter
from monero.backends.jsonrpc import JSONRPCWallet
from binascii import  hexlify, unhexlify
import struct

from pprint import pprint

from config import XMR_RPC_HTTPS_ENABLE, XMR_WALLET_RPC_HOST, XMR_WALLET_RPC_PORT
from config import  XMR_PRIV_VIEW_KEY, XMR_MASTER_ADDR



def get_address_ex(private_view_key : str, master_addr : str, major : int, minor : int ) -> str:
    """
    Calculates sub-address for account index (`major`) and address index within
    the account (`minor`).

    :rtype: :class:`BaseAddress <monero.address.BaseAddress>`
    """
    # ensure indexes are within uint32
    if major < 0 or major >= 2 ** 32:
        raise ValueError('major index {} is outside uint32 range'.format(major))
    if minor < 0 or minor >= 2 ** 32:
        raise ValueError('minor index {} is outside uint32 range'.format(minor))
    master_address = Address(master_addr)  # self.address()
    if major == minor == 0:  # 如果是  (0, 0) 则直接返回
        return str(master_address)

    # spk = Address(master_addr).spend_key() #根据master address 直接获取 public_key
    #  = Address(master_addr).view_key()

    priv_view_key = private_view_key  # seed.secret_view_key()
    # print(f'private_view_key: {priv_view_key}')
    master_svk = unhexlify(priv_view_key)

    pub_spend_key = Address(master_addr).spend_key()
    master_psk = unhexlify(pub_spend_key)

    # m = Hs("SubAddr\0" || master_svk || major || minor)
    hsdata = b''.join([
        b'SubAddr\0', master_svk,
        struct.pack('<I', major), struct.pack('<I', minor)])
    m = keccak_256(hsdata).digest()

    # print(f'subprivate_view_key: { hexlify(m) }')

    # D = master_psk + m * B
    D = ed25519.edwards_add(
        ed25519.decodepoint(master_psk),
        ed25519.scalarmult_B(ed25519.decodeint(m)))

    # print(f'{D}')
    # print(f'public_spend_key: { hexlify(  ed25519.encodepoint(D) ) }')

    # C = master_svk * D
    C = ed25519.scalarmult(D, ed25519.decodeint(master_svk))

    # print(f'public_view_key: { hexlify(  ed25519.encodepoint(C) ) }')

    netbyte = bytearray([const.SUBADDR_NETBYTES[const.NETS.index(master_address.net)]])
    data = netbyte + ed25519.encodepoint(D) + ed25519.encodepoint(C)
    checksum = keccak_256(data).digest()[:4]
    subaddr = address.SubAddress(base58.encode(hexlify(data + checksum)))
    logging.info(f'subaddr : {subaddr}')
    return str(subaddr)



class  JSONRPCWalletEx(JSONRPCWallet):

    #查看 RPC接口的实现发现,  incoming_transfers 内部调用的是 get_transfers
    # 所以直接使用  get_transfers 即可
    #https://web.getmonero.org/zh-cn/resources/developer-guides/wallet-rpc.html#get_transfers
    def get_deposit_txs(self):

        ret_txs = []

        params = {
            'in' : True,
            'pending' : False,
            'failed' : False,
            'pool' : False,
            'filter_by_height': False,  #通过高度过滤, 暂时不通过高度过滤, 后期充币比较多的时候,再根据高度过滤
            # 'min_height' : 0,
            # 'max_height': 0,
            'account_index': 0,
            # 'subaddr_indices' : []   # 如果为空, 则查询所有
        }

        logging.info(f'starting get_transfers')
        res = self.raw_request(method='get_transfers',  params=params )
        logging.info(f'get_transfers finished. result: {res}')

        res_in_txs = res['in'] if 'in' in res else []

        for in_tx in  res_in_txs:

            tmp_tx = {}

            tmp_tx['dst_addr'] = in_tx['address']
            tmp_tx['amount'] = RoundDown( Decimal( in_tx['amount'] ) / Decimal(10**12) )
            tmp_tx['confirmations'] = in_tx['confirmations']

            if  in_tx['confirmations'] < 10:
                logging.info(f'txid:{in_tx["txid"]} confirmations : {in_tx["confirmations"]}/10 .')
                continue

            tmp_tx['blocknumber'] = in_tx['height']

            #subaddr_index  {major, minor}  可以推出 和  in_tx['address']相同
            tmp_tx['timestamp'] = in_tx['timestamp']
            tmp_tx['txid'] = in_tx['txid']
            tmp_tx['type'] = in_tx['type']  #充币交易必须是  'in'

            #double_spend_seen 一般是用于  pool 交易的判断, 这里只是
            if in_tx['double_spend_seen']:
                logging.warning(f'txid:{tmp_tx["txid"]} is double spend tx ')
                continue

            tmp_tx['unlock_time'] = in_tx['unlock_time']  # 必须是 0,  如果不是0, 说明还没解锁
            tmp_tx['locked'] = in_tx['locked']  # 如果是锁定的不要,充币不能锁定
            if tmp_tx['locked']:
                logging.warning(f'txid:{tmp_tx["txid"]} is locked tx, unlock_time: { tmp_tx["unlock_time"]  }')
                continue

            major = in_tx['subaddr_index']['major']
            minor = in_tx['subaddr_index']['minor']
            if major == 0 and minor == 0:
                logging.warning(f'txid:{tmp_tx["txid"]} is master addr(0, 0) tx , do not regard as deposit tx  ')
                continue


            subaddr = get_address_ex(private_view_key=XMR_PRIV_VIEW_KEY, master_addr=XMR_MASTER_ADDR, major=major, minor=minor)

            if subaddr != tmp_tx['dst_addr']:
                logging.info(f'tx dst_addr is {tmp_tx["dst_addr"]}, but ({major}, {minor}) sub addr is {subaddr}')
                continue

            ret_txs.append( tmp_tx )

        return ret_txs


    pass



class  XmrScanner(object):


    def __init__(self,
                 wallet_rpc_host='127.0.0.1',
                 port=38089,
                 verify_ssl_certs=False,
                 protocol='http',
                 timeout = 30,
                confirmations=3):


        self._confirmations = confirmations
        self._rpc = JSONRPCWalletEx(
            protocol=protocol,
            host=wallet_rpc_host,
            port=port,
            verify_ssl_certs=verify_ssl_certs,
            timeout=timeout)

        self._wallet = Wallet( backend= self._rpc )

        #直接从数据库获取地址, 用户后面的比对
        # self.addrs = self._GetExDepositAddrsFromDB()




    # def _get_addrs_from_db(self):
    #     try:
    #         sqlstr = """SELECT DISTINCT `address` from `tb_trx_deposit_addrs`;"""
    #         sql_result = sql.run(sqlstr)
    #         addrs = []
    #         for item in sql_result:
    #             if 'address' not in item: continue
    #             addrs.append(item['address'].strip())
    #         return addrs
    #     except  Exception as e:
    #         logging.error(" _GetAddresses() error: {}".format( e))
    #         return []
    #     pass


    def _push_tx_into_db(self, tx : dict) :

        strSql = """INSERT INTO tb_xmr_deposit(`txid`,`timestamp`,`dst_addr`,`amount`,`symbol`,`confirmations`, `block_number`) """
        strSql += f"""VALUES('{tx['txid']}',{tx['timestamp']}, '{tx['dst_addr']}','{tx['amount']}','XMR',{tx['confirmations']}, {tx['blocknumber']}) """
        strSql += """ ON DUPLICATE KEY UPDATE `confirmations`={}; """.format(tx['confirmations'])
        logging.info("sql: {}  ".format(strSql))
        ret = sql.run(strSql)



    #TODO: 后期充币量大的时候, 从tb_xmr_deposit 表获取最大的区块高度,然后根据高度过滤
    def start_scan(self):

        txs = self._rpc.get_deposit_txs()

        for tx in txs:
            self._push_tx_into_db(tx)

        pass




def InitLoggingSetting():
    log_format = '[%(asctime)s |  %(process)d  |  %(levelname)s | %(pathname)s |%(funcName)s:%(lineno)d ] %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)




def test_1():
    InitLoggingSetting()

    logging.info("trx scanner starting ...")


    rpc = JSONRPCWalletEx(
        protocol='http',
        host='192.168.10.160',
        port=38089,
        verify_ssl_certs=False,
        timeout=60)

    wallet = Wallet( backend= rpc )

    print( wallet.view_key() )


    # watch-only 不能获取,  否则抛异常
    # print(wallet.seed())


    #如果是观察钱包, 需要导入 key-image  才能确定哪些余额是可用的
    print( wallet.balances() )


    # pprint(rpc.incoming_transfers( account_index=2 ))

    #
    # filter = {
    #     'tx_ids' : None,
    #     'unconfirmed': None,
    #     'payment_ids': None,
    #     'min_height': 0,
    #     'max_height': None
    # }
    #
    # filter = PaymentFilter( **filter )
    #
    # # filter = object.__dict__.update(filter)
    #
    #
    # ret = wallet._backend.transfers_in(0, filter)

    res = rpc.get_deposit_txs()






    #获取子地址
    print( wallet.get_address(0, 1) )



    pass


def main():
    # test_1()
    InitLoggingSetting()

    logging.info('xmr scanner starting .....')


    protocol = 'https' if XMR_RPC_HTTPS_ENABLE else 'http'
    host = XMR_WALLET_RPC_HOST
    port = XMR_WALLET_RPC_PORT
    xmr_scanner = XmrScanner(
               wallet_rpc_host=host,
               port=port,
               verify_ssl_certs=False,
               protocol=protocol,
               timeout=60 )

    while True:
        try:
            xmr_scanner.start_scan()
        except Exception as e:
            logging.error("{}".format(e))
            pass
        sleep(60)

    pass


if __name__ == '__main__':

    main()