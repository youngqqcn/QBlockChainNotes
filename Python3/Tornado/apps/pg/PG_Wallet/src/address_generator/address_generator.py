#!coding:utf8

#author:yqq
#date:2020/5/14 0014 13:46
#description: 地址生
import json
import logging
import time
from datetime import datetime
from typing import List

import pika
import redis
from pika.adapters.blocking_connection import BlockingChannel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# from src.api.handlers.address_handler import g_MNEMONIC
from src.model.model import Address, AddAddressOrder
from src.config.constant import RABBIT_MQ_USER_NAME, RABBIT_MQ_PASSWORD, RABBIT_MQ_IP, RABBIT_MQ_PORT, \
    RABBIT_MQ_VRIATUAL_HOST, ADDRESS_GENERATE_EXCHANGE, RABBIT_DIRECT_MODE, Q_ADDRESS_GENERATE, \
    ADDRESS_GENERATE_ROUTINGKEY, RABBIT_MQ_HEARTBEAT_TIME, RABBIT_BLOCKED_CONNECTION_TIMEOUT, g_MNEMONIC, \
    AddrAddressOrderGenerateStatus, AddAddressOrderStatus, AddrAddressOrderActiveStatus, REDIS_HOST, REDIS_PORT, \
    REDIS_ADDRESS_POOL_DB_NAME, REDIS_DEPOSIT_ADDRESS_POOL_NAME, \
    MYSQL_CONNECT_INFO, AddrAddressOrderAuditStatus, g_IS_MAINNET

from src.lib.log import get_default_logger

import traceback

logger = get_default_logger()



def generate_address( pro_id : int,
                     token_name : str,
                     account_index : int,
                     start_addr_index : int,
                     end_addr_index : int) -> List[Address]:
    """
    生成地址
    :return: [ Address ]
    """

    start_address_index = start_addr_index

    mnemonic = g_MNEMONIC


    end_address_index = end_addr_index

    addrs_objs = []
    for addr_index in range(start_address_index, end_address_index + 1):
        from src.lib.my_bip44.wrapper import gen_bip44_subaddr_from_mnemonic

        nettype = 'mainnet'
        if not g_IS_MAINNET:
            nettype = 'testnet'

        tmp_addr = gen_bip44_subaddr_from_mnemonic(mnemonic=mnemonic,
                                                   coin_type=token_name,
                                                   account_index=account_index,
                                                   address_index=addr_index,
                                                   nettype=nettype)



        logger.info(f'index:{addr_index}, addr:{tmp_addr}')


        addrs_objs.append(Address(address=tmp_addr,
                                  token_name=token_name,
                                  pro_id=pro_id,
                                  account_index=account_index,
                                  address_index=addr_index,
                                  create_time=datetime.now()))

    return addrs_objs


def callback(channel, method, properties, body):
    engine = create_engine(MYSQL_CONNECT_INFO, max_overflow=0, pool_size=5, )
    MySqlSessionClass = sessionmaker(bind=engine, autoflush=False, autocommit=True)
    session = MySqlSessionClass()
    order_id = ''
    try:
        time.sleep(3)

        logging.info("mq msg is  {}".format(body))
        msg_data = json.loads(body, encoding='utf8')
        if not isinstance(msg_data, dict) or 'order_id' not in msg_data:
            raise Exception("MQ body format error")

        # handler( session, msg_data['serial_id'], logger)

        order_id = msg_data['order_id']
        audit_complete_time = datetime.fromtimestamp(msg_data['audit_complete_time'])\
                                        if 'audit_complete_time' in msg_data else datetime.now()


        #等待几秒, 等审核状态改变
        order_data = None
        for n in range(3):
            order_data = session.query( AddAddressOrder )\
                                    .filter_by(order_id=order_id)\
                                    .first()

            if order_data is None:
                logger.error(f'NOT FOUND {order_id} in database!')
                raise Exception(f'NOT FOUND {order_id} in database!')

            assert isinstance(order_data, AddAddressOrder), 'order_data is not AddAddressOrder '

            if order_data.audit_status == AddrAddressOrderAuditStatus.PASSED:
                logger.info(f'order {order_id} , audit status is {order_data.audit_status}')
                break
            logger.info(f'order {order_id} , audit status is {order_data.audit_status}, sleep 3secs for audit_status changed ')
            time.sleep(n + 1)
            pass


        if not order_data.order_status == AddAddressOrderStatus.PROCESSING:
            logger.info(f'order {order_id} , order status is {order_data.order_status} ,  basic_ack  directly ')
            channel.basic_ack(delivery_tag=method.delivery_tag)
        else:
            straddrs_list = []
            addrs_obj_list = generate_address(pro_id=order_data.pro_id,
                                              token_name=order_data.token_name,
                                              account_index=order_data.pro_id,
                                              start_addr_index=order_data.start_addr_index,
                                              end_addr_index=order_data.end_addr_index
                                              )

            if len(addrs_obj_list) != order_data.count:
                logger.error(f'len(addrs_obj_list) != order_data.count : {len(addrs_obj_list)} != {order_data.count}  ')
                raise Exception


            # 直接新建一个连接,
            session = MySqlSessionClass()
            # logger.info(f'session.is_active:{session.is_active}')

            logger.info(f' addr count: {len(addrs_obj_list)} ')
            for addr_obj in addrs_obj_list:
                session.merge(addr_obj, load=True)
                straddrs_list.append(addr_obj.address)
            # session.add_all(addrs_obj_list)
            ret = session.flush()
            logger.info(f'flush ret : {ret}')

            # 更新订单状态
            session.query(AddAddressOrder) \
                .filter(AddAddressOrder.order_id == order_data.order_id) \
                .update({
                'generate_status': AddrAddressOrderGenerateStatus.SUCCESS,
                'order_complete_time': datetime.now(),
                'remark': f'{order_data.start_addr_index} to {order_data.end_addr_index}',
                'order_status': AddAddressOrderStatus.SUCCESS,
                'audit_complete_time' : audit_complete_time,
                'audit_status': AddrAddressOrderAuditStatus.PASSED   #以防万一
                # 'active_status' : AddrAddressOrderActiveStatus.YES
            })
            ret = session.flush()

            channel.basic_ack(delivery_tag=method.delivery_tag)

            #写入到redis中
            rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_ADDRESS_POOL_DB_NAME, decode_responses=True)
            ret = rds.sadd(REDIS_DEPOSIT_ADDRESS_POOL_NAME, *tuple(straddrs_list))
            logger.info(f'sadd ret: {ret}')

            session = MySqlSessionClass()
            session.query(AddAddressOrder) \
                .filter(AddAddressOrder.order_id == order_data.order_id) \
                .update({
                'active_status': AddrAddressOrderActiveStatus.YES
            })
            ret = session.flush()

        logger.info(f'processed order_id:{order_id} finished.')
    except Exception as e:

        if not session.is_active:
            logger.info('lost mysql connection, create new connection ')
            session = MySqlSessionClass()

        session.query(AddAddressOrder) \
            .filter(AddAddressOrder.order_id == order_id) \
            .update({
            # 'generate_status': AddrAddressOrderGenerateStatus.SUCCESS,  # order_data.generate_status
            'order_complete_time': datetime.now(),  # order_data.order_complete_time
            'remark': f'failed',
            'order_status': AddAddressOrderStatus.FAIL
        })

        # 手动回 ack
        channel.basic_ack(delivery_tag=method.delivery_tag)

        logging.error( f'callback() : error: {e}')
        traceback.print_exc()



def main():
    credentials = pika.PlainCredentials(RABBIT_MQ_USER_NAME, RABBIT_MQ_PASSWORD)
    # 创建连接
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        RABBIT_MQ_IP, RABBIT_MQ_PORT, RABBIT_MQ_VRIATUAL_HOST, credentials,
        heartbeat = RABBIT_MQ_HEARTBEAT_TIME,
        blocked_connection_timeout = RABBIT_BLOCKED_CONNECTION_TIMEOUT
    ))

    # 建立信道
    channel = connection.channel()

    assert isinstance(channel, BlockingChannel)

    # 一次只接受一条消息, 处理完了再处理下一条
    channel.basic_qos(prefetch_count=1, global_qos=True)

    channel.exchange_declare(exchange=ADDRESS_GENERATE_EXCHANGE, exchange_type=RABBIT_DIRECT_MODE)

    # 是为了防止没找到queue队列名称报错
    channel.queue_declare(queue=Q_ADDRESS_GENERATE, durable=True)
    channel.queue_bind(exchange=ADDRESS_GENERATE_EXCHANGE, queue=Q_ADDRESS_GENERATE, routing_key=ADDRESS_GENERATE_ROUTINGKEY)

    channel.basic_recover(requeue=True)

    # 接收消息
    channel.basic_consume(queue=Q_ADDRESS_GENERATE,
                          on_message_callback=callback,
                          auto_ack=False)  # 直接自动回复即可, 这里不关系结果,  因为有定时扫描
    # 开始接收
    logging.info('start consuming......')
    channel.start_consuming()



    pass


if __name__ == '__main__':

    for i in range(10):
        try:
            main()
        except Exception as e:
            logging.error(f'error------>{e}')
            time.sleep(60 * 10)
            pass