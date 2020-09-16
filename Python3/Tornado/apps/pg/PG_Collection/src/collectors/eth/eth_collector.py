#!coding:utf8

#author:yqq
#date:2020/4/30 0030 19:56
#description: ETH 归集, 满足 归集条件的  直接归集即可


import decimal
import time
from datetime import datetime
from decimal import Decimal

from web3 import Web3, HTTPProvider
from eth_typing import HexStr
from eth_utils import to_checksum_address
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.collectors.eth.eth_transfer_utils import eth_transfer
from src.collectors.eth.my_eth_utils import eth_get_transaction_status
from src.collectors.htdf.htdf_transfer_utils import htdf_transfer
from src.collectors.htdf.htdf_utils import htdf_get_transaction_status
from src.collectors.htdf.proxy import HTDFProxy
from src.config.constant import g_MNEMONIC, WithdrawStatus, CollectionType, ETH_FULL_NODE_RPC_URL, MYSQL_CONNECT_INFO, \
    ETH_ERC20_GAS_PRICE
from src.lib.addr_gen.htdf_addr_gen import bech32_decode
from src.lib.my_bip44.wrapper import gen_bip44_subprivkey_from_mnemonic
from src.model.model import ActiveAddressBalance, CollectionConfig, Address, CollectionRecords

import logging


def get_default_logger(log_level=logging.INFO):
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s |  %(process)d  |  %(levelname)s | %(pathname)s |%(funcName)s:%(lineno)d] %(message)s')
    return logging.getLogger(__name__)


logger = get_default_logger()


def is_valid_eth_address(address: str) -> bool:
    if not (address.startswith('0x') and len(address) == 42):
        return False

    try:
        n = int(address, 16)
    except Exception as e:
        return  False
    return True


def round_down(decim):
    decimalFormat = decim.quantize(Decimal("0.00000000"), getattr(decimal, 'ROUND_DOWN'))
    return decimalFormat


def collect_eth():
    """
    开始归集
    :return:
    """

    # 1) 查询 tb_active_address_balances 表获取符合归集条件的地址
    engine = create_engine(MYSQL_CONNECT_INFO,
                           max_overflow=0,
                           pool_size=5)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=True)  # 增删改操作 需要手动flush,
    session = Session()

    query_sets = session.query(CollectionConfig, ActiveAddressBalance, Address) \
        .filter(ActiveAddressBalance.token_name == 'ETH', CollectionConfig.token_name == 'ETH' ) \
        .filter(CollectionConfig.pro_id == ActiveAddressBalance.pro_id)  \
        .filter(Address.address == ActiveAddressBalance.address) \
        .filter(ActiveAddressBalance.balance >= CollectionConfig.min_amount_to_collect) \
        .all()

    tx_hash_list = []  # 保存本次广播的tx_hash 用于后面监控
    if not (query_sets is None or len(query_sets) == 0):
        logger.info(f'query_sets size is  {len(query_sets)} ')


        myweb3 = Web3(provider=HTTPProvider(endpoint_uri=ETH_FULL_NODE_RPC_URL))
        # https://web3py.readthedocs.io/en/stable/web3.eth.account.html?highlight=transaction
        # https://web3py.readthedocs.io/en/stable/web3.eth.account.html?highlight=transaction#sign-a-transaction


        # 2) 遍历地址列表进行转账操作, 并插入归集记录表
        for clc_cfg, act_addr, addr in query_sets:

            try:
                assert isinstance(clc_cfg, CollectionConfig)
                assert isinstance(act_addr, ActiveAddressBalance)
                assert isinstance(addr, Address)

                if not is_valid_eth_address(clc_cfg.collection_dst_addr):
                    logger.error(f'invalid collection dst address : {clc_cfg.collection_dst_addr}')
                    continue

                # TODO: 如果一笔交易早已经广播出去, 但是一直没有被打包, 此时如果贸然重新发起一笔新的交易,
                # TODO: 如果用的是 相同nonce 必然会导致上一笔交易被覆盖,
                # TODO: 如果用的是 pending 的nonce, 在上一笔交易被打包后, 这笔交易必然也失败

                # 判断 该地址是否有pending状态的归集交易, 如果有, 则跳过, 如果没有则正常归集
                pending_clcs = session.query(CollectionRecords)\
                                .filter( CollectionRecords.from_address == act_addr.address ,
                                        CollectionRecords.transaction_status == WithdrawStatus.transaction_status.PENDING)\
                                .all()

                if not( pending_clcs is None or len(pending_clcs) == 0 ):
                    logger.info(f'address {act_addr.address} had a pending tx, skipped it this time ')
                    continue


                address = addr.address

                from_address = to_checksum_address(address)  # 必须使用 checksum addres
                block_identifier = HexStr('pending')
                nonce = myweb3.eth.getTransactionCount(from_address, block_identifier=block_identifier)
                balance = myweb3.eth.getBalance(account=from_address, block_identifier=block_identifier)

                decim_balance = myweb3.fromWei(balance, 'ether')

                # balance_rsp = rpc.getBalance(strAddr=address)
                # float_balance = float(balance_rsp)
                # if float_balance < 0.06:

                min_tx_fee = Web3.fromWei( ETH_ERC20_GAS_PRICE * 10**9 * 21000 , 'ether')
                if decim_balance < min_tx_fee:
                    logger.info('balance is to small, skipped')
                    continue

                # logger.info(type(balance_rsp))
                logger.info(f'active address: {act_addr}')
                # logger.info( f'balance_rsp : {balance_rsp}')

                # 根据pro_id推导出私钥
                priv_key, sub_addr = gen_bip44_subprivkey_from_mnemonic(mnemonic=g_MNEMONIC,
                                                                        coin_type='ETH',
                                                                        account_index=addr.pro_id,
                                                                        address_index=addr.address_index
                                                                        )

                if not sub_addr == addr.address.lower():
                    # 致命错误, 不可恢复
                    raise Exception(f'ADDRESS NOT MATCH! { sub_addr  } != { addr.address.lower()}')
                    pass

                collect_amount = decim_balance - min_tx_fee


                if collect_amount < min_tx_fee:
                    logger.info('collect_amount is too small, skipped')
                    continue
                # 进行转账
                trans_rsp = eth_transfer(priv_key=priv_key,
                                         from_addr=sub_addr,
                                         to_addr=clc_cfg.collection_dst_addr, amount=collect_amount)

                logger.info(f'tx_hash: {trans_rsp.tx_hash}')

                clc_records = CollectionRecords()
                clc_records.tx_hash = trans_rsp.tx_hash
                clc_records.pro_id = addr.pro_id
                clc_records.token_name = addr.token_name
                clc_records.amount = round_down(Decimal(collect_amount))
                clc_records.transaction_status = WithdrawStatus.transaction_status.PENDING
                clc_records.from_address = addr.address
                clc_records.collection_type = CollectionType.AUTO
                clc_records.to_address = clc_cfg.collection_dst_addr
                clc_records.complete_time = datetime.now()
                # clc_records.block_time = trans_rsp.block_time
                clc_records.block_height = 0

                # session = Session()
                session.add(instance=clc_records)
                session.flush()

                # 稍后进行监控
                tx_hash_list.append(trans_rsp.tx_hash)

                pass
            except Exception as e:
                logger.error(f'error:{e}')
                pass



    # 3) 监控发出的交易, 获取区块高度等信息, 并修改 交易状态
    # logger.info('sleeping...')
    # time.sleep(3)
    # logger.info('sleeping...')
    # time.sleep(3)
    # logger.info('sleeping...')
    # time.sleep(4)


    # tx_hash_list.append('c094a5b0238caec95cd28856fbaf9cc74d7b532c99fdd5b3cc83227afd981f5a')

    # 4) 获取数据库中所有
    all_pending_txs = session.query(CollectionRecords.tx_hash) \
        .filter(CollectionRecords.transaction_status == WithdrawStatus.transaction_status.PENDING,
                CollectionRecords.token_name == 'ETH') \
        .all()

    for item in all_pending_txs:
        tx_hash_list.append(item.tx_hash)

    for tx_hash in tx_hash_list:
        tx_status = eth_get_transaction_status(tx_hash=tx_hash)
        if tx_status.transaction_status == WithdrawStatus.transaction_status.SUCCESS:
            session.query(CollectionRecords) \
                .filter_by(tx_hash=tx_hash) \
                .update({
                'block_height': tx_status.block_height,
                'transaction_status': tx_status.transaction_status,
                'block_time': tx_status.block_time,
                'tx_confirmations': tx_status.confirmations,
                'complete_time': datetime.now()
            })
        elif tx_status.transaction_status == WithdrawStatus.transaction_status.FAIL:
            session.query(CollectionRecords) \
                .filter_by(tx_hash=tx_hash) \
                .update({
                'block_height': tx_status.block_height,
                'transaction_status': tx_status.transaction_status,
                'block_time': tx_status.block_time,
                # 'confirmations': tx_status.confirmations,
                'complete_time': datetime.now()
            })
        else:
            logger.info(f'tx_hash:{tx_hash} is still pending')
            pass

        pass

    pass


def main():
    while True:
        try:
            collect_eth()
            # break
            for i in range(100):
                logger.info('sleeping....')
                time.sleep(6)  # 10分钟归集一次
        except Exception as e:
            logger.error(f'{e}')

    pass


if __name__ == '__main__':
    main()
