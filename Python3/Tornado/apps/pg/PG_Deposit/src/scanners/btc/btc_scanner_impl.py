#!coding:utf8

#author:yqq
#date:2020/4/30 0030 16:21
#description:  BTC 区块扫描
from math import ceil
from typing import List

from src.model.model import Deposit
from src.scanners.btc.btc_proxy import BTCProxy
from src.scanners.scanner_base import ScannerBase

import logging
import time
import traceback
from binascii import unhexlify, hexlify
from datetime import datetime
from decimal import Decimal
from typing import List, Union

import redis
from eth_bloom import BloomFilter
from eth_typing import URI, BlockNumber, HexStr
from eth_utils import to_hex, to_checksum_address
from eth_utils import units
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from web3.types import TxData, BlockData

from src.model.model import Deposit, Address, ActiveAddressBalance
from src.config.constant import g_IS_MAINNET, ERC20_CONTRACTS_LIST, ETH_BLOCK_TO_WAIT_FOR_CONFIRM, \
    ERC20_TRANSFER_EVENT_HASH, MYSQL_CONNECT_INFO, ETH_FULL_NODE_RPC_URL, ETH_CHAIN_ID
from src.lib.log import get_default_logger
from src.scanners.eth_erc20.abi import EIP20_ABI
from src.config.constant import REDIS_HOST, REDIS_PORT, REDIS_ADDRESS_POOL_DB_NAME
from src.scanners.scanner_base import ScannerBase
from src.scanners.utils import hex_to_int, RoundDown


class BtcScannerImpl(ScannerBase):

    def __init__(self, btc_api_host: str, btc_api_port: int , token_name: str = 'BTC'):
        self.block_count_to_wait_confirm = 0

        self.token_name = token_name

        self.logger = get_default_logger(log_level=logging.INFO)

        engine = create_engine(MYSQL_CONNECT_INFO,
                               max_overflow=0,
                               pool_size=5, pool_recycle=1800)

        Session = sessionmaker(bind=engine, autocommit=True, autoflush=False)

        self.session = Session()
        self.redis = redis.Redis(host=REDIS_HOST,
                                 port=REDIS_PORT,
                                 db=REDIS_ADDRESS_POOL_DB_NAME,
                                 decode_responses=True)

        self.proxy = BTCProxy(host=btc_api_host, port=btc_api_port)

        super().__init__()

        pass

    def refresh_deposit_address_balance(self, address: str) -> bool:
        try:
            self.logger.info("active_addr is : {}".format(address))

            deposit_address = self.session.query(Address).filter(Address.address == address).first()
            assert isinstance(deposit_address, Address), "deposit_address is not Address object!!!"
            assert deposit_address.token_name.upper() == self.token_name.upper(), 'token is not match'

            balance = self.proxy.get_balance(address=address)
            balance = RoundDown(Decimal(balance) / Decimal(10 ** 8))
            self.logger.info(f'{address} balance is {balance} ')
            address_balance_instance = ActiveAddressBalance(token_name=deposit_address.token_name,
                                                            address=address,
                                                            pro_id=deposit_address.pro_id,
                                                            balance=Decimal(balance),
                                                            update_time=datetime.now())
            sql_ret = self.session.merge(instance=address_balance_instance, load=True)
            self.session.flush()
            return True
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f" refresh_deposit_address_balance error: {e}")
            return False
        pass

    def get_latest_block_height_from_blockchain(self) -> int:
        return self.proxy.get_latest_height()

    def get_deposit_transactions_from_block(self, height: int) -> List[Deposit]:

        self.logger.info(f'get txs from block {height}')

        latest_height = self.proxy.get_latest_height()
        blk_hash = self.proxy.get_block_hash(block_height=height)
        blk_info = self.proxy.get_block_info(block_hash=blk_hash)
        tx_count = blk_info['tx_count']
        blk_time = blk_info['timestamp']

        page_size = 100
        total_pages = ceil(tx_count / page_size)
        self.logger.info(f'total_pages is {total_pages}')

        ret_tx_data = []
        for page_idx in range(total_pages):
            start_index = page_idx * page_size
            self.logger.info(f'start_index is {start_index}')
            txs = self.proxy.get_block_txs(block_hash=blk_hash, start_index=start_index)

            txs = txs  if start_index != 0 else txs[1:]  #去掉 coinbase

            for tx in txs :

                for vin in tx['vin']:
                    if 'prevout' not in vin: continue
                    if vin['prevout'] is None : continue
                    if 'scriptpubkey_address' not in vin['prevout'] : continue
                    if vin['prevout']['scriptpubkey_type'] != 'p2pkh'  : continue

                    from_addr = vin['prevout']['scriptpubkey_address']
                    if self.is_in_address_cache(address=from_addr):
                        self.logger.info(f'{from_addr} is shabao address, so refresh its balance')
                        self.refresh_deposit_address_balance(address=from_addr)

                for vout in tx['vout']:
                    if vout['scriptpubkey_type'] != 'p2pkh':
                        continue

                    if vout['value'] < 546: #0.00000546
                        continue

                    to_addr = vout['scriptpubkey_address']
                    if not self.is_in_address_cache(address=to_addr):
                        continue

                    #是充币交易
                    deposit_address = self.session.query(Address).filter(Address.address == to_addr).first()
                    if deposit_address is None:
                        self.logger.error(f'ERROR: not found address {to_addr} in databases!')
                        continue

                    deposit_tx = Deposit()
                    deposit_tx.tx_hash = tx['txid']
                    deposit_tx.token_name = "BTC"
                    deposit_tx.notify_status = 0
                    deposit_tx.pro_id = deposit_address.pro_id
                    deposit_tx.from_addr = 'sourceaddressisunknown'  #源地址不可知, 因为有多个输入
                    deposit_tx.to_addr = to_addr
                    deposit_tx.amount = RoundDown( Decimal(vout['value']) / Decimal(10**8) )
                    deposit_tx.block_time = datetime.fromtimestamp(blk_time)
                    deposit_tx.tx_confirmations = latest_height - height + 1
                    deposit_tx.block_height = height

                    ret_tx_data.append(deposit_tx)
                    self.refresh_deposit_address_balance(to_addr)

        return ret_tx_data

