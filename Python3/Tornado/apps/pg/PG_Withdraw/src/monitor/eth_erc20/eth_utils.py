#!coding:utf8

#author:yqq
#date:2020/5/11 0011 15:41
#description:  eth 和 erc20  交易状态获取


import logging
from datetime import datetime

from eth_typing import HexStr, BlockNumber
from web3 import Web3, HTTPProvider
from web3.datastructures import AttributeDict
from web3.exceptions import TimeExhausted, TransactionNotFound
from web3.types import TxReceipt, BlockData, TxData

from src.config.constant import WithdrawStatus, ETH_FULL_NODE_RPC_URL, g_IS_MAINNET, ETH_CHAIN_ID
from src.lib.pg_utils import timestamp_to_datatime
from src.monitor import SubMonitorFuncResponse

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s:%(funcName)s:%(lineno)d %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def eth_get_transaction_status(tx_hash : str) -> SubMonitorFuncResponse:
    """
     如果交易查不到, 怎么处理???  需要先根据 txid 获取, 如果获取不到, 就代表交易已经不在交易池中
     (1) 通过 getTransaction 查询不到, 并不代表交易已经失败, 因为交易会被移到 future queue中
     (2) 如果 getTransaction能够查询到交易,且 getTransactionReceipt能够获取到交易, 如果status为 0, 则ERC20交易为失败的

    情况(1), 如何判定一笔为失败的?


    :param tx_hash:
    :return:
    """

    myweb3 = Web3(provider=HTTPProvider(endpoint_uri=ETH_FULL_NODE_RPC_URL))

    rsp = SubMonitorFuncResponse()
    rsp.transaction_status = WithdrawStatus.transaction_status.PENDING  # 广播出去了, 就是pending
    rsp.confirmations = 0
    rsp.block_height = 0
    rsp.tx_hash = HexStr( tx_hash  )
    rsp.block_time = datetime.now()
    try:

        for i in range(1):
            # 首先根据 tx_hash 通过  getTransaction接口获取交易,
            #  如果交易的 blockHash, blockNumber为 null, 则说明交易还在 pending状态
            #  返回的是 null, 说明交易已经从交易池 移除!  处理异常 TransactionNotFound

            tx_data = myweb3.eth.getTransaction(rsp.tx_hash)
            assert isinstance(tx_data, AttributeDict), 'tx_data is not AttributeDict'

            if tx_data['blockNumber'] is None:
                logger.info(f"tx_hash:{tx_hash} is pending")
                break
                # raise Exception(f"tx_hash:{tx_hash} is pending")

            # receipt = myweb3.eth.waitForTransactionReceipt(
            #     transaction_hash= rsp.tx_hash,
            #     timeout=30,  # 超时时间 秒 , 没查到就抛异常 web3.exceptions.TimeExhausted
            #     poll_latency=1  # 每隔多少秒 请求一次
            # )

            receipt = myweb3.eth.getTransactionReceipt(transaction_hash=rsp.tx_hash)
            logger.info(receipt)
            assert receipt is not  None, 'receipt is None'

            # 如果提币交易的区块确认数小于3个, 则继续等待
            latest_block_number = myweb3.eth.blockNumber
            if isinstance(latest_block_number, int):
                MIN_CONFIRMATIONS = 3
                if latest_block_number - receipt['blockNumber'] < MIN_CONFIRMATIONS:
                    logger.info(f'tx_hash:{tx_hash} is confirmations is less than {MIN_CONFIRMATIONS}, '
                                f'so keep waiting for more confirmations ')
                    break
            else:
                logger.error('get latest blocknumber failed')
                raise Exception('get latest blocknumber failed')


            if receipt['status'] == 1:
                rsp.transaction_status = WithdrawStatus.transaction_status.SUCCESS
            else:
                rsp.transaction_status = WithdrawStatus.transaction_status.FAIL

            rsp.block_height = receipt['blockNumber']

            # 如果是测试 并且是Rinkeby测试网络 , 需要加入一个中间件
            if not g_IS_MAINNET and ETH_CHAIN_ID == 4:
                from web3.middleware import geth_poa_middleware
                myweb3.middleware_onion.inject(element=geth_poa_middleware, layer=0)



            block_data = myweb3.eth.getBlock(block_identifier=BlockNumber(rsp.block_height),
                                             full_transactions=False)

            assert isinstance(block_data, AttributeDict)
            rsp.block_time = timestamp_to_datatime(block_data.timestamp)

            rsp.confirmations =  latest_block_number - rsp.block_height

    except TransactionNotFound as e:
        # getTransaction(tx_hash)返回 null,  交易未找到, 说明已经从交易池 移除!
        rsp.transaction_status = WithdrawStatus.transaction_status.FAIL
        pass

    except TimeExhausted as e:
        #如果获取交易失败
        logger.info(f'{e}')
        pass
    except Exception as e:
        logger.error(f'{e}')

    logger.info(f'eth_get_transaction_status  finished, rsp:{rsp}')

    return  rsp
