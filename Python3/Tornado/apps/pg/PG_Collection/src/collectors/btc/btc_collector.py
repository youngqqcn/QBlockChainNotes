#!coding:utf8

#author:yqq
#date:2020/7/13
#description: BTC归集


import logging
from collections import OrderedDict

from bitcoin import SelectParams
from bitcoin.wallet import CBitcoinAddress

from src.collectors.btc.btc_proxy import BTCProxy, BadStatusCodeError
from src.collectors.btc.btc_transfer_utils import BTCTransferUitl
from src.lib.pg_utils import round_down


def get_default_logger(log_level=logging.INFO):
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s |  %(process)d  |  %(levelname)s | %(pathname)s |%(funcName)s:%(lineno)d] %(message)s')
    return logging.getLogger(__name__)

logger = get_default_logger()

import decimal
import time
from datetime import datetime
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.collectors.htdf.htdf_transfer_utils import htdf_transfer
from src.collectors.htdf.htdf_utils import htdf_get_transaction_status
from src.collectors.htdf.proxy import HTDFProxy
from src.config.constant import g_MNEMONIC, WithdrawStatus, CollectionType, MYSQL_CONNECT_INFO, \
    HTDF_NODE_RPC_HOST, HTDF_NODE_RPC_PORT, ENV_NAME, BTC_API_HOST, BTC_API_PORT, g_IS_MAINNET, SubMonitorFuncResponse
from src.lib.addr_gen.htdf_addr_gen import bech32_decode
from src.lib.my_bip44.wrapper import gen_bip44_subprivkey_from_mnemonic
from src.model.model import ActiveAddressBalance, CollectionConfig, Address, CollectionRecords



def btc_get_transaction_status(tx_hash: str) -> SubMonitorFuncResponse:
    """
    获取btc的交易状态,
    :param rst:
    :return: True: 成功,  False 失败
    """

    btcproxy = BTCProxy(host=BTC_API_HOST, port=BTC_API_PORT)

    ret_info = SubMonitorFuncResponse()
    ret_info.transaction_status = WithdrawStatus.transaction_status.PENDING
    ret_info.confirmations = 0
    ret_info.block_height = 0
    ret_info.tx_hash = tx_hash
    ret_info.block_time = datetime.now()

    try:
        txinfo = btcproxy.get_transaction(txid=tx_hash)

        if txinfo['status']['confirmed']:

            latest_height = btcproxy.get_latest_height()

            # 成功监控到
            ret_info.block_height = txinfo['status']['block_height']
            ret_info.block_time = datetime.fromtimestamp(txinfo['status']['block_time'])
            ret_info.confirmations = int(latest_height) - int(ret_info.block_height) + 1
            ret_info.transaction_status = WithdrawStatus.transaction_status.SUCCESS
            return ret_info

    except BadStatusCodeError as e:
        if str(e) == str('404'):
            logging.error(f'btc api server return 404, not found transaction: {tx_hash}')
            ret_info.transaction_status = WithdrawStatus.transaction_status.FAIL
            return ret_info

    except Exception as e:
        logging.error(e)

    return ret_info



def is_valid_addr(address: str, token_name: str) -> bool:

    try:
        if token_name == 'HTDF':
            return len(address) == 43 and  address.startswith('htdf1') and address.islower()
        elif token_name == 'ETH' or token_name == 'USDT':
            return len(address) == 42 and  address.startswith('0x') and  int(address, base=16)
        elif token_name == 'BTC':
            if g_IS_MAINNET:
                SelectParams('mainnet')
                addr = CBitcoinAddress(s = address)
            else:
                SelectParams('testnet')
                addr = CBitcoinAddress(s = address)

            assert addr is not None , 'addr is None'

            #如果没有抛异常直接返回即可
            return True
        else:
            raise RuntimeError(f"unknow token_name: {token_name}")
    except Exception as e:
        logger.error(f'is_valid_addr() , {address} is invalid address, error:{e}')
        return False
    pass

def btc_collect():
    # 1) 查询 tb_active_address_balances 表获取符合归集条件的地址
    engine = create_engine(MYSQL_CONNECT_INFO,
                           max_overflow=0,
                           pool_size=5)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=True)  # 增删改操作 需要手动flush,
    session = Session()

    query_sets = session.query(CollectionConfig, ActiveAddressBalance, Address) \
        .filter(ActiveAddressBalance.token_name == 'BTC', CollectionConfig.token_name == 'BTC') \
        .filter(CollectionConfig.pro_id == ActiveAddressBalance.pro_id) \
        .filter(Address.address == ActiveAddressBalance.address) \
        .filter(ActiveAddressBalance.balance >= CollectionConfig.min_amount_to_collect) \
        .all()

    tx_hash_set = set()  # 保存本次广播的tx_hash 用于后面监控

    if not (query_sets is None or len(query_sets) == 0):
        logger.info(f'query_sets size is  {len(query_sets)} ')

        proxy = BTCProxy(host=BTC_API_HOST, port=BTC_API_PORT)
        btcutil = BTCTransferUitl(host=BTC_API_HOST, port=BTC_API_PORT,
                                       net_type='mainnet' if g_IS_MAINNET else 'testnet')

        # 2) 遍历地址列表进行转账操作, 并插入归集记录表

        class CLC_ADDR_INFO:
            pro_id = 0xffffff
            src_address = ''
            dst_address = ''
            clc_amount_in_satoshi = 0
            priv_key = ''
            txhash  = ''

        addr_info_map = dict()

        for clc_cfg, act_addr, addr in query_sets:
            assert isinstance(clc_cfg, CollectionConfig)
            assert isinstance(act_addr, ActiveAddressBalance)
            assert isinstance(addr, Address)

            if not is_valid_addr(clc_cfg.collection_dst_addr, token_name='BTC'):
                logger.error(f'invalid collection dst address : {clc_cfg.collection_dst_addr}')
                continue

            from_addr = addr.address
            balance_in_satoshi = proxy.get_balance(address=from_addr) #默认是保守方式的余额
            balance_in_btc = round_down(Decimal(balance_in_satoshi) / Decimal(10 ** 8))

            # 判断地址的(链上)余额是否满足归集条件
            if balance_in_btc < Decimal(clc_cfg.min_amount_to_collect):
                logger.info(f'{from_addr}, BTC balance:{balance_in_btc} is less than min_amount_to_collect')
                continue
            logger.info(f'active address: {act_addr}')

            nettype = 'mainnet' if g_IS_MAINNET else 'testnet'
            priv_key, sub_addr = gen_bip44_subprivkey_from_mnemonic(mnemonic=g_MNEMONIC,
                                                                    coin_type='BTC',
                                                                    account_index=addr.pro_id,
                                                                    address_index=addr.address_index,
                                                                    nettype=nettype)

            if not sub_addr == addr.address:  #大小写敏感, 不能转为小写
                # 致命错误, 不可恢复
                raise Exception(f'ADDRESS NOT MATCH! { sub_addr  } != { addr.address}')
                pass

            if clc_cfg.pro_id not in addr_info_map:
                addr_info_map[clc_cfg.pro_id] = []

            addr_info = CLC_ADDR_INFO()
            addr_info.pro_id = clc_cfg.pro_id
            addr_info.src_address = from_addr
            addr_info.priv_key = priv_key
            addr_info.txhash = ''
            addr_info.clc_amount_in_satoshi = balance_in_satoshi
            addr_info.dst_address = clc_cfg.collection_dst_addr

            addr_info_map[clc_cfg.pro_id].append(addr_info)


        for pro_id, addr_infos in addr_info_map.items():

            if len(addr_infos) == 0: continue

            sum_amount_in_satoshi = 0
            tmp_addrs = []
            dst_addr = addr_infos[0].dst_address

            src_addrs_key_map = OrderedDict()

            for addr_info in addr_infos:
                assert pro_id == addr_info.pro_id , 'pro_id not match!'
                assert dst_addr == addr_info.dst_address, 'dst_addr not match!'
                if addr_info.src_address not in tmp_addrs: #去重
                    tmp_addrs.append(addr_info.src_address)
                    sum_amount_in_satoshi += addr_info.clc_amount_in_satoshi
                    src_addrs_key_map[addr_info.src_address] = addr_info.priv_key


            logger.info(f'to collect sub-address is: {tmp_addrs} ')


            # tmp_amount_in_btc = round_down(Decimal(sum_amount_in_satoshi) / Decimal(10 ** 8))
            is_enough, founded_utxos, sum_utxo_satoshi = btcutil.search_utxo(addrs=tmp_addrs,
                                                                        total_amount=Decimal('1000.0'), #为了获取所有的UTXO(包括尚未确认的utxo)
                                                                        min_utxo_value=1000)



            if sum_utxo_satoshi > sum_amount_in_satoshi:
                logger.info('sum_utxo_satoshi > sum_amount_in_satoshi,  will collect unconfirmed utxo')
            elif sum_utxo_satoshi == sum_amount_in_satoshi:
                logger.info('sum_utxo_satoshi == sum_amount_in_satoshi, not exist unconfirmed utxo, everything is perfect! ')
            else:
                logger.info('sum_utxo_satoshi < sum_amount_in_satoshi, maybe exsit some dusty utxo those less than 1000 satoshi')

            # 计算输入的utxo的数量, 用于计算手续费
            fee_rate = 20
            utxo_count = 0
            for addr, utxos in founded_utxos.items():
                utxo_count += len(utxos)

            txfee =  round_down( Decimal(str((148 * utxo_count + 34 * 1 + 10))) * Decimal(fee_rate) / Decimal(10 ** 8) )# Decimal(str((148 * nIn + 34 * nOut + 10))) * Decimal(rate)
            txfee = txfee if txfee <= Decimal('0.0002') else Decimal('0.0002')  # 防止手续费给太多

            #本次归集的金额, 以搜索到的所有utxo的总金额为准
            total_clc_amount_satoshi = sum_utxo_satoshi - int(txfee * Decimal(10**8)) - 1    #减去手续费, 因为 transfer中真实到账金额,不包括手续费

            dst_addrs_amount_map = OrderedDict()
            dst_addrs_amount_map[dst_addr] = round_down(Decimal(total_clc_amount_satoshi) / Decimal(10 ** 8))



            try:
                assert proxy.ping() == True, 'bitcoind rpc is gone'  # 测试 bitcoind的 rpc服务是否还在
                txid = btcutil.transfer(src_addrs_key_map=src_addrs_key_map,
                                        dst_addrs_amount_map=dst_addrs_amount_map,
                                        txfee=txfee,
                                        auto_calc_pay_back=False,
                                        pay_back_index=0xfffffff,
                                        ensure_one_txout=True)

                logger.info(f'txid: {txid}')

                if not session.is_active:
                    session = Session()

                for addr, utxos in founded_utxos.items():

                    collect_amount_in_satoshi = 0  # 当前地址归集了的金额
                    for utxo in utxos:
                        collect_amount_in_satoshi += utxo['value']

                    clc_records = CollectionRecords()
                    clc_records.tx_hash = txid
                    clc_records.pro_id = pro_id
                    clc_records.token_name = 'BTC'
                    clc_records.amount = round_down(Decimal(collect_amount_in_satoshi) / Decimal(10 ** 8))
                    clc_records.transaction_status = WithdrawStatus.transaction_status.PENDING
                    clc_records.from_address = addr
                    clc_records.collection_type = CollectionType.AUTO
                    clc_records.to_address = dst_addr
                    clc_records.complete_time = datetime.now()

                    session.add(clc_records)
                    session.flush()

                # 稍后要查询交易状态
                tx_hash_set.add(txid)

            except Exception as e:
                logger.error(f'error: {e}')
                time.sleep(2)
                pass


    # 3) 监控发出的交易, 获取区块高度等信息, 并修改 交易状态
    logger.info('waiting  5s for tx confirmed')
    time.sleep(5)

    # 4) 获取数据库中所有
    all_pending_txs = session.query(CollectionRecords.tx_hash) \
        .filter(CollectionRecords.transaction_status == WithdrawStatus.transaction_status.PENDING,
                CollectionRecords.token_name == 'BTC') \
        .all()

    for item in all_pending_txs:
        tx_hash_set.add( item.tx_hash)  #自动去重


    #因为BTC是批量归集, 所以存在多笔归集记录的tx_hash相同, 更新数据库的交易状态时, 根据tx_hash进行查找即可
    for tx_hash in tx_hash_set:
        try:
            tx_status = btc_get_transaction_status(tx_hash=tx_hash)
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
                logger.info(f'{tx_hash} is still pending....')
                pass
        except Exception as e:
            logger.error(f'error: {e}')
            time.sleep(5)


    pass





def main():

    btc_collect()



    pass


if __name__ == '__main__':

    main()