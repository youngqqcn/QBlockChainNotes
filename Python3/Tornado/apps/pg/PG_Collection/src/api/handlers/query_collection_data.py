#!coding:utf8

#author:yqq
#date:2020/5/22 0022 18:59
#description: 查询归集的数据



import math
from typing import Union

# from src.lib.base_handler import BaseHandler
import logging

#使用 sqlalchemy 进行 ORM
from sqlalchemy import create_engine, and_, func
from sqlalchemy.orm import sessionmaker

from src.api.handlers.handler_base import apiauth, BaseHandler
from src.config.constant import MYSQL_CONNECT_INFO, WithdrawStatus, g_TOKEN_NAME_LIST

logger = logging.getLogger(__name__)


#从model导入
from src.model.model import CollectionRecords
import json
from schema import And, Schema, Or



from decimal import Decimal
def decimal_to_str(decim : Union[Decimal, float],  precesion : int = 8 ) -> str:
    return str(Decimal(decim).quantize(Decimal('0.' + '0' * precesion)))

from datetime import datetime
import time
def datetime_to_timestamp( dt : datetime  ) -> int:
    return int(time.mktime(dt.timetuple()))



class QueryCollectionData(BaseHandler):
    """
    @api {POST} http://192.168.10.174/api/collection/getcollectiondata  4.2.查询归集数据
    @apiVersion 0.0.1
    @apiName  getcollectiondata
    @apiGroup 4.PG_Collection
    @apiDescription 查询归集数据,

    @apiParam {Integer} pro_id  项目方ID
    @apiParam {String} token_name 币种名(BTC, ETH, HTDF, USDT, BTU)
    @apiParam {Integer} start_time  起始时间戳
    @apiParam {Integer} end_time  结束时间戳
    @apiParam {Integer} page_index 当前页
    @apiParam {Integer} page_size 页大小(最大100)

    @apiParamExample {json} 请求参数示例:
    {
        "pro_id":1,
        "token_name":"HTDF"
        "start_time":0,
        "end_time":9999999999,
        "page_index":1,
        "page_size":20
    }


    @apiSuccess {Object} status 状态码
    @apiSuccess {Integer} pro_id  项目方ID
    @apiSuccess {String} token_name 币种名
    @apiSuccess {Integer} start_time  起始时间戳
    @apiSuccess {Integer} end_time  结束时间戳
    @apiSuccess {Integer} page_index 当前页
    @apiSuccess {Integer} page_size 页大小
    @apiSuccess {Integer} total_count 归集记录总数
    @apiSuccess {Integer} total_pages 总页数
    @apiSuccess {[Object]} collection_data 归集数据
    @apiSuccess {String} collection_data.token_name  币种名
    @apiSuccess {String} collection_data.from_addr  源地址
    @apiSuccess {String}  collection_data.to_addr   目的地址
    @apiSuccess {String}  collection_data.amount    归集金额
    @apiSuccess {String}  collection_data.tx_hash  交易哈希(或称交易ID) , v2.0版本注意: 项目方不能用此字段作为唯一性判断, 因BTC是批量归集, 同一批次(可能包含多个源地址)归集记录的交易哈希是相同的
    @apiSuccess {Integer} collection_data.block_time   区块时间
    @apiSuccess {Integer} collection_data.complete_time   归集完成时间
    @apiSuccess {Integer} collection_data.block_height   区块高度
    @apiSuccess {Integer} collection_data.tx_confirmations  区块确认数
    @apiSuccess {Integer} deposit_data.pro_id pro_id 项目方id



    @apiSuccessExample {json}  Success-Example:
    HTTP/1.1 200 OK
    {
        "err_code": 0,
        "err_msg": null,
        "timestamp": 1590148388415,
        "data": {
            "pro_id": 1,
            "token_name": "HTDF",
            "start_time": 0,
            "end_time": 9999999999,
            "page_index": 1,
            "page_size": 20,
            "total_count": 454,
            "total_pages": 23,
            "collection_data": [{
                "token_name": "HTDF",
                "from_addr": "htdf1z4gl0ey8s0fptj5tttnls07sjns27mlzl32afz",
                "to_addr": "htdf1jrh6kxrcr0fd8gfgdwna8yyr9tkt99ggmz9ja2",
                "amount": "0.09226700",
                "tx_hash": "5567A47FD74CCA008881F0525760654C0CA32C1DE320A66D020439276BFC4C13",
                "block_time": 1590066261,
                "block_height": 741935,
                "tx_confirmations": 1,
                "pro_id": 1,
                "complete_time": 1590066275
            }, {
                "token_name": "HTDF",
                "from_addr": "htdf1yrx9vjg4dugk2mggl7xj3v8jnec63jlz6jq8cq",
                "to_addr": "htdf1jrh6kxrcr0fd8gfgdwna8yyr9tkt99ggmz9ja2",
                "amount": "0.21999799",
                "tx_hash": "30E8B3AAD8834D80DA08F11AC032A9647E262BE6F05A9165BDF53A8357FF1156",
                "block_time": 1590067490,
                "block_height": 742180,
                "tx_confirmations": 1,
                "pro_id": 1,
                "complete_time": 1590067503
            },
            ......
            ]
        }
    }



    @apiErrorExample Error-Example:
    HTTP 1.1/ 200
    {
        "err_code": 400,
        "err_msg": "`token_name` is invalid",
        "timestamp": 1589784667060,
        "data": null
    }

    """


    collection_query_request_schema = {
        'pro_id': And(int, lambda item: item < 100000000, error='`pro_id` is invalid'),
        'token_name': And(str, lambda item: item in g_TOKEN_NAME_LIST, error='`token_name` is invalid'),
        'page_size': And(int, lambda item: 0 < item <= 100, error='`page_size` must 0 < page_size <=100'),
        'page_index': And(int, lambda item: 0 < item <= 1000000, error='`page_index` is invalid, must greater than 0'),

        "start_time" : And(int, lambda item: 0 <= item < 1000000000000,
                                                                  error='`start_time` is invalid '),

        'end_time': And(int, lambda item: 0 <= item < 1000000000000,
                                                              error='`end_time` is invalid'),
    }

    def query_collection_data(self, **kwargs):

        engine = create_engine(MYSQL_CONNECT_INFO, max_overflow=0, pool_size=5)
        Session = sessionmaker(bind=engine)
        session = Session()
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

        total_count = session.query( func.count( CollectionRecords.id )).filter_by(pro_id=pro_id, token_name=token_name) \
                            .filter(and_(CollectionRecords.complete_time >= start_time, CollectionRecords.complete_time <= end_time,
                                CollectionRecords.transaction_status == WithdrawStatus.transaction_status.SUCCESS
                            )).scalar()

        total_pages = math.ceil(total_count / page_size)

        if page_index > total_pages:
            err_msg = "page_index is too large"
            logger.error(msg=err_msg)
            raise RuntimeError(err_msg)

        collections_txs = session.query(CollectionRecords).filter_by(pro_id=pro_id, token_name=token_name) \
            .filter(and_(CollectionRecords.complete_time >= start_time, CollectionRecords.complete_time <= end_time,
                         CollectionRecords.transaction_status == WithdrawStatus.transaction_status.SUCCESS
                         )) \
            .order_by(CollectionRecords.complete_time)\
            .limit(limit_num).offset(offset_num)\
            .all()

        ret_data = []
        for tx in collections_txs:
            assert isinstance(tx, CollectionRecords)
            ret_data.append(
                {
                    'token_name': tx.token_name,
                    'from_addr': tx.from_address,
                    'to_addr': tx.to_address,
                    'amount': decimal_to_str(tx.amount),
                    'tx_hash': tx.tx_hash,
                    'block_time': datetime_to_timestamp(tx.block_time) ,
                    'block_height': tx.block_height,
                    'tx_confirmations': tx.tx_confirmations,
                    'pro_id': tx.pro_id,
                    'complete_time' : datetime_to_timestamp(tx.complete_time),
                }
            )

        return ret_data, total_count, total_pages


    @apiauth
    def post(self):

        try:
            logger.info(f'request.body : { self.request.body }')

            raw_req_params = json.loads(self.request.body)

            # 检验参数的合法性
            req_params = Schema(schema=self.collection_query_request_schema).validate(data=raw_req_params)

            ret_datas , total_count, total_pages = self.query_collection_data(**req_params)

            rsp_data = req_params
            rsp_data['total_count'] = total_count
            rsp_data['total_pages'] = total_pages
            rsp_data['collection_data'] = ret_datas
            logger.info(rsp_data)

            self.write(self.success_ret_with_data(data=rsp_data))
            pass
        except Exception as e:
            logger.error(f'QueryDepositData error occured: {e}')
            self.write(self.error_ret_with_data(err_code=400, err_msg=str(e), data=None))

        pass



    pass




