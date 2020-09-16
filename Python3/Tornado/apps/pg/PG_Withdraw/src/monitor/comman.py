import json
import time

import requests
from ed25519 import SigningKey

from src.config.constant import WithdrawStatus
from src.lib.pg_utils import decimal_to_str, datetime_to_timestamp
from src.model.model import WithdrawOrder, Project
from src.monitor import NotifyFuncResponse
from src.monitor.btc.btc_utils import btc_get_transaction_status
from src.monitor.eth_erc20.eth_utils import eth_get_transaction_status
from src.monitor.htdf.htdf_utils import htdf_get_transaction_status
# from src.monitor.tx_monitor_notify import NotifyFuncResponse




def handler(session , serial_id : str, logger):

    # 检验是否通过
    # req_params_tx_hash = Schema(schema=withdraw_body_schema).validate(data=rst)

    assert  isinstance(serial_id, str), 'serial_id is invalid'

    # 监控
    order_data = session.query(WithdrawOrder)\
                            .filter_by(serial_id=serial_id)\
                            .first()

    assert  isinstance(order_data, WithdrawOrder)

    logger.info(f'order_data :{order_data}')

    #如果  transaction_status 状态是 PENDING 才重新查询交易, 其他情况 不必查询交易
    if not( order_data.transaction_status == WithdrawStatus.transaction_status.PENDING ):
        logger.info(f"serial_id : {serial_id} transaction_status is {order_data.transaction_status} , no need get_transaction_status")
        order_data_new = order_data
    else: #交易还是 PENDING 状态
        if order_data.token_name.upper() in ['HTDF', 'BTU']:
            time.sleep(5)
            result_obj = htdf_get_transaction_status( order_data.tx_hash )
        elif order_data.token_name.upper() == 'ETH' or order_data.token_name == 'USDT':
            result_obj =  eth_get_transaction_status(order_data.tx_hash)
        elif order_data.token_name.upper() == 'BTC':
            result_obj = btc_get_transaction_status(order_data.tx_hash)
        else:
            raise Exception(f"not support token_name :{order_data.token_name }")


        update_fields = {
            "block_height": result_obj.block_height,
            "transaction_status": result_obj.transaction_status,
            # "block_time": result_obj.block_time,
            # "tx_confirmations": result_obj.confirmations
        }

        if result_obj.transaction_status == WithdrawStatus.transaction_status.SUCCESS \
           or result_obj.transaction_status == WithdrawStatus.transaction_status.FAIL:
            update_fields['block_time'] = result_obj.block_time
            update_fields['tx_confirmations'] = result_obj.confirmations
            #这里不修改complete_time,  等通知完成了再修改



        update_block_data = session.query(WithdrawOrder) \
                                    .filter_by(serial_id=serial_id) \
                                    .update(update_fields)

        # session.commit()
        session.flush()
        logger.info(f'update_block_data sql :{update_block_data}')

        # 重新查询一遍 获取最新的订单数据 !
        order_data_new = session.query(WithdrawOrder) \
            .filter_by(serial_id=serial_id) \
            .first()



    assert isinstance(order_data_new, WithdrawOrder)

    logger.info(f'order_data_new :{order_data_new}')

    # 如果一笔仍是 PENDING , 并且第一次通知已经成功, 则不重复通知
    if order_data_new.transaction_status == WithdrawStatus.transaction_status.PENDING \
            and order_data_new.notify_status == WithdrawStatus.notify_status.FIRSTSUCCESS:
        logger.info('serial_id:{} is PENDING and notify_status is FIRSTSUCCESS ,  '
                    'do not notify any more until transaction_status changed')
        return


    notify_req_data = {
        "serial_id": order_data_new.serial_id,
        "pro_id": order_data_new.pro_id,
        "order_id": order_data_new.order_id,
        "token_name": order_data_new.token_name,
        "from_addr": order_data_new.from_addr,
        "to_addr": order_data_new.to_addr,
        "amount": decimal_to_str(order_data_new.amount),
        'remark' : order_data.remark if order_data.remark is not None else '',
        "status": order_data_new.transaction_status,
        "tx_hash": order_data_new.tx_hash,
        "block_height": order_data_new.block_height,
        "block_time": datetime_to_timestamp( order_data_new.block_time) \
                        if order_data.block_time is not None else None,
        # "memo": order_data_new.memo,
        'transaction_status': order_data_new.transaction_status
    }


    qret = session.query(Project.server_sign_key).filter_by(pro_id=order_data.pro_id).first()
    svr_sign_key = qret.server_sign_key


    ret_info = notify_withdraw_to_outer_project(callback_url=order_data_new.callback_url,
                                                req_data=notify_req_data, logger=logger,
                                                svr_sign_key=svr_sign_key)

    fields_update = {
        "notify_times": order_data_new.notify_times + 1
    }

    if ret_info.is_notify_successed:
        #交易成功,并且第二次通知成功,订单状态才能成功
        if(order_data_new.transaction_status == 'SUCCESS'):
            fields_update['order_status'] = WithdrawStatus.order_status.SUCCESS
            fields_update['notify_status'] = WithdrawStatus.notify_status.SECONDSUCCESS
            fields_update['complete_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        elif(order_data_new.transaction_status == "FAIL"):
            fields_update['notify_status'] = WithdrawStatus.notify_status.SECONDSUCCESS
            fields_update['complete_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            fields_update['order_status'] = WithdrawStatus.order_status.FAIL
        elif(order_data_new.transaction_status == "PENDING"):
            fields_update['notify_status'] = WithdrawStatus.notify_status.FIRSTSUCCESS
    else:
        #交易失败,并且第二次通知成功,订单状态才失败
        if (order_data_new.transaction_status == 'SUCCESS' or order_data_new.transaction_status == "FAIL"):
            fields_update['notify_status'] = WithdrawStatus.notify_status.SECONDFAIL

            #2020-07-02 added by yqq
            #如果项目方不实现回调接口, 导致一直通知失败, 则直接将通知状态改为成功
            if order_data_new.notify_times + 1 >= 150:
                fields_update['notify_status'] = WithdrawStatus.notify_status.SECONDSUCCESS
                fields_update['complete_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                fields_update['remark'] = '24小时内回调通知项目方均无响应'

                if order_data_new.transaction_status == WithdrawStatus.transaction_status.SUCCESS:
                    fields_update['order_status'] = WithdrawStatus.order_status.SUCCESS
                else:
                    fields_update['order_status'] = WithdrawStatus.order_status.FAIL

        elif(order_data_new.transaction_status == "PENDING"):
            fields_update['notify_status'] = WithdrawStatus.notify_status.FIRSTFAIL



    update_notify_status = session.query(WithdrawOrder) \
                                    .filter_by(serial_id=serial_id) \
                                    .update(fields_update)

    # session.commit()
    session.flush()
    logger.info(f'update_notify_status sql:{update_notify_status}')

    logger.info(f"handle  {serial_id} finished.")

    pass



def notify_withdraw_to_outer_project( callback_url : str, req_data : dict,
                                      logger, svr_sign_key : str )-> NotifyFuncResponse:
    """
    提币回调通知统一接口
    :param serial_id:
    :return:
    """
    api_name = 'notifywithdraw'
    timestamp_str = str(int(time.time() * 1000))
    data_json_str = json.dumps(req_data, separators=(',', ':'), sort_keys=True)  # 按照key字母顺序排序
    join_str = '|'.join([timestamp_str, api_name, data_json_str])
    sign_msg_bytes = join_str.encode('utf8')
    sk = SigningKey(sk_s=svr_sign_key.encode('utf8'), prefix='', encoding='hex')
    signature_bytes = sk.sign(msg=sign_msg_bytes, prefix='', encoding='hex')
    signature_str = signature_bytes.decode('utf8')
    # print('json_str:{}'.format(data_json_str))

    req_headers = {
        'User-Agent' : 'shbao/1.0',  #自定义User-Agent
        'PG_NOTIFY_TIMESTAMP': timestamp_str,
        'PG_NOTIFY_SIGNATURE': signature_str
    }

    ret_info = NotifyFuncResponse()
    ret_info.is_notify_successed = False

    try:
        send_notify_rst = requests.post(url=callback_url, json=req_data, headers=req_headers, timeout=5)
        logger.info(send_notify_rst)

        http_status_code = send_notify_rst.status_code
        if http_status_code == 204 or http_status_code == 200:
            ret_info.is_notify_successed = True
    except Exception as e:
        logger.error('{}'.format(e))
        ret_info.is_notify_successed = False


    return ret_info
