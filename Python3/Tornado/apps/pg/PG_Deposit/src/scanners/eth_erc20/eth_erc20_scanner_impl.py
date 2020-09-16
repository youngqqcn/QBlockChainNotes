#!coding:utf8

#author:yqq
#date:2020/5/13 0013 20:26
#description:  ETH  和 ERC20区块扫描的 实现类
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


class EthErc20ScannerImpl(ScannerBase):
    """
    ETH  和 ERC20区块扫描的 实现类
    """

    def __init__(self, token_name : str = 'ETH'):

        self.block_count_to_wait_confirm = ETH_BLOCK_TO_WAIT_FOR_CONFIRM

        self.token_name  = token_name

        self.logger = get_default_logger(log_level=logging.INFO)

        engine = create_engine(MYSQL_CONNECT_INFO,
                               max_overflow=0,
                               pool_size=5)
        Session = sessionmaker(bind=engine, autocommit=True, autoflush=False)

        self.session = Session()
        self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_ADDRESS_POOL_DB_NAME, decode_responses=True)
        self.myweb3 = Web3(provider=HTTPProvider(endpoint_uri=URI(ETH_FULL_NODE_RPC_URL)))

        if not g_IS_MAINNET and ETH_CHAIN_ID == 4:
            self.myweb3.middleware_onion.inject(element=geth_poa_middleware, layer=0)

        super().__init__()
        pass


    def refresh_deposit_address_balance(self, address: str) -> bool:

        try:
            block_identifier = HexStr('latest')  #不能用pending
            nbalance = self.myweb3.eth.getBalance(account=to_checksum_address(address), block_identifier=block_identifier)
            ether_balance = self.myweb3.fromWei(nbalance, 'ether') #ETH 余额

            deposit_address = self.session.query(Address).filter(Address.address == address).first()

            assert isinstance(deposit_address, Address), "deposit_address is not Address object!!!"
            assert deposit_address.token_name.upper() == 'ETH', 'token name is not ETH'   #所有ERC20代币, 共用 ETH地址

            address_balance_instance = ActiveAddressBalance(token_name=deposit_address.token_name,
                                                            address=address,
                                                            pro_id=deposit_address.pro_id,
                                                            balance= RoundDown( ether_balance ),
                                                            update_time=datetime.now())

            sql_ret = self.session.merge(instance=address_balance_instance, load=True)
            self.logger.info(f'merge ret : {sql_ret}')
            self.session.flush()


            # 检查代币余额
            for contract_addr in ERC20_CONTRACTS_LIST:

                chksum_contract_addr = to_checksum_address(contract_addr)
                contract = self.myweb3.eth.contract(address=chksum_contract_addr, abi=EIP20_ABI)
                symbol = contract.functions.symbol().call()
                decimals = contract.functions.decimals().call()

                erc20_token_balance_int = contract.functions.balanceOf(  to_checksum_address(address) ).call()


                unit = ''
                for unitstr, decimnumber in units.units.items():
                    if decimnumber == Decimal(str(10**decimals)):
                        unit = unitstr

                assert unit in units.units,  'unit is not in units.units'

                erc20_token_balance= self.myweb3.fromWei(erc20_token_balance_int, unit=unit)

                # 有可能为 0
                if isinstance(erc20_token_balance, int):
                    erc20_token_balance = Decimal(str(erc20_token_balance))

                token_balance = RoundDown(erc20_token_balance)

                # strSymbol = self.eth_erc20_symbol(contract_addr)
                # strBalance = self.eth_erc20_balanceOf(contract_addr, strAddr, True)

                instance = ActiveAddressBalance(token_name=str(symbol),
                                                address=address,
                                                pro_id=deposit_address.pro_id,
                                                balance=token_balance,
                                                update_time=datetime.now())

                sql_ret = self.session.merge(instance=instance, load=True)
                self.logger.info(f'merge ret : {sql_ret}')
                self.session.flush()
                return True

        except Exception as e:
            traceback.print_exc()
            self.logger.error(f" refresh_deposit_address_balance error: {e}")
            return False

        pass

    def get_latest_block_height_from_blockchain(self) -> int:
        """
        获取最新区块高度
        :return:
        """

        latest_height = self.myweb3.eth.blockNumber

        return latest_height


    def _get_erc20_token_deposit(self,   txdata : TxData, block_data : BlockData,
                                 latest_height : int) -> Union[Deposit, None]:
        """
        获取 ERC20 代币交易
        :param txdata:   交易信息
        :param block_data:  区块数据
        :param latest_height:  最新区块高度
        :return:  如果有ERC20 返回 Deposit ,  如果没有返回 None
        """

        to_addr = txdata['to']

        is_my_erc20_contract = False
        for item in ERC20_CONTRACTS_LIST:
            if str(item).lower() == str(to_addr).lower():
                is_my_erc20_contract = True

        if not is_my_erc20_contract:
            self.logger.info(f'{str(to_addr).lower()} is not my  contract....')
            return None


        # 如果是合约调用合约进行的ERC20代币转账, to地址可能并不是代币合约的地址,
        # 因此必须通过bloomFilter进行过滤, 防止漏掉充值
        receipt = self.myweb3.eth.getTransactionReceipt(transaction_hash=txdata['hash'])

        if receipt['status'] != 1: return  None

        # 为了安全起见, 仅支持单个转账, 不支持合约批量转账!
        if receipt['logs'] == 1: return None

        n = int(hexlify(receipt["logsBloom"]).decode('latin1'), 16)
        bloom_filter = BloomFilter(n)

        # 检查 transfer事件是否存在
        if unhexlify(ERC20_TRANSFER_EVENT_HASH) not in bloom_filter:
            return None



        # 统一使用小写
        tmp_con_addrs = []

        for contract_addr in ERC20_CONTRACTS_LIST:
            con_addr = contract_addr.replace('0x', '').lower()  # 如果包含'0x'则去掉 '0x'
            if unhexlify(con_addr) in bloom_filter:
                tmp_con_addrs.append('0x' + con_addr)
                break

        if len(tmp_con_addrs) == 0:
            return None

        # 不支持合约的批量转账
        log = receipt['logs'][0]  # 安全起见 不支持 合约批量转账!

        if log['removed']: return None
        topics = log['topics']

        # transfer事件的topics的数量必须是3
        if len(topics) != 3: return None

        # 如果合约地址不是交易所要监控的合约,则跳过
        if str(log['address']).lower() not in tmp_con_addrs:
            return None

        # 如果事件的哈希不是transfer的, 则跳过
        event_hash = hexlify(topics[0]).decode('latin1')
        if ERC20_TRANSFER_EVENT_HASH.replace('0x', '').lower() != event_hash.replace('0x', '').lower():
            return None

        # addr_from 并不完全等于 tx['from'], 即合约的调用者并一定是token的发送方,
        #  可以参考ERC20标准的 transferFrom 方法
        token_sender = '0x' + hexlify(topics[1][-20:]).decode('latin1')  # ERC20代币的发送方
        token_recipient = '0x' + hexlify(topics[2][-20:]).decode('latin1')  # ERC20代币的接收方

        #因redis区分大小写, 所以统一使用小写,
        token_recipient = token_recipient.lower()
        token_sender = token_sender.lower()

        # 如果from地址是交易所的地址(一般是归集操作), 则也需要更新活跃地址表
        if self.is_in_address_cache(address=token_sender):
            # TODO:更新from地址的代币余额
            self.refresh_deposit_address_balance(token_sender)

        if not self.is_in_address_cache(address=token_recipient):  # 仅监测交易所用户的地址,
            self.logger.info(f'{token_recipient} not in address pool')
            return None

        # 正常充币的情况
        self.logger.info('in address pool')
        self.refresh_deposit_address_balance(token_recipient)

        # 获取代币简称 , 必须用 log['address'], 不能用tx['to'],
        # 因为合约调用合约, tx['to']是调用者, log['address']才是真正执行的合约
        contract_addr = log['address']
        chksum_contract_addr = to_checksum_address(contract_addr)
        contract = self.myweb3.eth.contract(address=chksum_contract_addr, abi=EIP20_ABI)
        symbol = contract.functions.symbol().call()
        decimals = contract.functions.decimals().call()

        amount_data = log['data']

        deposit_address = self.session.query(Address) \
            .filter(Address.address == token_recipient) \
            .first()

        if deposit_address is None:
            #如果能进来说明, 肯定有错!!
            self.logger.error(f'not found address token_recipient {token_recipient} in databases!')
            return None


        deposit_tx = Deposit()

        deposit_tx.tx_hash = to_hex(txdata["hash"])
        deposit_tx.token_name = symbol
        deposit_tx.notify_status = 0
        deposit_tx.memo = None
        deposit_tx.from_addr = str(txdata['from']).lower()
        deposit_tx.to_addr = token_recipient
        deposit_tx.amount = RoundDown(Decimal(int(amount_data, 16)) / Decimal(10 ** decimals))
        deposit_tx.block_time =datetime.fromtimestamp(int(block_data.timestamp))
        deposit_tx.block_height = block_data["number"]
        deposit_tx.pro_id = deposit_address.pro_id
        deposit_tx.tx_confirmations = latest_height - block_data['number']

        return  deposit_tx





    def get_deposit_transactions_from_block(self, height: int) -> List[Deposit]:

        try:
            ret_deposit_txs = []


            n_chain_lastest_height =  self.myweb3.eth.blockNumber

            block_info = self.myweb3.eth.getBlock(BlockNumber(height), full_transactions=True)


            included_contracts = []
            erc20_transfer_event = unhexlify(ERC20_TRANSFER_EVENT_HASH)

            n = int(hexlify(block_info.logsBloom).decode('latin1'), 16)
            bloom_filter = BloomFilter(n)

            # 测试合约地址是否存在
            if erc20_transfer_event in bloom_filter:  # 检查 transfer事件是否存在
                for contract_addr in ERC20_CONTRACTS_LIST:
                    con_addr = contract_addr.replace('0x', '').lower()  # 如果包含'0x'则去掉 '0x'
                    con_addr_bytes = unhexlify(con_addr)
                    if con_addr_bytes in bloom_filter:
                        included_contracts.append(con_addr)

            del bloom_filter

            for tx_data in block_info["transactions"]:

                # 如果是创建合约, to是 null  或者是 挖矿交易
                if tx_data['to'] is None :
                    self.logger.info('tx_data["to"] is None')
                    continue

                #因redis区分大小写, 所以统一使用小写进行redis匹配
                to_addr = str(tx_data['to']).lower()
                from_addr = str(tx_data['from']).lower()

                # if str(to_addr).lower() == '0xa1f5c76f14b3aeb1fd615f569c67993e8d890112':
                #     self.logger.info('-------------')

                if self.is_in_address_cache(address= to_addr):  # 普通的ETH充币

                    # 普通的ETH转账
                    deposit_address = self.session.query(Address)\
                                        .filter(Address.address == to_addr)\
                                        .first()

                    if deposit_address is None:
                        self.logger.warning(f'not found address {to_addr} in databases!')
                        continue

                    deposit_tx = Deposit()

                    deposit_tx.tx_hash = to_hex(tx_data["hash"])
                    deposit_tx.token_name = 'ETH'
                    deposit_tx.notify_status = 0
                    deposit_tx.memo = None
                    deposit_tx.pro_id = deposit_address.pro_id
                    deposit_tx.from_addr =  from_addr  # tx_data['from']
                    deposit_tx.to_addr = to_addr  #tx_data['to']
                    deposit_tx.amount = RoundDown( Web3.fromWei(tx_data["value"], 'ether'))
                    deposit_tx.block_time = datetime.fromtimestamp(int(block_info.timestamp)),
                    deposit_tx.tx_confirmations =  n_chain_lastest_height - block_info['number']
                    deposit_tx.block_height = block_info["number"]

                    self.logger.info(f"found  ETH deposit  tx:{deposit_tx}")
                    ret_deposit_txs.append(deposit_tx)

                    self.refresh_deposit_address_balance(address=to_addr)
                    continue

                # ETH归集
                if self.is_in_address_cache(address=from_addr):
                    self.refresh_deposit_address_balance(address=from_addr)
                    pass


                # 继续判断是否包含 ERC20代币交易
                if 0 == len(included_contracts):
                    continue

                # 获取关心的ERC20代币转账
                erc20_deposit_tx = self._get_erc20_token_deposit(tx_data, block_info, n_chain_lastest_height)

                if erc20_deposit_tx is not None:
                    ret_deposit_txs.append(erc20_deposit_tx)
                    self.logger.info(f"found  ETH deposit  tx:{erc20_deposit_tx}")

                pass

            return ret_deposit_txs
        except Exception as e:
            # traceback.print_exc()
            self.logger.error(f"get_deposit_transactions_from_block({height}) error:{e}")
            time.sleep(2)
            raise e

        pass

