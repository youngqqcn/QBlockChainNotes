#!coding:utf8

#author:yqq
#date:2020/5/7 0007 13:47
#description:  查询订单信息
#
#
import json
import math
from datetime import datetime
from typing import Union

from schema import And, Schema
from tornado.web import authenticated

from src.api.handlers.handler_base import BaseHandler, apiauth
import logging

#使用 sqlalchemy 进行 ORM
from sqlalchemy import create_engine, and_, func
from sqlalchemy.orm import sessionmaker

from src.config.constant import MYSQL_CONNECT_INFO, g_TOKEN_NAME_LIST, WithdrawStatus
from src.lib.my_apiauth.my_ed25519 import verify_sig
from src.model.model import WithdrawOrder

from src.lib.pg_utils import decimal_to_str, datetime_to_timestamp

logger = logging.getLogger(__name__)



class QueryWithdrawOrder(BaseHandler):
    """
    @api {POST} http://192.168.10.174/api/withdraw/querywithdraworder  3.3.查询提币订单详情
    @apiVersion 0.0.1
    @apiName  querywithdraworder
    @apiGroup 3.PG_Withdraw
    @apiDescription 查询提币订单详情

    @apiParam {Integer} pro_id 项目方ID
    @apiParam {String} serial_id  流水号

    @apiParamExample {json} 请求参数示例:
    {
        "pro_id": 3,
        "serial_id": "202005281833079967716"
    }

    @apiSuccess {Integer} err_code  错误码
    @apiSuccess {String} err_msg 错误信息
    @apiSuccess {Integer} timestamp  时间戳
    @apiSuccess {Object} data 订单数据
    @apiSuccess {Integer}  data.pro_id  项目方id
    @apiSuccess {String}   data.serial_id  序列号(支付网关生成的唯一的标识)
    @apiSuccess {String}   data.order_id 订单号(即项目方发起提币请求时提交的order_id)
    @apiSuccess {String}   data.token_name  币种名
    @apiSuccess {String}   data.from_addr  源地址
    @apiSuccess {String}   data.to_addr   目的地址
    @apiSuccess {String}   data.tx_hash  交易哈希(或称交易ID)
    @apiSuccess {Integer}  data.block_time   区块时间 (如果没有区块时间则为 null )
    @apiSuccess {Integer}  data.block_height   区块高度
    @apiSuccess {Integer}  data.tx_confirmations   区块确认数
    @apiSuccess {Integer}  data.complete_time   完成时间(如果订单未完成则为 null )
    @apiSuccess {String}   data.order_status   提币订单状态 (PROCESSING:订单处理中, SUCCESS:订单已成功, FAIL:订单已失败 )
    @apiSuccess {String}   data.transaction_status   转账交易状态(NOTYET:尚未转账, PENDING:已汇出, FAIL:交易失败 SUCCESS:交易成功 )
    @apiSuccess {String}   data.callback_url  回调通知地址, 当订单状态改变时主动通知项目方,项目方必须提供通知接口的url, 详细说明请看"公共参数说明"
    @apiSuccess {String}   data.memo     交易备注(区块链上交易中的memo)
    @apiSuccess {String}   data.remark  备注

    @apiSuccessExample {json} Success-Example:
    HTTP/1.1 200 OK
    {
        "err_code": 0,
        "err_msg": null,
        "timestamp": 1591341255875,
        "data": {
            "pro_id": 1,
            "serial_id": "202005281833079967716",
            "order_id": "21488153467324656239",
            "from_addr": "htdf1vhq6c38demm58cnevc4sntc77z8ppvl85mj0a6",
            "to_addr": "htdf1ewfage0jv8m4wsv7w3nhg9xar2d9qj9mh4c8m8",
            "amount": "0.10031000",
            "tx_confirmations": 1,
            "block_height": 859422,
            "block_time": 1590662008,
            "tx_hash": "86B084D97617C288AEEE22E2234F0572EFB96011CEF2A8E3348319ED83CAE4BE",
            "callback_url": "http://192.168.10.29:8001/notifywithdraw",
            "complete_time": 1590662007,
            "order_status": "SUCCESS",
            "transaction_status": "SUCCESS",
            "memo": "",
            "remark": ""
        }
    }

    @apiError {Integer} err_code  错误码
    @apiError {String}  err_msg  错误信息
    @apiError {Integer} timestamp 时间戳
    @apiError {Object} data   null
    @apiErrorExample  {json} Error-Example
    HTTP 1.1/ 200
    {
        "err_code":400,
        "err_msg":"not found order data",
        "timestamp":1589800815036,
        "data":null
    }
    """



    withdraw_request_schema = {

        'serial_id' : And(str, lambda item: 21 == len(item) and str(item).isnumeric(),
                          error='`serial_id` is invalid '),# 支付网关生成的唯一流水号

        # 'order_id': And(str, lambda item: 10 < len(item) and str(item).isnumeric(),
        #                 error='`order_id` is invalid '),# 判断  order_id  必须是 str, 并且是有效字符串

        'pro_id': And(int, lambda item: 0 < item < 100, error='`pro_id` is invalid'),
    }

    def query_withdraw_order(self,serial_id : str,  pro_id : int) -> Union[dict, None]:
        """
        通过 serial_id 查询提币订单号
        :param serial_id:  支付网关系统生成的唯一的id
        :return: 如果订单存在返回dict,  如果订单不存在则返回 None
        """
        engine = create_engine(MYSQL_CONNECT_INFO,
                               max_overflow=0,
                               pool_size=5)
        Session = sessionmaker(bind=engine, autocommit=True, autoflush=False)
        session = Session()

        #查询操作不需要 flush
        orderdata = session.query(WithdrawOrder).filter_by(serial_id=serial_id, pro_id=pro_id).first()

        if orderdata is None:
            raise Exception('not found order data')

        assert isinstance(orderdata, WithdrawOrder)

        ret_info = {
            'pro_id' : orderdata.pro_id,
            'serial_id' : orderdata.serial_id,
            'order_id' :orderdata.order_id,
            'from_addr' : orderdata.from_addr,
            'to_addr' : orderdata.to_addr,
            'amount' :  decimal_to_str(  orderdata.amount ),
            'tx_confirmations' : orderdata.tx_confirmations,
            'block_height': orderdata.block_height,
            'block_time':  datetime_to_timestamp(orderdata.block_time) \
                            if orderdata.block_time is not None else None ,
            'tx_hash':orderdata.tx_hash,
            'callback_url':orderdata.callback_url,
            'complete_time': datetime_to_timestamp( orderdata.complete_time ) \
                                if orderdata.complete_time is not None else None,
            'order_status':orderdata.order_status,
            # 'notify_status':orderdata.notify_status,
            'transaction_status':orderdata.transaction_status,
            # 'notify_times' : orderdata.notify_times,
            'memo' : orderdata.memo,
            'remark' : orderdata.remark,
        }

        return  ret_info


    @apiauth
    def post(self):
        try:
            logger.info(f'request.body : { self.request.body }')

            raw_req_params = json.loads(self.request.body)

            # 检验参数的合法性
            req_params = Schema(schema=self.withdraw_request_schema).validate(data=raw_req_params)

            # 验证pro_id 和请求的合法性

            serial_id = req_params['serial_id']
            pro_id = req_params['pro_id']

            ret_info = self.query_withdraw_order(serial_id=serial_id, pro_id=pro_id)
            logger.info('process_withdraw_order success returned ')

            rsp_data = ret_info
            logger.info(rsp_data)

            # 返回, 订单接收成功
            self.write(self.success_ret_with_data(data=rsp_data))
            pass
            pass
        except Exception as e:
            logger.error(f'QueryWithdrawOrder error occured: {e}')
            self.write(self.error_ret_with_data(err_code=400, err_msg=str(e), data=None))

        pass

    def write_error(self, status_code, **kwargs):
        self.write("Gosh darnit, user! You caused a %d error." % status_code)






class QueryAllWithdrawData(BaseHandler):
    """
    @api {POST} http://192.168.10.174/api/withdraw/queryallwithdrawdata  3.4.查询提币记录
    @apiVersion 0.0.1
    @apiName  queryallwithdrawdata
    @apiGroup 3.PG_Withdraw
    @apiDescription 查询已完提币记录, 即订单状态为已完成(成功或失败)的提币订单 , 不包括未完成的(即正在处理中)的订单。

    @apiParam {Integer} pro_id  项目方ID
    @apiParam {String} token_name 币种名(BTC, HTDF, ETH, USDT, BTU)
    @apiParam {Integer} start_time  起始时间戳(订单完成时间)
    @apiParam {Integer} end_time  结束时间戳(订单完成时间)
    @apiParam {Integer} page_index 当前页
    @apiParam {Integer} page_size 页大小(最大100)

    @apiParamExample {json} 请求参数示例:
    {
        "pro_id":1,
        "token_name":"HTDF"
        "start_time":0,
        "end_time":9999999999,
        "page_index":1,
        "page_size":2
    }

    @apiSuccess {Integer} err_code  错误码
    @apiSuccess {String} err_msg 错误信息
    @apiSuccess {Integer} timestamp  时间戳
    @apiSuccess {[Object]} data 提币记录列表
    @apiSuccess {Integer} data.pro_id  项目方id
    @apiSuccess {String}  data.token_name 币种名
    @apiSuccess {String}  data.from_addr 源地址
    @apiSuccess {String}  data.to_addr  目的地址
    @apiSuccess {String}  data.tx_hash 交易哈希(或称交易ID)
    @apiSuccess {Integer} data.block_time   区块时间(如果没有区块时间则为 null )
    @apiSuccess {Integer} data.block_height   区块高度
    @apiSuccess {Integer} data.tx_confirmations   区块确认数
    @apiSuccess {Integer} data.complete_time   完成时间
    @apiSuccess {String}  data.order_status   提币订单状态 (SUCCESS:订单已成功, FAIL:订单已失败, PROCESSING:订单处理中(此接口不返回此状态的订单数据) )
    @apiSuccess {String}  data.transaction_status   转账交易状态(NOTYET:尚未转账, PENDING:已汇出, FAIL:交易失败 SUCCESS:交易成功 )
    @apiSuccess {String}  data.callback_url 回调通知地址, 当订单状态改变时主动通知项目方,项目方必须提供通知接口的url, 详细说明请看"公共参数说明"
    @apiSuccess {String}  data.memo     交易备注(区块链上交易中的memo)
    @apiSuccess {String}  data.remark  备注

    @apiSuccessExample {json} Success-Example:
    HTTP/1.1 200 OK
    {
        "err_code": 0,
        "err_msg": null,
        "timestamp": 1591340671717,
        "data": {
            "pro_id": 1,
            "token_name": "HTDF",
            "start_time": 0,
            "end_time": 9999999999,
            "page_index": 1,
            "page_size": 2,
            "total_count": 747,
            "total_pages": 374,
            "withdraw_data": [{
                "pro_id": 1,
                "serial_id": "202005281833079967716",
                "order_id": "21488153467324656239",
                "from_addr": "htdf1vhq6c38demm58cnevc4sntc77z8ppvl85mj0a6",
                "to_addr": "htdf1ewfage0jv8m4wsv7w3nhg9xar2d9qj9mh4c8m8",
                "amount": "0.10031000",
                "tx_confirmations": 1,
                "block_height": 859422,
                "block_time": 1590662008,
                "tx_hash": "86B084D97617C288AEEE22E2234F0572EFB96011CEF2A8E3348319ED83CAE4BE",
                "callback_url": "http://192.168.10.29:8001/notifywithdraw",
                "complete_time": 1590662007,
                "order_status": "SUCCESS",
                "transaction_status": "SUCCESS",
                "memo": "",
                "remark": ""
            }, {
                "pro_id": 1,
                "serial_id": "202005281840022221101",
                "order_id": "01065339098581975260",
                "from_addr": "htdf1vhq6c38demm58cnevc4sntc77z8ppvl85mj0a6",
                "to_addr": "htdf1kz2qj8yq0kufqvc923zkjl62pxcaf3gkrdyc4r",
                "amount": "0.10033500",
                "tx_confirmations": 1,
                "block_height": 859504,
                "block_time": 1590662420,
                "tx_hash": "8BE51DB4C9441E406D636D93C04C5DC4F0FB0FBE5019B1F4513BEB459A54BD3A",
                "callback_url": "http://192.168.10.29:8001/notifywithdraw",
                "complete_time": 1590662419,
                "order_status": "SUCCESS",
                "transaction_status": "SUCCESS",
                "memo": "",
                "remark": ""
            }]
        }
    }

    @apiError {Integer} err_code  错误码
    @apiError {String}  err_msg  错误信息
    @apiError {Integer} timestamp 时间戳
    @apiError {Object} data   null
    @apiErrorExample  {json} Error-Example
    HTTP 1.1/ 200
    {
        "err_code":400,
        "err_msg":"page_index is too large"",
        "timestamp":1589800815036,
        "data":null
    }
    """



    query_all_withdaw_data_request_schema = {
        'pro_id': And(int, lambda item: item < 100000000, error='`pro_id` is invalid'),
        'token_name': And(str, lambda item: item in g_TOKEN_NAME_LIST, error='`token_name` is invalid'),
        'page_size': And(int, lambda item: 0 < item <= 100, error='`page_size` must 0 < page_size <=100'),
        'page_index': And(int, lambda item: 0 < item <= 1000000, error='`page_index` is invalid, must greater than 0'),

        "start_time": And(int, lambda item: 0 <= item < 1000000000000,
                          error='`start_time` is invalid '),

        'end_time': And(int, lambda item: 0 <= item < 1000000000000,
                        error='`end_time` is invalid'),
    }



    def query_withdraw_order(self, **kwargs) -> tuple:
        """
        通过 serial_id 查询提币订单号
        :param serial_id:  支付网关系统生成的唯一的id
        :return: 如果订单存在返回dict,  如果订单不存在则返回 None
        """
        pro_id = kwargs['pro_id']
        token_name = kwargs['token_name']
        start_time = kwargs['start_time']
        end_time = kwargs['end_time']

        page_size = kwargs['page_size']
        page_index = kwargs['page_index']

        limit_num = page_size
        offset_num = int((page_index - 1) * page_size)

        start_time = datetime.fromtimestamp(int(start_time))
        end_time = datetime.fromtimestamp(int(end_time))


        engine = create_engine(MYSQL_CONNECT_INFO,
                               max_overflow=0,
                               pool_size=5)
        Session = sessionmaker(bind=engine, autocommit=True, autoflush=False)
        session = Session()

        total_count =  session.query(func.count(WithdrawOrder.serial_id) )\
                        .filter(WithdrawOrder.pro_id == pro_id,
                                WithdrawOrder.token_name==token_name,
                                WithdrawOrder.order_status != WithdrawStatus.order_status.PROCESSING,
                                and_(WithdrawOrder.complete_time >= start_time, WithdrawOrder.complete_time <= end_time)
                                ).scalar()

        total_pages = math.ceil(total_count / page_size)
        if page_index > total_pages:
            err_msg = "page_index is too large"
            logger.error(msg=err_msg)
            raise RuntimeError(err_msg)

        #查询操作不需要 flush
        orders = session.query( WithdrawOrder )\
                        .filter(WithdrawOrder.pro_id == pro_id,
                                WithdrawOrder.token_name==token_name,
                                WithdrawOrder.order_status != WithdrawStatus.order_status.PROCESSING,
                                and_(WithdrawOrder.complete_time >= start_time, WithdrawOrder.complete_time <= end_time)
                                )\
                        .order_by(WithdrawOrder.complete_time)\
                        .limit(limit_num)\
                        .offset(offset_num)\
                        .all()

        if orders is None:
            raise Exception('not found order data')

        # assert isinstance(orders, list)

        ret_data = []
        for orderdata in orders:
            ret_data.append({
                'pro_id': orderdata.pro_id,
                'serial_id': orderdata.serial_id,
                'order_id': orderdata.order_id,
                'from_addr': orderdata.from_addr,
                'to_addr': orderdata.to_addr,
                'amount': decimal_to_str(orderdata.amount),
                'tx_confirmations': orderdata.tx_confirmations,
                'block_height': orderdata.block_height,
                'block_time': datetime_to_timestamp(orderdata.block_time) \
                                if orderdata.block_time is not None else None ,
                'tx_hash': orderdata.tx_hash,
                'callback_url': orderdata.callback_url,
                'complete_time': datetime_to_timestamp(orderdata.complete_time)\
                                if orderdata.complete_time is not None else None  ,
                'order_status': orderdata.order_status,
                # 'notify_status': orderdata.notify_status,
                'transaction_status': orderdata.transaction_status,
                # 'notify_times': orderdata.notify_times,
                'memo': orderdata.memo,
                'remark': orderdata.remark,
            })
            pass

        return  ret_data, total_count, total_pages


    @apiauth
    def post(self):
        try:
            logger.info(f'request.body : { self.request.body }')

            raw_req_params = json.loads(self.request.body)

            # 检验参数的合法性
            req_params = Schema(schema=self.query_all_withdaw_data_request_schema).validate(data=raw_req_params)


            data, total_count, total_pages = self.query_withdraw_order(**req_params)
            logger.info('process_withdraw_order success returned ')

            rsp_data = req_params
            rsp_data['total_count'] = total_count
            rsp_data['total_pages'] = total_pages
            rsp_data['withdraw_data'] = data

            logger.info(rsp_data)

            # 返回
            self.write(self.success_ret_with_data(data=rsp_data))
            pass
        except Exception as e:
            logger.error(f'QueryWithdrawOrder error occured: {e}')
            self.write(self.error_ret_with_data(err_code=400, err_msg=str(e), data=None))

        pass

    def write_error(self, status_code, **kwargs):
        self.write("You caused a %d error." % status_code)