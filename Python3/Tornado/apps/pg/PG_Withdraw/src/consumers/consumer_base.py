#!coding:utf8

#author:yqq
#date:2020/5/11 0011 10:59
#description:  提币消费者抽象基类


import json
import time
from decimal import Decimal

import pika
import abc
import logging

from bitcoin import SelectParams
from bitcoin.wallet import CBitcoinAddress
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import StreamLostError
from schema import And, Schema, SchemaError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.constant import WithdrawStatus, RABBIT_MQ_USER_NAME, RABBIT_MQ_PASSWORD, RABBIT_MQ_PORT, RABBIT_MQ_IP, \
    RABBIT_MQ_VRIATUAL_HOST, MONITOR_EXCHANGE, Q_TX_MONITOR, RABBIT_DELIVERY_MODE, g_TOKEN_NAME_LIST, \
    MONITOR_ROUTINGKEY, RABBIT_DIRECT_MODE, g_MNEMONIC, SMS_EXCHANGE, Q_SMS, SMS_ROUTINGKEY, RABBIT_MQ_HEARTBEAT_TIME, \
    RABBIT_BLOCKED_CONNECTION_TIMEOUT, g_IS_MAINNET

from src.lib.exceptions import InvalidParametersException, TxBroadcastFailedException, BalanceNotEnoughException, \
    MqBodyException, SqlCDUSException, HttpConnectionError
from src.lib.my_bip44.wrapper import gen_bip44_subprivkey_from_mnemonic
from src.lib.pg_utils import decimal_to_str
from src.model.model import WithdrawOrder
import traceback



def is_valid_addr(address: str, token_name: str) -> bool:

    try:
        if token_name in ['HTDF', 'BTU']:
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
        logging.error(f'is_valid_addr() , {address} is invalid address, error:{e}')
        return False

    pass

class TransferFuncResponse:
    block_height = 0
    transaction_status = WithdrawStatus.transaction_status.NOTYET
    confirmations = 0
    tx_hash = ''
    block_time = 0



class  WithdrawConsumerBase(metaclass=abc.ABCMeta):

    withdraw_body_schema = {
        'serial_id': And(str, lambda item: 21 == len(item) and str(item).isnumeric(),
                         error='`serial_id` is invalid '),  # 支付网关生成的唯一流水号
    }

    withdraw_addr_schema = {
        'from_addr': And(str, lambda item: 30 < len(item) < 80 , error='`from` is invalid address'),
        'to_addr': And(str, lambda item: 30 < len(item) < 80 , error='`to` is invalid address'),
        'amount': And(Decimal, lambda item: 0.00001 < item < 999999999, error='`amount` is invalid, must be decimal'),
        'token_name': And(str, lambda item: item in g_TOKEN_NAME_LIST, error=f'`token_name` is invalid, must in {g_TOKEN_NAME_LIST}'),
        'memo':  str
    }

    channel = None  #MQ
    logger = None  #日志
    session = None  #数据库

    def __init__(self):
        pass

    @abc.abstractmethod
    def check_src_address_balance(self, **kwargs) -> bool:
        """
        抽象方法:  子类必须实现

        获取地址余额
        :param kwargs:
        :return:
        """

        pass


    @abc.abstractmethod
    def transfer(self,  **kwargs ) -> TransferFuncResponse:
        """
        抽象方法,  子类必须实现此方法

        转账函数
        :param args:
        :param kwargs:
        :return:  TransferFuncResponse
        """
        pass

    @abc.abstractmethod
    def init_db_session(self):
        """
        抽象方法 ,  子类必须实现
        在此函数中  初始化 数据库session
        :return:
        """
        pass

    @abc.abstractmethod
    def init_mq_connect(self):
        """
        抽象方法 ,  子类必须实现
        在此方法中初始化   MQ
        :return:
        """
        pass


    @abc.abstractmethod
    def init_others(self):
        """
        抽象方法 , 子类必须实现

        初始化其他东西
        :return:
        """

        pass


    #@final 方法
    #不要重写此方法!!
    def start(self):
        """DON'T OVERRIDE THIS METHOD"""
        #此方法不允许子类重写!

        self.init_db_session()
        self.init_mq_connect()
        self.init_others()

        self.logger.info(f'{__name__} started .......')

        assert isinstance(self.channel, BlockingChannel ), "channel is not BlockingChannel "
        self.channel.start_consuming()
        pass



    def send_msg_to_tx_monitor_queue(self, serial_id: str) -> None:
        '''
        发送mq队列：通知monitor_notify转账成功
        :param tx_hash:
        :return:
        '''

        credentials = pika.PlainCredentials(RABBIT_MQ_USER_NAME, RABBIT_MQ_PASSWORD)
        # 创建连接
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            RABBIT_MQ_IP, RABBIT_MQ_PORT, RABBIT_MQ_VRIATUAL_HOST, credentials))

        channel = connection.channel()


        # 单条模式
        channel.exchange_declare(MONITOR_EXCHANGE, RABBIT_DIRECT_MODE)
        # 创建一个新队列balance，设置durable=True 队列持久化，注意不要跟已存在的队列重名，否则有报错
        channel.queue_declare(queue=Q_TX_MONITOR, durable=True)

        # 绑定队列与交换器
        channel.queue_bind(exchange=MONITOR_EXCHANGE, queue=Q_TX_MONITOR)

        # 发送消息
        # n RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange.
        channel.basic_publish(exchange=MONITOR_EXCHANGE,
                              routing_key=MONITOR_ROUTINGKEY,
                              body=f'{json.dumps({"serial_id":serial_id})}',
                              properties=pika.BasicProperties(
                                  delivery_mode=RABBIT_DELIVERY_MODE,  # 使消息或任务也持久化存储
                              ))
        self.logger.info('send_msg_to_tx_monitor_queue successed')

    def send_sms_queue(self, sms_content: str, tel_no : str) -> None:
        '''
        发送短信
        :param tx_hash:
        :return:
        '''
        self.logger.info(f'tel_no:{tel_no}, sms_content:{sms_content}')

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
        self.logger.info('send msg to sms queue successed.')


    # MQ 回调函数
    def on_message_callback(self, channel, method, properties, body):
        """
        :param channel: channel
        :param method:
        :param properties:
        :param body: 消息体
        :return: 无
        """

        serial_id = ''
        try:
            try:
                msg_data = json.loads(body, encoding='utf8')
                if not isinstance(msg_data, dict) and 'serial_id' in msg_data:
                    raise MqBodyException("msg body format error")
                # assert isinstance(channel, BlockingChannel), "channel is not BlockingChannel "
                serial_id = msg_data["serial_id"]

                self.logger.info( f"msg_data:{ json.dumps(msg_data, indent=4) }" )


                # 查询是否有serialid
                time.sleep(1)
                order_data = self.session.query(WithdrawOrder).filter_by(serial_id=serial_id).first()
                self.logger.info(f'order_data sql:{order_data}')

                assert isinstance(order_data, WithdrawOrder), 'order_data is not WithdrawOrder'

                data = {
                    'from_addr': order_data.from_addr,
                    'to_addr': order_data.to_addr,
                    'token_name': order_data.token_name,
                    'amount': order_data.amount,
                    'memo': order_data.memo,
                }

                self.logger.info(f"serial_id:{serial_id},data:{data}")
                params = Schema(schema=self.withdraw_addr_schema).validate(data=data)

                if not is_valid_addr(address=order_data.from_addr, token_name=order_data.token_name):
                    raise Exception('`from` is invalid address')

                if not is_valid_addr(address=order_data.to_addr, token_name=order_data.token_name):
                    raise Exception('`to` is invalid address')



                #只对未进行转账的订单 进行转账
                if order_data.transaction_status != WithdrawStatus.transaction_status.NOTYET:
                    self.logger.info(f'serial_id:{serial_id} tranaction_status is {order_data.transaction_status}, no need transfer')
                else:
                    self.logger.info(f'serial_id:{serial_id} tranaction_status is NOTYET , starting transfer ')

                    #根据pro_id推导出私钥
                    coin_type = order_data.token_name.upper().strip()
                    if coin_type == 'USDT':
                        coin_type = 'ETH'

                    if coin_type in ['BTU']:  #HRC20 代币
                        coin_type = 'HTDF'

                    nettype = 'mainnet'  if g_IS_MAINNET else 'testnet'
                    priv_key, addr = gen_bip44_subprivkey_from_mnemonic(mnemonic=g_MNEMONIC,
                                                       coin_type=coin_type,
                                                       account_index=order_data.pro_id ,
                                                       address_index=0,  # 0 索引作为用户的出币地址
                                                       nettype=nettype)

                    if not addr.lower() == order_data.from_addr.lower():
                        raise InvalidParametersException( f'ADDRESS NOT MATCH! { addr  } != { order_data.from_addr }')
                        pass


                    #检查出币地址余额,如果余额不够发送短信通知用户, 然后, 抛出BalanceNotEnoughException
                    params['pro_id'] = order_data.pro_id
                    self.check_src_address_balance(**params)


                    params['priv_key'] = priv_key


                    # 调用子类自己的transfer
                    trans_rsp = self.transfer(**params)

                    update_fields = {
                        "block_height": trans_rsp.block_height,
                        "transaction_status": trans_rsp.transaction_status,
                        "tx_hash" : trans_rsp.tx_hash,
                    }

                    if trans_rsp.transaction_status == WithdrawStatus.transaction_status.SUCCESS \
                            or trans_rsp.transaction_status == WithdrawStatus.transaction_status.FAIL:
                        update_fields['block_time'] = trans_rsp.block_time
                        update_fields['tx_confirmations'] = trans_rsp.confirmations
                        update_fields['tx_hash'] = trans_rsp.tx_hash

                    #TODO: 异常处理, 增加写文件
                    # 存入tx_hash和更新完成时间
                    sql_str = self.session.query(WithdrawOrder) \
                                           .filter_by(serial_id=serial_id) \
                                           .update(update_fields)

                    self.session.flush()  #修改操作 , 手动 flush


                    self.logger.info(f'update_tx_hash sql: {sql_str}')

                    pass

                channel.basic_ack(delivery_tag=method.delivery_tag)

                self.logger.info(f"send_msg_to_tx_monitor_queue starting, serial_id: {serial_id} ...")

                # 发送消息通知
                self.send_msg_to_tx_monitor_queue(serial_id=serial_id)
                self.logger.info(f"send_msg_to_tx_monitor_queue finished,  serial_id : {serial_id}")

            except SchemaError as e:
                # 处理  from to  amount  memo 非法格式!
                self.logger.error(f' serial_id : {serial_id}, error: {str(e)} ')

                # 更新订单的状态  transaction_status 为  FAIL
                self.session.query(WithdrawOrder) \
                    .filter_by(serial_id=serial_id) \
                    .update({
                    "remark" : "invalid order data",
                    "transaction_status": WithdrawStatus.transaction_status.FAIL
                })

                channel.basic_ack(delivery_tag=method.delivery_tag)
                pass

            except StreamLostError as e:
                #如果MQ连接已经断开
                self.logger.error( f'{e}' )
                self.init_mq_connect()  #重新连接一下
                pass
            except InvalidParametersException as e:
                #  参数不对
                self.logger.error(f"InvalidParametersException: {e}")
                sql_ret = self.session.query(WithdrawOrder)\
                                        .filter_by(serial_id=serial_id)\
                                        .update({
                                            "remark": str(e),
                                            "transaction_status": WithdrawStatus.transaction_status.FAIL
                                        })

                self.session.flush()   #修改操作 , 手动 flush
                self.logger.error(f'sql_ret :{sql_ret}')
                channel.basic_ack(delivery_tag=method.delivery_tag)
            except HttpConnectionError as e:
                assert isinstance(channel, BlockingChannel)
                #回nack ,
                self.logger.error(f"{e}")
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                pass
            except TxBroadcastFailedException as e:
                # 广播失败, 一般是 nonce 或 sequence 不对
                self.logger.error(f"{e}")

                #这里回 nack
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            except BalanceNotEnoughException as e:
                #  通知项目方赶紧充值 账户余额不足 短信通知用户
                self.logger.error(f"{e}")
                sql_ret = self.session.query(WithdrawOrder)\
                                                    .filter_by(serial_id=serial_id)\
                                                    .update({
                                                        "remark": f"balance not enough:{e}",
                                                        "transaction_status": WithdrawStatus.transaction_status.FAIL
                                                    })
                self.session.flush()  #修改操作 , 手动 flush

                self.logger.info(f'sql: {sql_ret}')
                channel.basic_ack(delivery_tag=method.delivery_tag)
            except MqBodyException as e:
                #  mq接收信息格式错误
                self.logger.error(f"{e}")
                sql_ret = self.session.query(WithdrawOrder) \
                    .filter_by(serial_id=serial_id) \
                    .update({
                    "remark": "msg format is illegal",
                    "transaction_status": WithdrawStatus.transaction_status.FAIL
                })
                self.session.flush()  # 修改操作 , 手动 flush

                self.logger.info(f'sql: {sql_ret}')
                channel.basic_ack(delivery_tag=method.delivery_tag)
            except SqlCDUSException as e:
                # SQL异常处理
                self.logger.error(f"{e}")
                sql_ret = self.session.query(WithdrawOrder) \
                    .filter_by(serial_id=serial_id) \
                    .update({
                    "remark": "internal error: db error",
                    "transaction_status": WithdrawStatus.transaction_status.FAIL
                })
                self.session.flush()  # 修改操作 , 手动 flush

                channel.basic_ack(delivery_tag=method.delivery_tag)
                self.logger.error(f"{e}")
            except Exception as e:
                self.logger.error(f"{e}")
                sql_ret = self.session.query(WithdrawOrder) \
                    .filter_by(serial_id=serial_id) \
                    .update({
                    "remark": f"unknow error: {str(e)[:200]} ",
                    "transaction_status": WithdrawStatus.transaction_status.FAIL
                })
                self.session.flush()  # 修改操作 , 手动 flush

                channel.basic_ack(delivery_tag=method.delivery_tag)
                traceback.print_exc()
            finally:
                pass

        except Exception as e:
            self.logger(f'error:{e}')
            pass

        # 收尾
        pass





