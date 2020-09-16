#!coding:utf8

#author:yqq
#date:2020/5/13 0013 22:29
#description:  HTDF scanner 实现类
import logging
from datetime import datetime
from decimal import Decimal
from typing import List

import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.model.model import Deposit, Address, ActiveAddressBalance
from src.config.constant import HTDF_BLOCK_TO_WAIT_FOR_CONFIRM, REDIS_HOST, REDIS_PORT, REDIS_ADDRESS_POOL_DB_NAME, \
    g_IS_MAINNET, \
    HTDF_NODE_RPC_HOST, HTDF_NODE_RPC_PORT, MYSQL_CONNECT_INFO, HRC20_CONTRACT_MAP
from src.lib.log import get_default_logger
from src.scanners.htdf.cosmos_proxy import CosmosProxy
from src.scanners.htdf.my_bech32 import HexAddrToBech32
from src.scanners.scanner_base import ScannerBase
from src.scanners.utils import round_down

class HTDFScannerImpl(ScannerBase):

    def __init__(self, token_name : str = 'HTDF'):
        self.block_count_to_wait_confirm = HTDF_BLOCK_TO_WAIT_FOR_CONFIRM

        self.token_name = token_name

        self.logger = get_default_logger(log_level=logging.INFO)

        engine = create_engine(MYSQL_CONNECT_INFO,
                               max_overflow=0,
                               pool_size=5)
        Session = sessionmaker(bind=engine, autocommit=True, autoflush=False)

        self.session = Session()
        self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_ADDRESS_POOL_DB_NAME, decode_responses=True)

        self.rpc = CosmosProxy(host=HTDF_NODE_RPC_HOST, port=HTDF_NODE_RPC_PORT, cointype=token_name)

        super().__init__()
        pass

    def refresh_deposit_address_balance(self, address: str) -> bool:

        try:
            self.logger.info("active_addr is : {}".format(address))
            strBalance = self.rpc.getBalance(address)  # 获取余额


            deposit_address =  self.session.query(Address).filter(Address.address == address).first()

            assert isinstance(deposit_address, Address), "deposit_address is not Address object!!!"
            assert deposit_address.token_name.upper() == self.token_name.upper()

            address_balance_instance = ActiveAddressBalance(token_name= deposit_address.token_name,
                                                            address=address,
                                                            pro_id=deposit_address.pro_id,
                                                            balance=Decimal(strBalance),
                                                            update_time=datetime.now())
            sql_ret = self.session.merge(instance=address_balance_instance, load=True)
            self.session.flush()
            return True
        except Exception as e:
            self.logger.error(f" refresh_deposit_address_balance error: {e}")
            return  False

        pass

    def refresh_deposit_address_hrc20_balance(self, address: str, symbol: str, contract_addr: str) -> bool:
        """
        更新地址的HRC20 余额
        :param address: 充币地址
        :param symbol: 代币名
        :param contract_addr:  合约地址
        :return: 成功: True  失败: False
        """
        try:
            self.logger.info(f'active HRC20 is : {address}, symbol:{symbol},contract:{contract_addr}')
            strbalance = self.rpc.getHRC20TokenBalance(contract_addr, address)

            deposit_address = self.session.query(Address).filter(Address.address == address).first()

            assert isinstance(deposit_address, Address), "deposit_address is not Address object!!!"
            assert  contract_addr.lower() in HRC20_CONTRACT_MAP , f'not found contract: {contract_addr} in HRC20_CONTRACT_MAP'
            assert  symbol == HRC20_CONTRACT_MAP[contract_addr]['symbol'], f'symbol:{symbol} is not matched in HRC20_CONTRACT_MAP!'


            address_balance_instance = ActiveAddressBalance(token_name=symbol, #HRC20 代币的 symbol
                                                            address=address,
                                                            pro_id=deposit_address.pro_id,
                                                            balance=Decimal(strbalance),
                                                            update_time=datetime.now())
            sql_ret = self.session.merge(instance=address_balance_instance, load=True)
            self.session.flush()
            return True
        except Exception as e:
            self.logger.error(f" refresh_deposit_address_HRC20_balance error: {e}")
            return  False

        pass

    def get_latest_block_height_from_blockchain(self) -> int:
        latest_height = int(str(self.rpc.getLastestBlockNumber()))
        return latest_height


    def get_deposit_transactions_from_block(self, height: int) -> List[Deposit]:

        block_data = self.rpc.getBlockByBlockNum(height)

        ret_tx_data = []
        txs = block_data["block"]["txs"]
        if not isinstance(txs, list): return []
        for tx in txs:

            tmp_tx_data = {}

            if tx is None : continue


            if tx['TxClassify'] not in [0, 1] : continue    # 0:HTDF交易   1:合约交易


            # 2019-06-13 yqq 因失败的交易也会被打包进区块, 所以,加上交易有效性判断
            strTxid = str(tx["Hash"]).strip()
            if len(strTxid) != 64:
                self.logger.info("strTxid is invalid txid")
                continue

            # 对交易有效性进行判断
            if not self.rpc.isValidTx(strTxid):
                self.logger.info("%s is invalid tx" % strTxid)
                continue

            # 如果是HRC20代币, 暂时不支持, 直接跳过即可
            # if tx['Amount'][0]['amount'] == '0':
            #     continue
            tmp_tx_data["txid"] = str(tx["Hash"]).strip()
            tmp_tx_data["from"] = str(tx["From"]).strip()
            tmp_tx_data["to"] = str(tx["To"]).strip()
            tmp_tx_data["amount"] = tx["Amount"][0]["amount"]  # 单位是 HTDF, 不用再除10**8
            # tmp_tx_data["timestamp"] = timestamp
            tmp_tx_data['memo'] = str(tx['Memo']).strip() if len(tx['Memo']) < 50 else tx['Memo'][:50]  # 如果太长截取前50个字符
            from_addr = tmp_tx_data["from"].strip()
            to_addr = tmp_tx_data["to"].strip()

            self.logger.info(f"{strTxid} is valid tx, from: {from_addr} to:{to_addr}")

            if tx['TxClassify'] == 1: # 1 : 合约交易
                data = tx['Data']
                if len(data) != (4 + 32 + 32) * 2 :
                    continue

                contract_addr = tx['To']
                if contract_addr not in HRC20_CONTRACT_MAP:
                    self.logger.info(f'contract address {contract_addr} is not my case')
                    continue

                method_sig = data[: 4 * 2]
                if method_sig.lower() != 'a9059cbb':  # 验证方法是否是 transfer
                    self.logger.info(f'method sig is not  `transfer` sig . data:{method_sig}')
                    continue

                token_recipient = data[4*2+12*2 : 4*2+32*2]  # 只去最后 20 字节, 丢掉前面填补的12字节0

                token_recv_addr = HexAddrToBech32(hrp='htdf', hexstraddr=token_recipient)
                token_amount = data[4*2+32*2 : ]
                token_decimal = HRC20_CONTRACT_MAP[contract_addr]['decimal']
                token_symbol = HRC20_CONTRACT_MAP[contract_addr]['symbol']
                token_sender = tx['From']

                if self.is_in_address_cache(address=token_sender):
                    self.refresh_deposit_address_balance(address=token_sender) #因发送方需要扣除HTDF作为手续费, 所以需要更新 HTDF余额
                    self.refresh_deposit_address_hrc20_balance(token_sender, token_symbol, contract_addr)

                if not self.is_in_address_cache(address = token_recv_addr ):
                    self.logger.info(f'{token_recv_addr} is not is address pool')
                    continue

                assert token_decimal == 18 , 'token_decimal is not 18'  #除非有特殊, 原则上精度都是 18

                if int(token_amount, 16) < 10**10:
                    self.logger.info(f'token_amount:{token_amount} is too small, skip!')
                    continue

                deposit_address = self.session.query(Address).filter(Address.address == token_recv_addr).first()
                if deposit_address is None:
                    self.logger.error(f'ERROR: not found address {to_addr} in databases!')
                    continue

                token_amount = round_down( Decimal(int(token_amount, 16)) / Decimal(10 ** token_decimal) )

                deposit_tx = Deposit()
                deposit_tx.tx_hash = tmp_tx_data['txid']
                deposit_tx.token_name =  str(token_symbol).upper()
                deposit_tx.notify_status = 0
                deposit_tx.memo = tmp_tx_data['memo']
                deposit_tx.pro_id = deposit_address.pro_id
                deposit_tx.from_addr = token_sender
                deposit_tx.to_addr = token_recv_addr
                deposit_tx.amount = token_amount
                deposit_tx.block_time = datetime.strptime(block_data['time'], "%Y-%m-%d %H:%M:%S")
                deposit_tx.tx_confirmations = 1
                deposit_tx.block_height = height

                ret_tx_data.append(deposit_tx)

                #接收地址只更新 HRC20代币余额, 不更新HTDF余额
                self.refresh_deposit_address_hrc20_balance(token_recv_addr, token_symbol, contract_addr)

                continue

            else: # 0 表示 HTDF交易

                if self.is_in_address_cache(address=from_addr):  # 这种情况是地址被归集了,需要更新余额
                    self.refresh_deposit_address_balance(from_addr)

                if not self.is_in_address_cache(address=to_addr):  # 仅监测交易所用户的地址,
                    self.logger.info(f"TX IS NOT MY CARE: {strTxid} is valid tx,from: {from_addr} to:{to_addr}")
                    continue

                # 发现关心的充币交易
                self.logger.info(f"TX IS MINE: {strTxid} is valid tx,from: {from_addr} to:{to_addr}")

                deposit_address = self.session.query(Address).filter(Address.address == to_addr).first()
                if deposit_address is None:
                    self.logger.error(f'ERROR: not found address {to_addr} in databases!')
                    continue

                deposit_tx = Deposit()
                deposit_tx.tx_hash = tmp_tx_data['txid']
                deposit_tx.token_name = self.token_name.upper()
                deposit_tx.notify_status = 0
                deposit_tx.memo = tmp_tx_data['memo']
                deposit_tx.pro_id = deposit_address.pro_id
                deposit_tx.from_addr = tmp_tx_data['from']
                deposit_tx.to_addr = tmp_tx_data['to']
                deposit_tx.amount = Decimal(tmp_tx_data['amount'])
                deposit_tx.block_time = datetime.strptime(block_data['time'], "%Y-%m-%d %H:%M:%S")
                deposit_tx.tx_confirmations = 1
                deposit_tx.block_height = height

                ret_tx_data.append(deposit_tx)
                self.refresh_deposit_address_balance(to_addr)



        return ret_tx_data



