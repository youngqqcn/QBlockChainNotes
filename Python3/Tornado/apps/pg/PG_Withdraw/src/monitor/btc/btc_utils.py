#!coding:utf8

#author:yqq
#date:2020/7/10 0010 20:48
#description:
import json
import time

import logging
import datetime
import requests

from src.config.constant import WithdrawStatus, BTC_API_HOST, BTC_API_PORT
from src.consumers.btc.btc_proxy import BTCProxy, BadStatusCodeError
from src.lib.exceptions import MqBodyException
from src.monitor import SubMonitorFuncResponse




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
    ret_info.block_time = datetime.datetime.now()

    try:
        txinfo = btcproxy.get_transaction(txid=tx_hash)

        if txinfo['status']['confirmed']:

            latest_height = btcproxy.get_latest_height()

            # 成功监控到
            ret_info.block_height = txinfo['status']['block_height']
            ret_info.block_time = datetime.datetime.fromtimestamp(txinfo['status']['block_time'])
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




def main():
    global BTC_API_PORT
    BTC_API_PORT = 3001

    tx_hash='0bcee73f43fb2f052f647663faea554b65a71f8947dbbf31852fe25b0241922d'
    ret = btc_get_transaction_status(tx_hash=tx_hash)


    pass


if __name__ == '__main__':

    main()