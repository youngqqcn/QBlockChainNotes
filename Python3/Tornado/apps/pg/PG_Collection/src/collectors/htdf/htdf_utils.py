#!coding:utf8

#author:yqq
#date:2020/5/10 0010 21:06
#description:
import json
import time

import logging
import datetime
import requests

from src.config.constant import WithdrawStatus, SubMonitorFuncResponse, HTDF_RPC_HOST
from src.lib.exceptions import MqBodyException



def htdf_get_transaction_status(tx_hash : str) -> SubMonitorFuncResponse:
    """
    获取htdf的交易状态,
    :param rst:
    :return: True: 成功,  False 失败
    """

    monitor_url = f'http://{HTDF_RPC_HOST}/txs/' + tx_hash

    logging.info(f'monitor_url method: GET {monitor_url}')
    monitor_rst = requests.get(monitor_url)
    logging.info(f'monitor_rst:{monitor_rst}')

    # 判断进来格式是否正确
    rsp_tx  = json.loads(monitor_rst.text, encoding='utf8')


    if not isinstance(rsp_tx, dict):
        #TODO: 这种情况, 怎么复现?
        raise Exception(f"rsp_tx format error")

    # 把时间转换成正确格式
    times = rsp_tx["timestamp"]
    d1 = datetime.datetime.strptime(times, '%Y-%m-%dT%H:%M:%SZ')
    logging.info("d1:%s" % (d1))
    delta = datetime.timedelta(hours=8)
    n_time = d1 + delta
    logging.info('n_time: %s' % (n_time))

    if  rsp_tx["logs"][0]["success"] == False:
        ret_info = SubMonitorFuncResponse()
        ret_info.block_height = rsp_tx["height"]
        ret_info.block_time = n_time #rsp_tx["timestamp"]
        ret_info.tx_hash = rsp_tx['txhash']
        ret_info.confirmations = 0
        ret_info.transaction_status = WithdrawStatus.transaction_status.FAIL
        return ret_info



    # 成功监控到
    ret_info = SubMonitorFuncResponse()
    ret_info.block_height = rsp_tx["height"]
    ret_info.block_time = n_time
    ret_info.tx_hash = rsp_tx['txhash']
    ret_info.confirmations = 1
    ret_info.transaction_status = WithdrawStatus.transaction_status.SUCCESS
    return ret_info



