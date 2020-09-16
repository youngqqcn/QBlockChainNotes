#!coding:utf8

#author:yqq
#date:2020/5/20 0020 13:41
#description:  ERC20代币归集



import decimal
import json
import time
from datetime import datetime
from decimal import Decimal

import pika
from eth_utils.units import units
from web3 import Web3, HTTPProvider
from eth_typing import HexStr
from eth_utils import to_checksum_address
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

from src.collectors.eth.eth_transfer_utils import eth_transfer, erc20_transfer
from src.collectors.eth.my_eth_utils import eth_get_transaction_status
from src.collectors.eth.token_abi.abi import EIP20_ABI
from src.collectors.htdf.htdf_transfer_utils import htdf_transfer
from src.collectors.htdf.htdf_utils import htdf_get_transaction_status
from src.collectors.htdf.proxy import HTDFProxy
from src.config.constant import g_MNEMONIC, WithdrawStatus, CollectionType, ETH_FULL_NODE_RPC_URL, \
    ERC20_USDT_CONTRACT_ADDRESS, MYSQL_CONNECT_INFO, RABBIT_MQ_USER_NAME, RABBIT_MQ_PASSWORD, RABBIT_MQ_VRIATUAL_HOST, \
    RABBIT_MQ_PORT, RABBIT_MQ_IP, RABBIT_MQ_HEARTBEAT_TIME, RABBIT_BLOCKED_CONNECTION_TIMEOUT, SMS_EXCHANGE, \
    RABBIT_DIRECT_MODE, Q_SMS, SMS_ROUTINGKEY, RABBIT_DELIVERY_MODE, ENV_NAME, g_IS_MAINNET, ETH_ERC20_GAS_PRICE, \
    ERC20_GAS_LIMIT
from src.lib.addr_gen.htdf_addr_gen import bech32_decode
from src.lib.my_bip44.wrapper import gen_bip44_subprivkey_from_mnemonic
from src.model.model import ActiveAddressBalance, CollectionConfig, Address, CollectionRecords, Project

import logging
import traceback


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
    if isinstance(decim, Decimal):
        decimalFormat = decim.quantize(Decimal("0.00000000"), getattr(decimal, 'ROUND_DOWN'))
    # elif isinstance(decim, int):
    else:
        decimalFormat = Decimal(str(decim)).quantize(Decimal("0.00000000"), getattr(decimal, 'ROUND_DOWN'))
    return decimalFormat


def send_sms_queue(sms_content: str, tel_no : str) -> None:
    '''
    发送短信
    :param tx_hash:
    :return:
    '''
    logger.info(f'tel_no:{tel_no}, sms_content:{sms_content}')

    credentials = pika.PlainCredentials(RABBIT_MQ_USER_NAME, RABBIT_MQ_PASSWORD)
    # 创建连接
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        RABBIT_MQ_IP, RABBIT_MQ_PORT, RABBIT_MQ_VRIATUAL_HOST, credentials,
        heartbeat = RABBIT_MQ_HEARTBEAT_TIME,
        blocked_connection_timeout = RABBIT_BLOCKED_CONNECTION_TIMEOUT
    ))

    channel = connection.channel()


    # 单条模式
    channel.exchange_declare(SMS_EXCHANGE, RABBIT_DIRECT_MODE)
    # 创建一个新队列balance，设置durable=True 队列持久化，注意不要跟已存在的队列重名，否则有报错
    channel.queue_declare(queue=Q_SMS, durable=True)

    # 绑定队列与交换器
    channel.queue_bind(exchange=SMS_EXCHANGE, queue=Q_SMS)

    # 发送消息
    # n RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange.
    channel.basic_publish(exchange=SMS_EXCHANGE,
                          routing_key=SMS_ROUTINGKEY,
                          body=f'{json.dumps({"msg_content":sms_content, "tel_no":tel_no})}',
                          properties=pika.BasicProperties(
                              delivery_mode=RABBIT_DELIVERY_MODE,  # 使消息或任务也持久化存储
                          ))
    logger.info('send msg to sms queue successed.')



def collect_erc20_usdt():
    """
    开始归集
    :return:
    """

    # 1) 查询 tb_active_address_balances 表获取符合归集条件的地址
    engine = create_engine(MYSQL_CONNECT_INFO,
                           max_overflow=0,
                           pool_size=5,
                           pool_pre_ping=True, pool_recycle=360
                           )
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=True)  # 增删改操作 需要手动flush,
    session = Session()

    query_sets = session.query(CollectionConfig, ActiveAddressBalance, Address) \
        .filter(ActiveAddressBalance.token_name == 'USDT', CollectionConfig.token_name=='USDT') \
        .filter(CollectionConfig.pro_id == ActiveAddressBalance.pro_id) \
        .filter(Address.address == ActiveAddressBalance.address) \
        .filter(ActiveAddressBalance.balance >= CollectionConfig.min_amount_to_collect) \
        .all()

    logger.info(f'USDT collection query_sets size is {len(query_sets)}')

    tx_hash_list = []  # 保存本次广播的tx_hash 用于后面监控
    if not (query_sets is None or len(query_sets) == 0):
        logger.info(f'query_sets size is  {len(query_sets)} ')


        myweb3 = Web3(provider=HTTPProvider(endpoint_uri=ETH_FULL_NODE_RPC_URL))
        # https://web3py.readthedocs.io/en/stable/web3.eth.account.html?highlight=transaction
        # https://web3py.readthedocs.io/en/stable/web3.eth.account.html?highlight=transaction#sign-a-transaction


        # 2) 遍历地址列表进行转账操作, 并插入归集记录表
        for clc_cfg, act_addr, addr in query_sets:

            logger.info(f'active address is {act_addr}')

            try:
                assert isinstance(clc_cfg, CollectionConfig)
                assert isinstance(act_addr, ActiveAddressBalance)
                assert isinstance(addr, Address)

                if not is_valid_eth_address(clc_cfg.collection_dst_addr):
                    logger.error(f'invalid collection dst address : {clc_cfg.collection_dst_addr}')
                    continue

                #  如果一笔交易早已经广播出去, 但是一直没有被打包, 此时如果贸然重新发起一笔新的交易,
                #  如果用的是 相同nonce 必然会导致上一笔交易被覆盖,
                # 如果用的是 pending 的nonce, 在上一笔交易被打包后, 这笔交易必然也失败

                # 判断 该地址是否有pending状态的归集交易, 如果有, 则跳过, 如果没有则正常归集
                pending_clcs = session.query(CollectionRecords)\
                                .filter( CollectionRecords.from_address == act_addr.address ,
                                        CollectionRecords.transaction_status == WithdrawStatus.transaction_status.PENDING)\
                                .all()

                if not( pending_clcs is None or len(pending_clcs) == 0 ):
                    logger.info(f'address {act_addr.address} had a pending tx, skipped it this time ')
                    continue


                #判断是否有正在给这个地址补充手续费
                fee_pending = session.query(CollectionRecords)\
                                    .filter(CollectionRecords.to_address == act_addr.address,
                                        CollectionRecords.transaction_status == WithdrawStatus.transaction_status.PENDING,
                                        CollectionRecords.collection_type == CollectionType.FEE
                                            )\
                                    .all()

                if not( fee_pending is None or len(fee_pending) == 0 ):
                    logger.info(f'address {act_addr.address} had a pending FEE tx, skipped it this time ')
                    continue


                address = addr.address
                act_chksum_address = to_checksum_address(address)  # 必须使用 checksum addres
                # block_identifier =
                # nonce = myweb3.eth.getTransactionCount(act_chksum_address, block_identifier=block_identifier)
                balance = myweb3.eth.getBalance(account=act_chksum_address, block_identifier=HexStr('pending'))
                decim_eth_balance = myweb3.fromWei(balance, 'ether')


                #获取其 ERC20_USDT的余额
                chksum_contract_addr = to_checksum_address(ERC20_USDT_CONTRACT_ADDRESS)
                contract = myweb3.eth.contract(address=chksum_contract_addr, abi=EIP20_ABI)
                # symbol = contract.functions.symbol().call()
                # decimals = contract.functions.decimals().call()
                erc20_token_balance_int = contract.functions.balanceOf(to_checksum_address(address)).call()
                erc20_token_balance = myweb3.fromWei(erc20_token_balance_int, 'mwei')

                #有可能为 0
                if isinstance( erc20_token_balance , int):
                    erc20_token_balance =  Decimal(str(erc20_token_balance))

                token_balance = round_down(erc20_token_balance)

                if token_balance < clc_cfg.min_amount_to_collect:
                    logger.info(f'{act_chksum_address},USDT token balance:{token_balance} is less than min_amount_to_collect')
                    continue


                logger.info(f'{act_chksum_address},USDT token balance:{token_balance} , start to collect ...')


                #判断其ETH余额是否够手续费, 如果ETH余额不够手续费, 则进行补充手续费
                min_erc20_tx_fee = Web3.fromWei(int(ETH_ERC20_GAS_PRICE * 10 ** 9 * ERC20_GAS_LIMIT), 'ether')
                if decim_eth_balance < min_erc20_tx_fee:
                    logger.info(f'{act_chksum_address}, ETH balance : {decim_eth_balance} is not enough too pay fee. start supply fee')

                    # 根据pro_id推导出手续费地址的私钥
                    nettype = 'mainnet' if g_IS_MAINNET else 'testnet'
                    priv_key, fee_addr = gen_bip44_subprivkey_from_mnemonic(mnemonic=g_MNEMONIC,
                                                                            coin_type='ETH',
                                                                            account_index=addr.pro_id,
                                                                            address_index=100000000,
                                                                            nettype=nettype)


                    fee_amount = min_erc20_tx_fee
                    logger.info(f'fee addreess:{fee_addr}')
                    fee_chksum_address = to_checksum_address(fee_addr)

                    #判断手续费地址的ETH,
                    eth_balance_in_wei = myweb3.eth.getBalance(account=fee_chksum_address, block_identifier=HexStr('pending'))

                    eth_balance = myweb3.fromWei(eth_balance_in_wei, 'ether')
                    logger.info(f'fee addreess ETH balance :{eth_balance}')
                    if eth_balance < fee_amount * 3:
                        #手续费地址的ETH余额不够, 发送短信通知
                        sms_template = '【shbao】 尊敬的管理员，余额报警。{0}归集手续费地址{1}余额为{2}，已影响正常归集，请立即充值{3}。{4},{5}'
                        sms_content = sms_template.format('USDT', 'ETH', eth_balance, 'ETH', str(datetime.now()),
                                                                ENV_NAME.upper())

                        proj = session.query(Project).filter_by(pro_id=clc_cfg.pro_id).first()
                        assert isinstance(proj, Project), 'proj is not Project'

                        sms_content += ',{0}'.format(proj.pro_name)
                        send_sms_queue(sms_content=sms_content, tel_no=proj.tel_no)

                        logger.warning(sms_content)
                        continue
                    elif eth_balance < fee_amount * 15:
                        #手续费地址的ETH余额不够, 发送短信通知
                        sms_template = '【shbao】 尊敬的管理员，手续费余额预警。{0}归集手续费地址{1}余额为{2}，请立即充值{3}。{4},{5}'
                        sms_content = sms_template.format('USDT', 'ETH', eth_balance, 'ETH', str(datetime.now()),
                                                          ENV_NAME.upper())
                        proj = session.query(Project).filter_by(pro_id=clc_cfg.pro_id).first()
                        assert isinstance(proj, Project), 'proj is not Project'
                        sms_content += ',{0}'.format(proj.pro_name)
                        send_sms_queue(sms_content=sms_content, tel_no=proj.tel_no)
                        logger.warning(sms_content)
                        pass


                    trans_rsp = eth_transfer(priv_key=priv_key,
                                             from_addr=fee_addr,
                                             to_addr=act_chksum_address, amount=fee_amount)

                    clc_records = CollectionRecords()
                    clc_records.tx_hash = trans_rsp.tx_hash
                    clc_records.pro_id = addr.pro_id
                    clc_records.token_name = 'ETH'  #addr.token_name
                    clc_records.amount = round_down(fee_amount)
                    clc_records.transaction_status = WithdrawStatus.transaction_status.PENDING
                    clc_records.from_address = fee_addr
                    clc_records.collection_type = CollectionType.FEE
                    clc_records.to_address = addr.address
                    clc_records.complete_time = datetime.now()
                    # clc_records.block_time = trans_rsp.block_time
                    clc_records.block_height = 0

                    # session = Session()
                    session.add(instance=clc_records)
                    session.flush()

                    # 稍后进行监控
                    tx_hash_list.append(trans_rsp.tx_hash)
                    continue


                #如果 ETH余额 够付手续费, 则直接进行ERC20代币归集
                logger.info(f'active address: {act_addr}')

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

                collect_amount = token_balance  #decim_balance - Decimal('0.00042')  # 20*10**9 * 21000 / 10**18


                # 进行转账
                trans_rsp = erc20_transfer(priv_key=priv_key,
                               from_addr=sub_addr,
                               contract_addr=ERC20_USDT_CONTRACT_ADDRESS,
                               token_recipient_addr=clc_cfg.collection_dst_addr,
                               token_amount=collect_amount)

                logger.info(f'tx_hash: {trans_rsp.tx_hash}')

                clc_records = CollectionRecords()
                clc_records.tx_hash = trans_rsp.tx_hash
                clc_records.pro_id = addr.pro_id
                clc_records.token_name = 'USDT' #addr.token_name
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
                traceback.print_exc()
                pass



    # 3) 监控发出的交易, 获取区块高度等信息, 并修改 交易状态
    # 4) 获取数据库中所有
    all_pending_txs = session.query(CollectionRecords.tx_hash) \
        .filter(CollectionRecords.transaction_status == WithdrawStatus.transaction_status.PENDING,
                CollectionRecords.token_name.in_(['USDT','ETH'])) \
        .all()

    for item in all_pending_txs:
        tx_hash_list.append(item.tx_hash)


    logger.info(f' tx_hash_list  size is {len(tx_hash_list)}')
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
            collect_erc20_usdt()
            # break
            for i in range(100):
                logger.info('sleeping....')
                time.sleep(6)  # 10分钟归集一次
        except Exception as e:
            logger.error(f'{e}')

    pass


if __name__ == '__main__':
    main()