#!coding:utf8

#author:yqq
#date:2020/5/7 0007 16:02
#description:
import json
import math
from datetime import datetime
from typing import Union

import redis
from sqlalchemy import create_engine, and_, func
from sqlalchemy.orm import sessionmaker

from src.api.handlers.handler_base import BaseHandler, apiauth
from src.lib.pg_utils import datetime_to_timestamp
from src.model.model import Address, AddAddressOrder, WithdrawConfig
from src.config.constant import AddAddressOrderStatus, AddrAddressOrderAuditStatus, AddrAddressOrderGenerateStatus, \
    AddrAddressOrderActiveStatus, REDIS_HOST, REDIS_PORT, REDIS_ADDRESS_POOL_DB_NAME, REDIS_DEPOSIT_ADDRESS_POOL_NAME, MYSQL_DB_NAME, \
    MYSQL_CONNECT_INFO, g_TOKEN_NAME_LIST
import logging

#使用 sqlalchemy 进行 ORM

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

from schema import And, Schema, Optional


class  GenerateAddress(BaseHandler):
    """
    @api {POST} http://192.168.10.174/api/wallet/addaddresses  1.2.申请充币地址
    @apiVersion 0.0.1
    @apiName  addaddresses
    @apiGroup 1.PG_Wallet
    @apiDescription  申请增加充币地址, 需管理员审核,审核通过才生效.
    注意: 如项目方需新增对接币种(如:v2.0新增的BTC), 则需要沙暴管理员为项目方生成币种配置(项目方需提供币种的配置信息)之后,项目方才能进行地址申请

    @apiParam {Integer} pro_id  项目方ID
    @apiParam {String} token_name 币种名(BTC, HTDF, ETH) , 注意:USDT与ETH共用充币地址,不需单独申请;如只想对接USDT,直接申请ETH地址即可. 另外, HRC20代币(如: BTU)与HTDF共用充币地址,不需要单独申请,只需申请HTDF地址即可
    @apiParam {Integer} address_count 申请增加数量(单次单币种申请最大数量为2000,如某个币种有未完成的申请订单,则不可再次申请. 注意:申请订单需人工审核,生产环境下请提前申请!)

    @apiParamExample {json} 请求参数示例:
    {
        "address_count": 100,
        "pro_id":1,
        "token_name":"HTDF"
    }

    @apiSuccess {Integer} err_code 错误码
    @apiSuccess {String} err_msg 错误信息
    @apiSuccess {Integer} timestamp  时间戳
    @apiSuccess {Object} data  数据
    @apiSuccess {Integer} data.pro_id  项目方id
    @apiSuccess {String} data.token_name  币种名
    @apiSuccess {Integer} data.address_count 本次申请数量
    @apiSuccess {String} data.order_id 申请订单号

    @apiSuccessExample {json}  Success-Example:
    HTTP/1.1 200 OK
    {
        "err_code": 0,
        "err_msg": "null",
        "timestamp": 1589784667060,
        "data":{
            "pro_id" : 1,
            "token_name" : "HTDF",
            "address_count": 200,
            "order_id" : "202202055161651810313"
        }
    }

    @apiErrorExample Response-Fail:
    HTTP 1.1/ 200
    {
        "err_code": 400,
        "err_msg": "this is error messages",
        "timestamp": 1589784667060,
        "data": null
    }
    """

    gen_addr_req_params_schema = {
        'address_count' : And(int, lambda item : 1 <= item <= 2000, error='`address_count` must between 1 and 2000'),
        # 'account_index' : And(int, lambda item : 0 <= item <= 100, error='`account_index` must between 0 and 100'),
        'pro_id' : And(int, lambda item : 1 <= item <= 100, error='`pro_id` must between 1 and 100'),
        'token_name': And(str, lambda item: item in g_TOKEN_NAME_LIST, error='`token_name` is invalid, it must be one of BTC or HTDF or ETH'),
    }

    def __init__(self, application , request, **kwargs):

        engine = create_engine(MYSQL_CONNECT_INFO, max_overflow=0, pool_size=5)
        MySqlSessionClass = sessionmaker(bind=engine, autocommit=True, autoflush=False)
        self.session = MySqlSessionClass()
        super().__init__(application=application, request=request, **kwargs)


    def get_address_start_index(self, pro_id : int, token_name : str) -> int:
        """
        获取某个项目方  某个币种的起始索引
        :param pro_id:
        :param token_name:
        :return:
        """

        # session = MySqlSessionClass()

        ret = self.session.query(func.max(Address.address_index))\
                    .filter(and_(Address.pro_id == pro_id, Address.token_name == token_name))\
                    .first()

        if ret is not None:
            return ret[0] + 1 if ret[0] is not None else 0
        return 0

    def check_token_for_pro_is_created(self, pro_id: int, token_name: str) -> bool:
        """
        检查某个项目方的某个币种, 是否已经创建了出币地址? 是否填写了归集地址? 等等...
        如果某个项目方没有这些信息, 则不可申请充币地址
        :param pro_id:
        :param token_name:
        :return:
        """
        ret = self.session.query(WithdrawConfig.address)\
                    .filter(and_(WithdrawConfig.pro_id == pro_id, WithdrawConfig.token_name == token_name))\
                    .first()
        if ret is None:
            return False
        return True



    def generate_serial_id(self) -> str:
        """
        生成流水号
        :return: 流水号
        """
        import time
        serial_id = str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))) + \
                            str(int(time.perf_counter_ns()))[-7:]
        return serial_id

    def generate_address_order(self, **kwargs) -> AddAddressOrder :



        #如果该项目方  某个币种 已有申请, 并且还未完成,  不可再次申请
        pro_id = kwargs['pro_id']
        token_name = kwargs['token_name']

        #检查沙暴内部管理台是否已经为项目方创建了某个币种的配置(如: 出币地址, 归集地址, 等等...)
        #如果尚未配置, 则项目方不可进行此币种充币地址的申请
        if not self.check_token_for_pro_is_created(pro_id=pro_id, token_name=token_name):
            msg = f'Sorry, Some configurations of {token_name} has not been created for you, Please contact with shbao administrator.'
            logger.info(f'pro_id:{pro_id},  {msg}')
            raise Exception(msg)



        pending_order = self.session.query(AddAddressOrder) \
                    .filter_by(pro_id= pro_id, token_name=token_name, order_status=AddAddressOrderStatus.PROCESSING )\
                     .first()

        if isinstance( pending_order, AddAddressOrder):
            raise Exception(f'a pending order {pending_order.order_id} exist! you could not apply new order until pending order finished!')

        new_order = AddAddressOrder()
        new_order.order_id = self.generate_serial_id()
        new_order.order_create_time = datetime.now()
        new_order.generate_status = AddrAddressOrderGenerateStatus.NOTYET
        new_order.active_status = AddrAddressOrderActiveStatus.YES
        new_order.count = kwargs['address_count']


        sqlret = self.session.query(func.max(Address.address_index))\
                    .filter_by(pro_id=pro_id, token_name=token_name)\
                    .first()

        if sqlret[0] is None:
            start_addr_index = 1    #所有充币地址 从  1 开始   ,
            end_addr_index =  new_order.count
        else:
            start_addr_index = sqlret[0] + 1
            end_addr_index = start_addr_index + new_order.count - 1


        # session.query(AddAddressOrder).filter_by(pro_id=pro_id, token_name=token_name,  )


        all_apply_orders_count = self.session.query( func.count(AddAddressOrder.order_id))\
                                        .filter_by(pro_id=pro_id, token_name=token_name)\
                                        .first()

        new_order.end_addr_index = end_addr_index
        new_order.start_addr_index = start_addr_index
        new_order.pro_id = pro_id
        new_order.token_name = token_name
        new_order.apply_times = all_apply_orders_count[0] if all_apply_orders_count[0] is not None else 1
        new_order.audit_status = AddrAddressOrderAuditStatus.PENDING
        new_order.remark = ''
        new_order.order_status = AddAddressOrderStatus.PROCESSING
        new_order.active_status = AddrAddressOrderActiveStatus.NO


        #保存订单
        self.session.add(instance=new_order)
        self.session.flush()

        return new_order



    @apiauth
    def post(self):
        try:

            raw_req_params = json.loads(self.request.body)
            logger.info( f'request.body : {self.request.body}' )

            # 检验参数的合法性
            req_params = Schema(schema=self.gen_addr_req_params_schema).validate(data=raw_req_params)


            order = self.generate_address_order(**req_params)

            assert isinstance(req_params, dict)
            # assert isinstance(addresses, list)

            rsp_data = req_params
            rsp_data['order_id'] = order.order_id

            self.write(self.success_ret_with_data(data=rsp_data))
        except Exception as e:
            logger.error(f'GenerateAddress error occured: {e}')
            self.write(self.error_ret_with_data(err_code=400, err_msg=str(e), data=None))



class  QueryAddress(BaseHandler):
    """
    @api {POST} http://192.168.10.174/api/wallet/queryaddresses  1.3.查询充币地址
    @apiVersion 0.0.1
    @apiName  queryaddresses
    @apiGroup 1.PG_Wallet
    @apiDescription  查询所有充币地址

    @apiParam {Integer} pro_id  项目方ID
    @apiParam {String} token_name 币种名(三者之一: BTC, HTDF, ETH, 因USDT共用ETH,查询USDT地址时填ETH即可, HRC20代币(例如:BTU)共用HTDF地址,查询HRC20代币地址时填HTDF即可)
    @apiParam {String} [order_id]  申请订单号, (如果指定了order_id, 则返回指定申请订单的生成的地址)
    @apiParam {Integer} page_size 页大小(最大100)
    @apiParam {Integer} page_index 当前页

    @apiParamExample {json} 请求参数示例:
    {
        "pro_id":1,
        "token_name":"HTDF"
        "order_id":"202005251048312179718",
        "page_size": 50,
        "page_index":1
    }


    @apiSuccess {Integer} err_code 错误码
    @apiSuccess {String} err_msg 错误信息
    @apiSuccess {Integer} timestamp  时间戳
    @apiSuccess {Object} data  数据
    @apiSuccess {Integer} data.pro_id  项目方id
    @apiSuccess {String} [data.order_id]  申请订单号,(如果指定了order_id, 则返回指定订单申请的所有地址(即同一批次))
    @apiSuccess {Integer} data.page_size 页大小
    @apiSuccess {Integer} data.page_index 当前页
    @apiSuccess {Integer} data.total_count  总条数
    @apiSuccess {Integer} data.total_pages  总页数
    @apiSuccess {[Object]} data.addresses 地址列表
    @apiSuccess {String} data.address.address 地址
    @apiSuccess {Integer} data.address.index 地址索引

    @apiSuccessExample {json}  Success-Example:
    HTTP/1.1 200 OK
    {
        "err_code": 0,
        "err_msg": null,
        "timestamp": 1590465671648,
        "data": {
            "pro_id": 1,
            "token_name": "HTDF",
            "order_id": "202005251048312179718",
            "page_size": 50,
            "page_index": 1,
            "total_count": 10,
            "total_pages": 1,
            "addresses": [{
                    "address": "htdf13q9jkku3wwmawk7wnd0j4zvg279hl8aw5402mp",
                    "index": 12321
                }, {
                    "address": "htdf17yn887sgl08nutvn3qxg5sh697h22yqcnhxpel",
                    "index": 12322
                }, {
                    "address": "htdf1dszt4fez9va27xg3elz79taxeh5zzkfr7xp4wc",
                    "index": 12323
                }, {
                    "address": "htdf1hukhed7yzaa49n9as9z4m99y2xky7xwpyfp62u",
                    "index": 12324
                }, {
                    "address": "htdf1lqwt57c7jlds70ry266swxx6cvcdshuxa8ms30",
                    "index": 12325
                }, {
                    "address": "htdf1g2ex0jwmk6elaz7cgk0tq6qgf2m702drdnfz7t",
                    "index": 12326
                }, {
                    "address": "htdf12gdha4xfxfg3gyedq5qxzddvatmhumy7ecpptr",
                    "index": 12327
                }, {
                    "address": "htdf1k3cgmudczk4k08dzwu6nf6mf3u7rg67qracp6j",
                    "index": 12328
                }, {
                    "address": "htdf1vzkhtsa3nu5jj90zfkhw7s2gdwdhd38vy0nd3p",
                    "index": 12329
                }, {
                    "address": "htdf1mqcspg3mw29au0mdr44ch2frcd4ce77hhpklpc",
                    "index": 12330
                }
            ]
        }
    }

    @apiErrorExample Error-Example:
    HTTP 1.1/ 200
    {
        "err_code": 400,
        "err_msg": "this is error msg",
        "timestamp": 1589784667060,
        "data": null
    }
    """

    query_addr_req_params_schema = {
        'pro_id': And(int, lambda item: 0 <= item <= 100, error='`pro_id` must between 0 and 100'),
        Optional('order_id'): And(str, lambda item: 21 == len(item) and str(item).isnumeric(), error='`order_id` is invalid '),
        'token_name': And(str, lambda item: item in g_TOKEN_NAME_LIST , error='`token_name` is invalid'),
        'page_size' : And(int, lambda  item : 0 < item <= 200, error='`page_size` must between 1 and 200'),
        'page_index': And(int, lambda item : 0 < item <= 1000000, error='`page_index` is invalid, must greater than 0'),
    }

    def __init__(self, application , request, **kwargs):

        engine = create_engine(MYSQL_CONNECT_INFO, max_overflow=0, pool_size=5)
        MySqlSessionClass = sessionmaker(bind=engine, autocommit=True, autoflush=False)
        self.session = MySqlSessionClass()
        super().__init__(application=application, request=request, **kwargs)


    def get_all_addresses(self, **kwargs):
        """
        查询地址
        :param kwargs:
        :return:
        """

        pro_id = kwargs['pro_id']
        token_name = kwargs['token_name']

        # 使用 limit 进行分页
        page_size = kwargs['page_size']
        page_index = kwargs['page_index']

        limit_num = page_size
        offset_num = int((page_index - 1) * page_size)
        # session = MySqlSessionClass()
        if 'order_id' in kwargs:
            order_id = kwargs['order_id']

            order = self.session.query(AddAddressOrder)\
                                .filter_by(order_id=order_id,
                                            token_name=token_name,
                                            pro_id=pro_id)\
                                .first()

            assert isinstance(order, AddAddressOrder) , f'not found order data'

            start_idx = order.start_addr_index
            end_idx = order.end_addr_index

            total_count = self.session.query( func.count(Address.pro_id)) \
                                    .filter(and_(Address.pro_id == pro_id, Address.token_name == token_name,
                                            Address.address_index >= start_idx, Address.address_index <= end_idx))\
                                    .scalar()

            total_pages = math.ceil( total_count / page_size)

            if page_index > total_pages:
                err_msg = "page_index is too large"
                logger.error(msg=err_msg)
                raise RuntimeError(err_msg)

            rets = self.session.query(Address.address, Address.address_index) \
                .filter(and_(Address.pro_id == pro_id, Address.token_name == token_name,
                             Address.address_index >= start_idx, Address.address_index <= end_idx)) \
                .order_by(Address.address_index)\
                .limit(limit_num).offset(offset_num).all()
        else:
            total_count = self.session.query( func.count( Address.pro_id)) \
                        .filter(and_(Address.pro_id == pro_id, Address.token_name == token_name)).scalar()

            total_pages = math.ceil( total_count / page_size)
            if page_index > total_pages:
                err_msg = "page_index is too large"
                logger.error(msg=err_msg)
                raise RuntimeError(err_msg)

            rets = self.session.query(Address.address, Address.address_index) \
                        .filter(and_(Address.pro_id == pro_id, Address.token_name == token_name)) \
                        .order_by(Address.address_index)\
                        .limit(limit_num ).offset(offset_num) .all()

        logger.info(f'length: {len(rets)}')
        ret_addrs = []
        for addr in rets:
            # assert  isinstance(addr, Address)
            ret_addrs.append({
                'address' : addr.address,
                'index' : addr.address_index
            })

        return  ret_addrs, total_count, total_pages



    @apiauth
    def post(self):
        try:

            raw_req_params = json.loads(self.request.body)
            logger.info( f'request.body : {self.request.body}' )

            # 检验参数的合法性
            req_params = Schema(schema=self.query_addr_req_params_schema).validate(data=raw_req_params)

            addresses, total_count, total_pages = self.get_all_addresses(**req_params)

            # assert isinstance(req_params, dict)
            assert isinstance(addresses, list)

            rsp_data = req_params
            rsp_data['total_count'] = total_count
            rsp_data['total_pages'] = total_pages
            rsp_data['addresses'] = addresses

            # logger.info(f'{rsp_data}')
            self.write(self.success_ret_with_data(data=rsp_data))
        except Exception as e:
            logger.error(f'QueryAddress error occured: {e}')
            self.write(self.error_ret_with_data(err_code=400, err_msg=str(e), data=None))

        pass




class  QueryAddAddressOrder(BaseHandler):
    """
    @api {POST} http://192.168.10.174/api/wallet/queryaddaddressesorder  1.4.查询申请充币地址订单
    @apiVersion 0.0.1
    @apiName  queryaddaddressesorder
    @apiGroup 1.PG_Wallet
    @apiDescription  查询申请充币地址订单

    @apiParam {Integer} pro_id  项目方ID
    @apiParam {String} order_id  申请订单号

    @apiParamExample {json} 请求参数示例:
    {
        "pro_id":1,
        "order_id":"202005251048312179718",
    }


    @apiSuccess {Integer} err_code 错误码
    @apiSuccess {String} err_msg 错误信息
    @apiSuccess {Integer} timestamp  时间戳
    @apiSuccess {Object} data  数据
    @apiSuccess {Integer} data.pro_id  项目方id
    @apiSuccess {String} data.order_id  申请订单号
    @apiSuccess {String} data.token_name 币种名(BTC, HTDF, ETH) 注意: USDT共用ETH地址,不需单独申请; HRC20代币(例如:BTU)与HTDF共用地址, 不需要单独申请地址
    @apiSuccess {Integer} data.count 申请数量
    @apiSuccess {Integer} data.start_addr_index 地址起始索引
    @apiSuccess {Integer} data.end_addr_index 地址结束索引
    @apiSuccess {String} data.audit_status 订单审核状态(PENDING:待审核, REJECTED:已拒绝, PASSED:已通过)
    @apiSuccess {String} data.generate_status 地址生成状态(NOTYET:未生成, SUCCESS:生成完成)
    @apiSuccess {String} data.order_status  订单状态(PROCESSING:处理中, SUCCESS:成功, FAIL:失败)
    @apiSuccess {String} data.remark  审核备注信息
    @apiSuccess {String} data.active_status 启用状态,NO:未启用,YES:已启用.(注意: "未启用"表示网关尚开始监测地址入账, "已启用"表示已开始监测地址入账)
    @apiSuccess {Integer} data.order_complete_time   完成时间戳(如果订单未完成则为 null )
    @apiSuccess {Integer} data.order_create_time 订单生成时间戳
    @apiSuccess {Integer} data.audit_complete_time   审核(通过或拒绝)完成时间戳( 如果审核未完成则为 null)


    @apiSuccessExample {json}  Success-Example:
    HTTP/1.1 200 OK
    {
        "err_code": 0,
        "err_msg": null,
        "timestamp": 1590465671888,
        "data": {
            "pro_id": 1,
            "order_id": "202005251048312179718",
            "token_name": "HTDF",
            "count": 10,
            "start_addr_index": 12321,
            "end_addr_index": 12330,
            "audit_status": "PASSED",
            "generate_status": "SUCCESS",
            "order_status": "SUCCESS",
            "remark": "12321 to 12330",
            "active_status": "YES",
            "order_complete_time": 1590374936,
            "order_create_time": 1590374911,
            "audit_complete_time": 1590374935
        }
    }

    @apiErrorExample Error-Example:
    HTTP 1.1/ 200
    {
        "err_code": 400,
        "err_msg": "this is error msg",
        "timestamp": 1589784667060,
        "data": null
    }
    """

    query_addaddressorder_schema = {
        'pro_id': And(int, lambda item: 0 <= item <= 100, error='`pro_id` must between 0 and 100'),
        'order_id': And(str, lambda item: 21 == len(item) and str(item).isnumeric(), error='`order_id` is invalid '),
    }

    def get_order_data(self, pro_id : int, order_id : str) -> Union[dict, None]:
        """
        获取申请订单数据
        :param kwargs:
        :return:
        """
        engine = create_engine(MYSQL_CONNECT_INFO,
                               max_overflow=0,
                               pool_size=5)
        Session = sessionmaker(bind=engine, autocommit=True, autoflush=False)
        session = Session()

        # 查询操作不需要 flush
        orderdata = session.query(AddAddressOrder).filter_by(order_id=order_id, pro_id=pro_id).first()

        if orderdata is None:
            raise Exception('not found order data')

        assert isinstance(orderdata, AddAddressOrder)

        ret_info = {
            'pro_id': orderdata.pro_id,
            'order_id': orderdata.order_id,
            'token_name' : orderdata.token_name,
            'count' : orderdata.count,
            'start_addr_index': orderdata.start_addr_index,
            'end_addr_index': orderdata.end_addr_index,
            'audit_status': orderdata.audit_status,
            'generate_status' : orderdata.generate_status,
            'order_status': orderdata.order_status,
            'remark': orderdata.remark,
            'active_status': orderdata.active_status,
            'order_complete_time': datetime_to_timestamp(orderdata.order_complete_time) \
                                if orderdata.order_complete_time is not None else None,
            'order_create_time': datetime_to_timestamp(orderdata.order_create_time) \
                                if orderdata.order_create_time is not None else None,
            'audit_complete_time': datetime_to_timestamp(orderdata.audit_complete_time) \
                                if orderdata.audit_complete_time is not None else None ,
        }

        return ret_info


    @apiauth
    def post(self):
        try:

            raw_req_params = json.loads(self.request.body)
            logger.info(f'request.body : {self.request.body}')

            # 检验参数的合法性
            req_params = Schema(schema=self.query_addaddressorder_schema).validate(data=raw_req_params)

            order_data = self.get_order_data(**req_params)

            assert isinstance(order_data, dict)
            rsp_data = order_data

            logger.info(f'{rsp_data}')

            self.write(self.success_ret_with_data(data=rsp_data))
        except Exception as e:
            logger.error(f'QueryAddAddressOrder error occured: {e}')
            self.write(self.error_ret_with_data(err_code=400, err_msg=str(e), data=None))

        pass

