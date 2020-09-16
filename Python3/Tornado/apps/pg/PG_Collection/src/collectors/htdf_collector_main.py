#!coding:utf8

#author:yqq
#date:2020/4/30 0030 19:56
#description:  HTDF归集
# 定时扫描 tb_active_address_balances 表, 对HTDF进行归集
import decimal
import time
from datetime import datetime
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.collectors.eth.erc20_collector import send_sms_queue
from src.collectors.htdf.htdf_transfer_utils import htdf_transfer, hrc20_transfer
from src.collectors.htdf.htdf_utils import htdf_get_transaction_status
from src.collectors.htdf.proxy import HTDFProxy
from src.config.constant import g_MNEMONIC, WithdrawStatus, CollectionType, MYSQL_CONNECT_INFO, \
    HTDF_NODE_RPC_HOST, HTDF_NODE_RPC_PORT, ENV_NAME, g_IS_MAINNET, HRC20_CONTRACT_MAP
from src.lib.addr_gen.htdf_addr_gen import bech32_decode
from src.lib.my_bip44.wrapper import gen_bip44_subprivkey_from_mnemonic
from src.model.model import ActiveAddressBalance, CollectionConfig, Address, CollectionRecords, Project

import logging
def get_default_logger(log_level=logging.INFO):
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s |  %(process)d  |  %(levelname)s | %(pathname)s |%(funcName)s:%(lineno)d] %(message)s')
    return logging.getLogger(__name__)


logger = get_default_logger()



def is_valid_htdf_address(address : str) -> bool:

    if not( address.startswith('htdf1') and len(address) == 43 ):
        return False

    hrp, data = bech32_decode(address)

    if hrp is None or data is None :
        return  False

    return  True



def round_down(decim):
    decimalFormat = decim.quantize(Decimal("0.00000000"), getattr(decimal, 'ROUND_DOWN'))
    return decimalFormat

def htdf_collect():
    """
    开始归集
    :return:
    """

    #1) 查询 tb_active_address_balances 表获取符合归集条件的地址
    engine = create_engine(MYSQL_CONNECT_INFO,
                           max_overflow=0,
                           pool_size=5)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=True)  # 增删改操作 需要手动flush,
    session = Session()

    query_sets = session.query(CollectionConfig, ActiveAddressBalance, Address)\
                        .filter(ActiveAddressBalance.token_name == 'HTDF', CollectionConfig.token_name == 'HTDF')\
                        .filter(CollectionConfig.pro_id == ActiveAddressBalance.pro_id)\
                        .filter(Address.address == ActiveAddressBalance.address)\
                        .filter(ActiveAddressBalance.balance >= CollectionConfig.min_amount_to_collect)\
                        .all()



    tx_hash_list = []  #保存本次广播的tx_hash 用于后面监控
    if not (query_sets is None or len(query_sets) == 0):
        logger.info(f'query_sets size is  {len(query_sets)} ')

        rpc = HTDFProxy(host=HTDF_NODE_RPC_HOST, port=HTDF_NODE_RPC_PORT)

        # 2) 遍历地址列表进行转账操作, 并插入归集记录表
        minimum_amount = Decimal('0.03')
        for clc_cfg, act_addr, addr in query_sets:
            assert isinstance(clc_cfg, CollectionConfig)
            assert isinstance(act_addr, ActiveAddressBalance)
            assert isinstance(addr, Address)

            if not is_valid_htdf_address(clc_cfg.collection_dst_addr):
                logger.error(f'invalid collection dst address : {clc_cfg.collection_dst_addr}')
                continue

            address = addr.address
            balance_rsp = rpc.getBalance(strAddr=address)

            float_balance = float(balance_rsp)
            if float_balance < minimum_amount * 2:
                logger.info('balance is to small, skipped')
                continue

            #判断地址的(链上)余额是否满足归集条件
            if float_balance < clc_cfg.min_amount_to_collect:
                logger.info(f'{address}, HTDF balance:{float_balance} is less than min_amount_to_collect')
                continue

            # logger.info(type(balance_rsp))
            logger.info(f'active address: {act_addr}')
            # logger.info( f'balance_rsp : {balance_rsp}')

            # 根据pro_id推导出私钥
            nettype = 'mainnet' if g_IS_MAINNET else 'testnet'
            priv_key, sub_addr = gen_bip44_subprivkey_from_mnemonic(mnemonic=g_MNEMONIC,
                                                                    coin_type='HTDF',
                                                                    account_index=addr.pro_id,
                                                                    address_index=addr.address_index,
                                                                    nettype=nettype)

            if not sub_addr == addr.address.lower():
                # 致命错误, 不可恢复
                raise Exception(f'ADDRESS NOT MATCH! { sub_addr  } != { addr.address.lower()}')
                pass

            collect_amount =  round_down( Decimal(float_balance) - minimum_amount)
            if collect_amount < minimum_amount:
                logger.info('collect_amount is to small, skipped')
                continue

            # 进行转账
            try:
                trans_rsp = htdf_transfer(priv_key=priv_key,
                                          from_addr=sub_addr,
                                          to_addr=clc_cfg.collection_dst_addr,
                                          amount_in_htdf=collect_amount,
                                          memo='shbao'
                                          )

                logger.info(f'tx_hash: {trans_rsp.tx_hash}')

                clc_records = CollectionRecords()
                clc_records.tx_hash = trans_rsp.tx_hash
                clc_records.pro_id = addr.pro_id
                clc_records.token_name = addr.token_name
                clc_records.amount = round_down(collect_amount)
                clc_records.transaction_status = WithdrawStatus.transaction_status.PENDING
                clc_records.from_address = addr.address
                clc_records.collection_type = CollectionType.AUTO
                clc_records.to_address = clc_cfg.collection_dst_addr
                clc_records.complete_time = datetime.now()
                # clc_records.block_time = trans_rsp.block_time
                clc_records.block_height = 0

                session.add(instance=clc_records)
                session.flush()

                # 稍后进行监控
                tx_hash_list.append(trans_rsp.tx_hash)
            except Exception as e:
                logger.error(f'error: {e}')
                time.sleep(1)

            pass



    #3) 监控发出的交易, 获取区块高度等信息, 并修改 交易状态
    sleep_secs = 10
    logger.info(f'waiting  {sleep_secs}s for tx confirmed')
    time.sleep(sleep_secs)



    #4) 获取数据库中所有
    all_pending_txs = session.query(CollectionRecords.tx_hash)\
                    .filter(CollectionRecords.transaction_status == WithdrawStatus.transaction_status.PENDING,
                            CollectionRecords.token_name == 'HTDF')\
                    .all()

    for item in all_pending_txs:
        tx_hash_list.append( item.tx_hash)



    for tx_hash in tx_hash_list:
        try:
            tx_status = htdf_get_transaction_status(tx_hash=tx_hash)
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
                logger.info('  other situation')
                pass
        except Exception as e:
            logger.error(f'error: {e}')
            time.sleep(1)

        pass

    pass



def hrc20_collect():
    """
    开始归集
    :return:
    """

    #1) 查询 tb_active_address_balances 表获取符合归集条件的地址
    engine = create_engine(MYSQL_CONNECT_INFO,
                           max_overflow=0,
                           pool_size=5)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=True)  # 增删改操作 需要手动flush,
    session = Session()

    query_sets = session.query(CollectionConfig, ActiveAddressBalance, Address)\
                        .filter(ActiveAddressBalance.token_name == 'BTU', CollectionConfig.token_name == 'BTU')\
                        .filter(CollectionConfig.pro_id == ActiveAddressBalance.pro_id)\
                        .filter(Address.address == ActiveAddressBalance.address)\
                        .filter(ActiveAddressBalance.balance >= CollectionConfig.min_amount_to_collect)\
                        .all()



    tx_hash_list = []  #保存本次广播的tx_hash 用于后面监控
    if not (query_sets is None or len(query_sets) == 0):
        logger.info(f'query_sets size is  {len(query_sets)} ')

        rpc = HTDFProxy(host=HTDF_NODE_RPC_HOST, port=HTDF_NODE_RPC_PORT)

        # 2) 遍历地址列表进行转账操作, 并插入归集记录表
        for clc_cfg, act_addr, addr in query_sets:
            assert isinstance(clc_cfg, CollectionConfig)
            assert isinstance(act_addr, ActiveAddressBalance)
            assert isinstance(addr, Address)

            if not is_valid_htdf_address(clc_cfg.collection_dst_addr):
                logger.error(f'invalid collection dst address : {clc_cfg.collection_dst_addr}')
                continue

            #  如果一笔交易早已经广播出去, 但是一直没有被打包, 此时如果贸然重新发起一笔新的交易,
            #  如果用的是 相同nonce 必然会导致上一笔交易被覆盖,
            # 如果用的是 pending 的nonce, 在上一笔交易被打包后, 这笔交易必然也失败

            # 判断 该地址是否有pending状态的归集交易, 如果有, 则跳过, 如果没有则正常归集
            pending_clcs = session.query(CollectionRecords) \
                .filter(CollectionRecords.from_address == act_addr.address,
                        CollectionRecords.transaction_status == WithdrawStatus.transaction_status.PENDING) \
                .all()

            if not (pending_clcs is None or len(pending_clcs) == 0):
                logger.info(f'address {act_addr.address} had a pending tx, skipped it this time ')
                continue

            # 判断是否有正在给这个地址补充手续费
            fee_pending = session.query(CollectionRecords) \
                .filter(CollectionRecords.to_address == act_addr.address,
                        CollectionRecords.transaction_status == WithdrawStatus.transaction_status.PENDING,
                        CollectionRecords.collection_type == CollectionType.FEE
                        ) \
                .all()

            if not (fee_pending is None or len(fee_pending) == 0):
                logger.info(f'address {act_addr.address} had a pending FEE tx, skipped it this time ')
                continue

            hrc20_contract = ''
            hrc20_decimals = 18
            for con_addr, sym_info in HRC20_CONTRACT_MAP.items():
                if sym_info['symbol'] == 'BTU':
                    hrc20_contract = con_addr
                    hrc20_decimals = sym_info['decimal']

            assert len(hrc20_contract) == 43, 'hrc20_contract is illegal'
            assert hrc20_decimals == 18, 'hrc20_deciaml not equal 18'

            address = addr.address
            str_hrc20_balance = rpc.getHRC20TokenBalance(contract_addr=hrc20_contract, address=address)
            token_balance = round_down(Decimal(str_hrc20_balance))

            # 判断地址的(链上)余额是否满足归集条件
            if token_balance < clc_cfg.min_amount_to_collect:
                logger.info(f'{addr.address}, BTU balance:{token_balance} is less than min_amount_to_collect')
                continue


            logger.info(f'active address: {act_addr}')

            str_htdf_balance = rpc.getBalance(strAddr=address)
            htdf_balance = round_down( Decimal(str_htdf_balance) )

            fee_amount = Decimal('0.20')
            if htdf_balance <  fee_amount:
                logger.info(f'{address}, HTDF balance : {htdf_balance} is not enough too pay fee. start supply fee')
                nettype = 'mainnet' if g_IS_MAINNET else 'testnet'
                priv_key, fee_addr = gen_bip44_subprivkey_from_mnemonic(mnemonic=g_MNEMONIC,
                                                                        coin_type='HTDF',
                                                                        account_index=addr.pro_id,
                                                                        address_index=100000000,
                                                                        nettype=nettype)
                logger.info(f'fee address is {fee_addr}')


                str_fee_addr_htdf_balance = rpc.getBalance(strAddr=fee_addr)
                fee_addr_htdf_balance = round_down(Decimal(str_fee_addr_htdf_balance))
                if fee_addr_htdf_balance < fee_amount * Decimal(10.0):
                    # 手续费地址的ETH余额不够, 发送短信通知
                    sms_template = '【shbao】 尊敬的管理员，余额报警。{0}归集手续费地址{1}余额为{2}，已影响正常归集，请立即充值{3}。{4},{5}'
                    sms_content = sms_template.format('BTU', 'HTDF', str_fee_addr_htdf_balance, 'HTDF', str(datetime.now()),
                                                      ENV_NAME.upper())

                    proj = session.query(Project).filter_by(pro_id=clc_cfg.pro_id).first()
                    assert isinstance(proj, Project), 'proj is not Project'

                    sms_content += ',{0}'.format(proj.pro_name)
                    send_sms_queue(sms_content=sms_content, tel_no=proj.tel_no)

                    logger.warning(sms_content)
                    continue
                elif fee_addr_htdf_balance < fee_amount * 30:
                    # 手续费地址的ETH余额不够, 发送短信通知
                    sms_template = '【shbao】 尊敬的管理员，手续费余额预警。{0}归集手续费地址{1}余额为{2}，请立即充值{3}。{4},{5}'
                    sms_content = sms_template.format('BTU', 'HTDF', str_fee_addr_htdf_balance, 'HTDF', str(datetime.now()),
                                                      ENV_NAME.upper())
                    proj = session.query(Project).filter_by(pro_id=clc_cfg.pro_id).first()
                    assert isinstance(proj, Project), 'proj is not Project'
                    sms_content += ',{0}'.format(proj.pro_name)
                    send_sms_queue(sms_content=sms_content, tel_no=proj.tel_no)
                    logger.warning(sms_content)
                    pass
                else:
                    pass

                time.sleep(7)
                trans_rsp = htdf_transfer(priv_key=priv_key,
                                          from_addr=fee_addr,
                                          to_addr=address,
                                          amount_in_htdf=fee_amount,
                                          memo='shbao'
                                          )

                logger.info(f'tx_hash: {trans_rsp.tx_hash}')

                clc_records = CollectionRecords()
                clc_records.tx_hash = trans_rsp.tx_hash
                clc_records.pro_id = addr.pro_id
                clc_records.token_name = 'HTDF'
                clc_records.amount = round_down(fee_amount)
                clc_records.transaction_status = WithdrawStatus.transaction_status.PENDING
                clc_records.from_address = fee_addr
                clc_records.to_address = address
                clc_records.collection_type = CollectionType.FEE
                clc_records.complete_time = datetime.now()
                # clc_records.block_time = trans_rsp.block_time
                clc_records.block_height = 0

                session.add(instance=clc_records)
                session.flush()

                # 稍后进行监控
                tx_hash_list.append(trans_rsp.tx_hash)

                continue




            # 根据pro_id推导出私钥
            nettype = 'mainnet' if g_IS_MAINNET else 'testnet'
            priv_key, sub_addr = gen_bip44_subprivkey_from_mnemonic(mnemonic=g_MNEMONIC,
                                                                    coin_type='HTDF',
                                                                    account_index=addr.pro_id,
                                                                    address_index=addr.address_index,
                                                                    nettype=nettype)

            if not sub_addr == addr.address.lower():
                # 致命错误, 不可恢复
                raise Exception(f'ADDRESS NOT MATCH! { sub_addr  } != { addr.address.lower()}')
                pass

            collect_amount = token_balance

            if collect_amount < 0.01:
                logger.info('collect_amount is to small, skipped')
                continue

            # 进行转账
            try:
                trans_rsp = hrc20_transfer(priv_key=priv_key,
                                          from_addr=sub_addr, contract_addr=hrc20_contract,
                                          token_recipient=clc_cfg.collection_dst_addr,
                                          token_amount=collect_amount,
                                          token_decimal=hrc20_decimals,
                                          memo='shbao'
                                          )

                logger.info(f'tx_hash: {trans_rsp.tx_hash}')

                clc_records = CollectionRecords()
                clc_records.tx_hash = trans_rsp.tx_hash
                clc_records.pro_id = addr.pro_id
                clc_records.token_name = 'BTU'
                clc_records.amount = round_down(Decimal(collect_amount))
                clc_records.transaction_status = WithdrawStatus.transaction_status.PENDING
                clc_records.from_address = addr.address
                clc_records.collection_type = CollectionType.AUTO
                clc_records.to_address = clc_cfg.collection_dst_addr
                clc_records.complete_time = datetime.now()
                # clc_records.block_time = trans_rsp.block_time
                clc_records.block_height = 0

                session.add(instance=clc_records)
                session.flush()

                # 稍后进行监控
                tx_hash_list.append(trans_rsp.tx_hash)
            except Exception as e:
                logger.error(f'error: {e}')
                time.sleep(1)

            pass



    #3) 监控发出的交易, 获取区块高度等信息, 并修改 交易状态
    sleep_secs = 7
    logger.info(f'waiting  {sleep_secs}s for tx confirmed')
    time.sleep(sleep_secs)



    #4) 获取数据库中所有
    all_pending_txs = session.query(CollectionRecords.tx_hash)\
                    .filter(CollectionRecords.transaction_status == WithdrawStatus.transaction_status.PENDING,
                            CollectionRecords.token_name.in_(['HTDF', 'BTU']) )\
                    .all()

    for item in all_pending_txs:
        tx_hash_list.append( item.tx_hash)



    for tx_hash in tx_hash_list:
        try:
            tx_status = htdf_get_transaction_status(tx_hash=tx_hash)
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
                logger.info('  other situation')
                pass
        except Exception as e:
            logger.error(f'error: {e}')
            time.sleep(1)

        pass

    pass



def main():
    cap_time = 100 if str(ENV_NAME).upper() == 'PRO' else 30
    while True:
        try:
            hrc20_collect()
            time.sleep(10)
            hrc20_collect()
            time.sleep(10)
            hrc20_collect()
            time.sleep(10)
            htdf_collect()
            # break
            for i in range(cap_time):
                logger.info('sleeping....')
                time.sleep(6)  # 10分钟归集一次
        except Exception as e:
            logger.error(f'{e}')


    pass


if __name__ == '__main__':

    main()