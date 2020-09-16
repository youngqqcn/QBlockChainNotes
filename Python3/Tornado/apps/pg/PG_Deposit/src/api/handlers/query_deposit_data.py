import math
from typing import Union

# from src.lib.base_handler import BaseHandler
import logging

#使用 sqlalchemy 进行 ORM
from sqlalchemy import create_engine, and_, func
from sqlalchemy.orm import sessionmaker

from src.api.handlers.handler_base import apiauth, BaseHandler
from src.config.constant import MYSQL_CONNECT_INFO, g_TOKEN_NAME_LIST

logger = logging.getLogger(__name__)


#从model导入
from src.model.model import Deposit
import json
from schema import And, Schema, Or



from decimal import Decimal
def decimal_to_str(decim : Union[Decimal, float],  precesion : int = 8 ) -> str:
    return str(Decimal(decim).quantize(Decimal('0.' + '0' * precesion)))

from datetime import datetime
import time
def datetime_to_timestamp( dt : datetime  ) -> int:
    return int(time.mktime(dt.timetuple()))



class QueryDepositData(BaseHandler):
    """
    @api {POST} http://192.168.10.174/api/deposit/getdepositdata  2.2.查询充币数据
    @apiVersion 0.0.1
    @apiName  getdepositdata
    @apiGroup 2.PG_Deposit
    @apiDescription 查询充币数据,
    注意: 请求参数 start_height和end_height , start_blocktime和end_blocktime  必须二选一 。
    注意: v2.0 BTC 特别注意:因BTC交易的特殊性,BTC充币交易的from_addr固定为字符串"sourceaddressisunknown"

    @apiParam {Integer} pro_id  项目方ID
    @apiParam {String} token_name 币种名 (BTC, ETH, HTDF, USDT, BTU)
    @apiParam {Integer} start_height  起始高度
    @apiParam {Integer} end_height  结束高度
    @apiParam {Integer} page_index 当前页
    @apiParam {Integer} page_size 页大小(最大为100)

    @apiParamExample {json} 请求参数示例:
    {
        "pro_id":1,
        "token_name":"HTDF"
        "start_height":0,
        "end_height":999999999,
        "page_index":1,
        "page_size":20
    }


    @apiSuccess {Integer} pro_id  项目方ID
    @apiSuccess {String} token_name 币种名
    @apiSuccess {Integer} [start_height]  起始高度(和 end_height配合使用)
    @apiSuccess {Integer} [end_height]  结束高度(和 start_height配合使用)
    @apiSuccess {Integer} [start_blocktime]  起始区块时间 (和 end_blocktime配合使用)
    @apiSuccess {Integer} [end_blocktime]  结束区块时间 (和 start_blocktime配合使用 )
    @apiSuccess {Integer} page_index 当前页
    @apiSuccess {Integer} page_size 页大小
    @apiSuccess {Integer} total_count 总条数
    @apiSuccess {Integer} total_pages 总页数
    @apiSuccess {[Object]} deposit_data 充币数据
    @apiSuccess {String} deposit_data.token_name  币种名
    @apiSuccess {String} deposit_data.from_addr  源地址 (v2.0特别注意:因BTC交易的特殊性,BTC充币交易的from_addr固定为字符串"sourceaddressisunknown")
    @apiSuccess {String}  deposit_data.to_addr   目的地址
    @apiSuccess {String}  deposit_data.tx_hash  交易哈希(或称交易ID)
    @apiSuccess {String}  deposit_data.amount  充币金额
    @apiSuccess {Integer}  deposit_data.block_time   区块时间
    @apiSuccess {Integer} deposit_data.block_height   区块高度
    @apiSuccess {Integer}  deposit_data.tx_confirmations   区块确认数
    @apiSuccess {String}  deposit_data.memo     交易备注(区块链上交易中的memo,若无memo则为值null),注意:目前仅HTDF和HRC20代币(如:BTU)支持memo
    @apiSuccess {Integer} deposit_data.pro_id  项目方id



    @apiSuccessExample {json}  Success-Example:
    HTTP/1.1 200 OK
    {
        "err_code": 0,
        "err_msg": null,
        "timestamp": 1590148388415,
        "data": {
            "pro_id": 1,
            "token_name": "HTDF",
            "start_height": 0,
            "end_height": 999999999,
            "page_index": 1,
            "page_size": 20,
            "total_count": 79,
            "total_pages": 4,
            "deposit_data": [{
                    "token_name": "HTDF",
                    "from_addr": "htdf1jrh6kxrcr0fd8gfgdwna8yyr9tkt99ggmz9ja2",
                    "to_addr": "htdf1x8fe2pqwx9fd9n4xqg4k4xqz4lxr7dsl96dscm",
                    "amount": "0.00192608",
                    "tx_hash": "03f5707f943973c7304986153e9150b8eace98ee2dea8bb35700e73e49e08a11",
                    "block_time": 1589534869,
                    "block_height": 643160,
                    "tx_confirmations": 3,
                    "memo": "yqq",
                    "pro_id": 1
                }, {
                    "token_name": "HTDF",
                    "from_addr": "htdf1jrh6kxrcr0fd8gfgdwna8yyr9tkt99ggmz9ja2",
                    "to_addr": "htdf16y33nhgfft3spz5fee4z0yqn87ezn6smyqlsq3",
                    "amount": "0.00362508",
                    "tx_hash": "0b0cd8402247f46c1e3264f26fef0d2831d8250d296a6f1e105141cd1bff36fe",
                    "block_time": 1589534799,
                    "block_height": 643146,
                    "tx_confirmations": 3,
                    "memo": "yqq",
                    "pro_id": 1
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


    #充币查询接口,参数校验器
    deposit_query_request_schema = {
        'pro_id': And(int, lambda item: item < 100000000, error='`pro_id` is invalid'),
        'token_name' : And(str, lambda item : item in g_TOKEN_NAME_LIST, error='`token_name` is invalid' ),
        'page_size' : And(int, lambda item : 0 < item <= 100, error='`page_size` must 0 < page_size <=100'),
        'page_index' : And(int, lambda item : 0 < item <= 1000000, error='`page_index` is invalid, must greater than 0'),

        Or('start_height', "start_blocktime", only_one=True ) : And(int, lambda item : 0 <= item < 1000000000000,
                                                error='`start_height` or `start_blocktime` must be only one  ' ),

        Or('end_height', 'end_blocktime', only_one=True) : And(int, lambda item : 0 <= item < 1000000000000,
                                                error='`end_height` or `end_blocktime` must only one' ),

    }



    def query_deposit_data(self, **kwargs  ):
        """
        获取充币数据
        :param kwargs:
        :return:  ([], int, int)
        """
        engine = create_engine(MYSQL_CONNECT_INFO, max_overflow=0, pool_size=5)
        Session = sessionmaker(bind=engine)
        session = Session()
        pro_id = kwargs['pro_id']
        token_name = kwargs['token_name']

        # 使用 limit 进行分页
        page_size = kwargs['page_size']
        page_index = kwargs['page_index']

        limit_num = page_size
        offset_num = int((page_index - 1) * page_size)


        if 'end_height' in kwargs and 'start_height' in kwargs:

            #根据区块高度查询
            start_height = kwargs['start_height']
            end_height = kwargs['end_height']

            logger.info(f'start_height:{start_height}, end_height:{end_height}')

            total_count = session.query( func.count( Deposit.id )).filter_by(pro_id=pro_id, token_name=token_name) \
                                .filter(Deposit.block_height >= start_height, Deposit.block_height < end_height)\
                                .scalar()

            total_pages = math.ceil(total_count / page_size)

            deposit_txs = session.query(Deposit).filter_by(pro_id=pro_id, token_name=token_name) \
                                .filter(Deposit.block_height >= start_height, Deposit.block_height < end_height) \
                                .limit(limit_num).offset(offset_num).all()

        elif 'start_blocktime' in kwargs and 'end_blocktime' in kwargs:

            #根据区块时间查询
            start_blocktime = kwargs['start_blocktime']
            end_blocktime =  kwargs['end_blocktime']

            start_blocktime = datetime.fromtimestamp(int(start_blocktime))
            end_blocktime = datetime.fromtimestamp(int(end_blocktime))

            logger.info(f'start_blocktime:{start_blocktime}, end_blocktime:{end_blocktime}')



            total_count = session.query( func.count(Deposit.id)).filter_by(pro_id=pro_id, token_name=token_name) \
                            .filter(and_(Deposit.block_time >= start_blocktime, Deposit.block_time <= end_blocktime)) \
                            .scalar()

            total_pages = math.ceil(total_count / page_size)

            deposit_txs = session.query(Deposit).filter_by(pro_id=pro_id, token_name=token_name) \
                            .filter(and_( Deposit.block_time >= start_blocktime, Deposit.block_time <= end_blocktime))\
                            .all()

        else:
            logger.error('invalid request parameter')
            raise  RuntimeError("invalid request parameters")

        logger.info(f'found  {len(deposit_txs)} deposit txs ')


        ret_data = []
        for tx in deposit_txs:
            assert isinstance(tx, Deposit)
            ret_data.append(
                    {
                        'token_name'        : tx.token_name,
                        'from_addr'         : tx.from_addr,
                        'to_addr'           : tx.to_addr,
                        'amount'            : decimal_to_str( tx.amount ),
                        'tx_hash'           : tx.tx_hash,
                        'block_time'        : datetime_to_timestamp( tx.block_time ),
                        'block_height'      : tx.block_height,
                        'tx_confirmations'  : tx.tx_confirmations,
                        'memo'              : tx.memo,
                        'pro_id'            : tx.pro_id
                    }
                )

        return ret_data, total_count, total_pages



    @apiauth
    def post(self):

        try:
            logger.info(f'request.body : { self.request.body }')

            raw_req_params = json.loads(self.request.body)

            # 检验参数的合法性
            req_params = Schema(schema=self.deposit_query_request_schema).validate(data=raw_req_params)

            ret_datas, total_count, total_pages = self.query_deposit_data( **req_params)

            rsp_data = req_params
            rsp_data['total_count'] = total_count
            rsp_data['total_pages'] = total_pages
            rsp_data['deposit_data'] = ret_datas
            logger.info(rsp_data)

            self.write( self.success_ret_with_data(data=rsp_data) )
            pass
        except Exception as e:
            logger.error(f'QueryDepositData error occured: {e}')
            self.write(self.error_ret_with_data(err_code=400, err_msg=str(e), data=None))

        pass