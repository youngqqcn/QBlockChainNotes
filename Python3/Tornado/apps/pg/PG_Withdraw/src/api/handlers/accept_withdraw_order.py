#!coding:utf8

#author:yqq
#date:2020/4/30 0030 19:27
#description:  接收用户提币请求


"""
400 坏请求（Bad Request）
401 无授权（Unauthorized）
402 所需付款 （Payment Required）
403 禁止（Forbidden）
404 未找到 （Not Found）
405 方法不允许 （Method Not Allowed）
406 非可接受的（Not Acceptable）
407 需要代理身份验证（Proxy Authentication Required）
408 请求超时 (Request Timeout)
409 冲突(Conflict)
410 好了（Gone）？？？
411 所需长度（Length Required ）
412  先决条件失败（Precondition Failed）
413 请求实体太大（Request Entity Too Large）
414 请求URI太长（Request-URI Too Long）
415 不支持的媒体类型（Unsupported Media Type）
416 不能满足所请求的范围（Requested Range Not Stisfiable）
417 期望失败（Expectation Failed）
"""
import json
from decimal import Decimal

import pika
from bitcoin import SelectParams
from bitcoin.wallet import CBitcoinAddress
from schema import And, Schema, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from src.api.handlers.serial_fanout_mqsend import mqsend
from src.config.constant import WITHDRAW_ORDER_EXCHANGE, Q_HTDF_WITHDRAW, Q_ETH_ERC_WITHDRAW, HTDF_ROUTING_KEY, \
    ETH_ROUTING_KEY, ERC20_USDT_ROUTING_KEY, g_TOKEN_NAME_LIST, RABBIT_MQ_PORT, RABBIT_MQ_IP, RABBIT_MQ_VRIATUAL_HOST, \
    RABBIT_DIRECT_MODE, RABBIT_DELIVERY_MODE, RABBIT_MQ_PASSWORD, RABBIT_MQ_USER_NAME, WithdrawStatus, \
    MYSQL_CONNECT_INFO, g_IS_MAINNET, BTC_ROUTING_KEY, Q_BTC_WITHDRAW, HRC20_BTU_ROUTING_KEY
from src.api.handlers.handler_base import BaseHandler, apiauth
import logging
import datetime


#使用 sqlalchemy 进行 ORM
from src.lib.pg_utils import round_down
from src.model.model import WithdrawOrder, WithdrawConfig

logger = logging.getLogger(__name__)


#从model导入


def is_valid_addr(address: str, token_name: str) -> bool:

    try:
        if token_name == 'HTDF' or token_name == 'BTU':
            return len(address) == 43 and  address.startswith('htdf1') and address.islower()
        elif token_name == 'ETH' or token_name == 'USDT':
            return len(address) == 42 and  address.startswith('0x') and  int(address, base=16)
        elif token_name == 'BTC':
            if g_IS_MAINNET:
                SelectParams('mainnet')
                addr = CBitcoinAddress(s = address)
            else:
                SelectParams('testnet')
                addr = CBitcoinAddress(s = address)

            assert addr is not None , 'addr is None'

            #如果没有抛异常直接返回即可
            return True
        else:
            raise RuntimeError(f"unknow token_name: {token_name}")
    except Exception as e:
        logger.error(f'is_valid_addr() , {address} is invalid address, error:{e}')
        return False

    pass


class AcceptWithdrawOrder(BaseHandler):
    """
    @api {POST} http://192.168.10.174/api/withdraw/withdraw  3.2.提币接口
    @apiVersion 0.0.1
    @apiName  withdraw
    @apiGroup 3.PG_Withdraw
    @apiDescription  提币接口

    @apiParam {String} order_id  订单号,注意:此order_id是项目方自己生成的提币业务订单号,注意和其他接口中的order_id区分
    @apiParam {String} from_address 源地址,提币的from地址, 项目方的出币地址(由支付网关预先分配), 注意:USDT共用ETH的出币地址; HRC20(如: BTU)共用HTDF出币地址
    @apiParam {String} to_address  目的地址
    @apiParam {String} amount  金额, 普通币种最多保留8小数, USDT最多保留6小数, 如超出则截断
    @apiParam {String} token_name 币种, (BTC, HTDF, ETH, USDT, BTU)
    @apiParam {Integer} pro_id 项目方ID
    @apiParam {String} [memo] 转账备注(如果不填,则不需要加此字段;如果填,必须是字符串,不能是null) , 注意: 目前仅HTDF和HRC20代币(例如:BTU)支持memo
    @apiParam {String} callback_url 回调通知地址, 当订单状态改变时主动通知项目方,项目方必须提供通知接口的url, 详细说明请看"公共参数说明"

    @apiParamExample {json} 请求参数示例:
    {
        "order_id": "932360002322392082354",
        "from_address": "0x3e6ff85cf9d3340b213faea15751c86d74ffc525",
        "to_address": "0x954d1a58c7abd4ac8ebe05f59191cf718eb0cb89",
        "amount": "0.0011",
        "token_name": "ETH",
        "pro_id": 3,
        "callback_url": "http://192.168.10.29:8001/notifywithdraw"
    }

    @apiSuccess {Integer} err_code 错误码(0:成功 其他错误码:失败)
    @apiSuccess {String} err_msg 错误信息(成功时此字段为null)
    @apiSuccess {Integer} timestamp  时间戳(毫秒)
    @apiSuccess {Object} data 数据
    @apiSuccess {String} data.serial_id 序列号(支付网关生成的唯一的标识)
    @apiSuccess {String} data.order_id 订单号(与用户请求时提交的order_id相同)


    @apiSuccessExample {json}  Success-Example:
    HTTP/1.1 200 OK
    {
        "err_code": 0,
        "err_msg": null,
        "timestamp": 1589784667060,
        "data": {
            "serial_id":"202005181810193441231",
            "order_id":"932360002322392082354"
        }
    }


    @apiErrorExample Error-Example:
    HTTP 1.1/ 200
    {
        "err_code": 400,
        "err_msg": "order already exists",
        "timestamp": 1589784667060,
        "data": null
    }

    """

    #关于schema的使用
    # https://github.com/keleshev/schema/
    # https://github.com/keleshev/schema/blob/master/test_schema.py
    #提币请求参数




    withdraw_request_schema = {

        # 判断  order_id  必须是 str, 并且是有效字符串
        'order_id': And(str, lambda item: 10 < len(item) and str(item).isnumeric(), error='`order_id` is invalid '),

        'from_address': And(str, lambda item: 30 < len(item) < 80, error='`from` is invalid address'),

        'to_address': And(str, lambda item: 30 < len(item) < 80, error='`to` is invalid address'),

        'amount': And(str, lambda item: 0.00001 < Decimal(item) < 999999999, error=f'`amount` is invalid , must be str, and 0.00001 < amout < 999999999'),
        'token_name' : And(str, lambda item : item in g_TOKEN_NAME_LIST, error='`token_name` is invalid' ),
        'pro_id' : And(int, lambda item : item < 100000000, error='`pro_id` is invalid'),
        Optional('memo') : And(str, lambda item : len(item) < 50 and str(item).isprintable()
                                                  and '&' not in str(item) and '*' not in str(item)
                                                  and '\\' not in item and '^' not in str(item)
                                                  and '$' not in str(item) and '%' not in str(item)
                                                  and '`' not in str(item),
                               error='`memo` is invalid'),
        'callback_url': And(str, lambda item : str(item).startswith('http'))
    }

    def send_msg_to_mq(self, serial_id, token_name):
        """
        发送消息到消息队列
        :param serial_id: 流水号
        :param token_name: 币种
        :return: 无
        """
        logging.info(f"token_name:{token_name}, serial_id:{serial_id}")


        credentials = pika.PlainCredentials(RABBIT_MQ_USER_NAME, RABBIT_MQ_PASSWORD)

        # 创建连接
        connection = pika.BlockingConnection(
                            pika.ConnectionParameters(RABBIT_MQ_IP, RABBIT_MQ_PORT, RABBIT_MQ_VRIATUAL_HOST, credentials))


        channel = connection.channel()
        channel.exchange_declare(WITHDRAW_ORDER_EXCHANGE, RABBIT_DIRECT_MODE)

        # 声明queue
        # 创建一个新队列balance，设置durable=True 队列持久化，注意不要跟已存在的队列重名，否则有报错
        channel.queue_declare(queue=Q_HTDF_WITHDRAW, durable=True)
        channel.queue_declare(queue=Q_ETH_ERC_WITHDRAW, durable=True)

        # 绑定队列与交换器
        # assert  token_name in g_TOKEN_NAME_LIST

        if token_name == HTDF_ROUTING_KEY or token_name == HRC20_BTU_ROUTING_KEY:
            queue_name = Q_HTDF_WITHDRAW
        elif token_name == ETH_ROUTING_KEY or token_name == ERC20_USDT_ROUTING_KEY:
            queue_name = Q_ETH_ERC_WITHDRAW
        elif token_name == BTC_ROUTING_KEY:
            queue_name = Q_BTC_WITHDRAW
        else:
            raise Exception(f"invalid token_name:{token_name}")

        # 绑定队列与交换器
        channel.queue_bind(exchange=WITHDRAW_ORDER_EXCHANGE, queue=queue_name, routing_key=token_name)

        # 发送消息
        # n RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange.
        channel.basic_publish(exchange=WITHDRAW_ORDER_EXCHANGE,
                              routing_key=token_name,  # 一个routing_key不知道填哪一个
                              body=f'{json.dumps(serial_id)}',
                              properties=pika.BasicProperties(
                                  delivery_mode=RABBIT_DELIVERY_MODE,  # 使消息或任务也持久化存储
                              ))

        logging.info(" send_msg_to_mq  successed! ")

        pass


    def generate_serial_id(self) -> str:
        """
        生成流水号
        :return: 流水号
        """
        import time
        serial_id =  str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))) + str(int(time.perf_counter_ns()))[-7:]
        return  serial_id

    def is_order_exists(self, orderid: str, pro_id: int) -> bool:
        """
        根据订单号和项目方号判断 订单是否已经存在
        :param orderid: 项目方传来的订单号
        :param pro_id: 项目方id
        :return:  bool
        """
        engine = create_engine(MYSQL_CONNECT_INFO,
                               max_overflow=0,
                               pool_size=5)

        #参考: https://www.jianshu.com/p/b219c3dd4d1e
        Session = sessionmaker(bind=engine, autocommit=True, autoflush=False)
        session = Session()

        ret_data = session.query(WithdrawOrder).filter_by(order_id=orderid, pro_id=pro_id).all()
        # session.commit()
        # session.flush() #查询操作不需要 flush

        logging.info(f'ret_data : {ret_data}')

        return len(ret_data) != 0

    def insert_order(self, orderid , serial_id, token_name, from_addr, to_addr, amount, challback_url, pro_id, memo):
        """
         保存订单
        :param orderid:
        :param serial_id:
        :param token_name:
        :param from_addr:
        :param to_addr:
        :param amount:
        :param challback_url:
        :param pro_id:
        :param memo:
        :return:
        """

        engine = create_engine(MYSQL_CONNECT_INFO,
                               max_overflow=0,
                               pool_size=5)
        Session = sessionmaker(bind=engine, autocommit=True, autoflush=False)  #手动刷新
        session = Session()
        logging.info(f'insert_order(): serial_id:{serial_id}, order_id:{orderid}')

        #仅HTDF和HRC20支持 memo
        tx_memo = memo if memo is not None else ''
        if token_name not in ['HTDF', 'BTU']:
            tx_memo = ''

        order = WithdrawOrder(serial_id=serial_id,
                              token_name=token_name,
                              order_id=orderid,
                              pro_id=pro_id,
                              callback_url=challback_url,
                              from_addr=from_addr,
                              to_addr=to_addr,
                              memo=tx_memo,
                              amount=amount,
                              block_height=0,
                              tx_hash='',
                              tx_confirmations=0,
                              transaction_status= WithdrawStatus.transaction_status.NOTYET ,
                              order_status = WithdrawStatus.order_status.PROCESSING ,
                              notify_status = WithdrawStatus.notify_status.NOTYET,
                              notify_times=0,
                              # block_time=None, #datetime.datetime.now(),
                              # complete_time= None,  #datetime.datetime.now(),
                              remark=''
                              )

        logging.info( f'order: {order}')
        session.add(instance=order, _warn=True)
        # session.commit()
        session.flush()  #增加操作需要 flush

        pass


    def check_valid_params(self, pro_id : int, token_name : str, from_addr : str, amount : Decimal ):
        """
        检查提币参数 是否符合提币配置
        :param pro_id : 项目方id
        :param from_addr:
        :param amount: 转账金额
        :return:
        """
        engine = create_engine(MYSQL_CONNECT_INFO,
                               max_overflow=0,
                               pool_size=5)
        Session = sessionmaker(bind=engine, autocommit=True, autoflush=False)  # 手动刷新
        session = Session()
        # logging.info(f'insert_order(): serial_id:{serial_id}, order_id:{orderid}')


        cfg = session.query( WithdrawConfig ).filter_by(pro_id=pro_id, token_name=token_name).first()
        if cfg is None:
            raise Exception('invalid `pro_id` or `from_addr` ')

        assert isinstance(cfg, WithdrawConfig), 'cfg is not istance of WithdrawConfig '

        if cfg.address.lower() != str(from_addr).lower():
            raise Exception('illegal `from_addr`')

        if not (cfg.min_amount <= amount <= cfg.max_amount):
            raise Exception('illegal `amount` ')

        return




    def process_withdraw_order(self, **kwargs) :
        """
        处理提币
        :param kwargs:
        :return:
        """
        logger.info( f'kwargs: { json.dumps(kwargs)}')

        orderid = str(kwargs['order_id']).strip()
        from_addr = str(kwargs['from_address']).strip()
        to_addr = str(kwargs['to_address']).strip()
        amount =  round_down( Decimal( kwargs['amount']) )
        token_name = str(kwargs['token_name']).strip()
        challback_url = kwargs['callback_url']
        pro_id = kwargs['pro_id']
        memo = '' if 'memo' not in kwargs else  kwargs['memo']


        if not is_valid_addr(address=from_addr, token_name=token_name):
            raise Exception('`from` is invalid address')

        if not is_valid_addr(address=to_addr, token_name=token_name):
            raise Exception('`to` is invalid address')


        self.check_valid_params(pro_id=pro_id, token_name=token_name, from_addr=from_addr, amount=amount)



        #处理, 如果有异常, 则抛出异常
        #根据订单号查询是否存在该订单
        if self.is_order_exists(orderid, pro_id):
            logging.info(f"order already exists, order_id : {orderid}")
            #订单重复咋处理?   直接抛异常
            raise Exception("order already exists")


        #生成唯一的流水号
        serial_id =  self.generate_serial_id()

        # 保存订单
        self.insert_order(orderid, serial_id, token_name ,from_addr, to_addr, amount, challback_url, pro_id, memo)

        # 发送消息到mq
        msg = {
            "serial_id": serial_id
        }

        logger.info('start send MQ...')

        #TODO  如果发送失败, 应该从数据库里面删除刚刚插入订单那数据
        self.send_msg_to_mq(msg, token_name)

        logger.info('send MQ sucessed')


        #如果一切顺利, 返回
        ret_info = {
            'serial_id' : serial_id,
            'order_id' : orderid
        }

        return ret_info

    @apiauth
    def post(self):

        try:
            logger.info(f'request.body : { self.request.body }')

            raw_req_params = json.loads(self.request.body)

            #检验参数的合法性
            req_params = Schema(schema=self.withdraw_request_schema).validate(data=raw_req_params)

            ret_info = self.process_withdraw_order(**req_params)
            logger.info('process_withdraw_order success returned ')

            rsp_data = ret_info

            #返回, 订单接收成功
            self.write( self.success_ret_with_data(data=rsp_data) )
            pass
        except Exception as e:
            logger.error(f'AcceptWithdrawOrder error occured: {e}')
            self.write(self.error_ret_with_data(err_code=400, err_msg=str(e), data=None))

        pass
