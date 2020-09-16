#!coding:utf8

#author:fhh
#date:2020/5/7
#description:
#  1) 定时从数据库中获取未确认(未打包)的交易, 通过txid查询交易是否被打包
#  2) 接收 MQ发来的监控消息
import time

import pika
import requests
import json
import logging

from pika.adapters.blocking_connection import BlockingChannel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.constant import RABBIT_MQ_USER_NAME, RABBIT_MQ_PASSWORD, RABBIT_MQ_IP, RABBIT_MQ_PORT, \
    RABBIT_MQ_VRIATUAL_HOST, MONITOR_EXCHANGE, Q_TX_MONITOR, RABBIT_DIRECT_MODE, MONITOR_ROUTINGKEY, MYSQL_CONNECT_INFO
from src.lib.exceptions import MqBodyException
from src.monitor.comman import handler

logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s | %(filename)s:%(funcName)s:%(lineno)d | %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

engine = create_engine(MYSQL_CONNECT_INFO,
                       pool_size=5, pool_pre_ping=True, pool_recycle=120)

SessionCls = sessionmaker(bind=engine,
                          autoflush=False,   #关于 autoflush https://www.jianshu.com/p/b219c3dd4d1e
                          autocommit=True# 自动提交
                          )
session = SessionCls()

# withdraw_body_schema = {
#     'serial_id' : And(str, lambda item: 21 == len(item) and str(item).isnumeric(),
#                           error='`serial_id` is invalid '),# 支付网关生成的唯一流水号
#     'tx_hash'   : And(str, lambda item: 64 == len(item),
#                           error='`tx_hash` is invalid '),# tx_hash
#     'token_name': And(str, lambda item: item in 'HTDF', error='`token_name` is invalid'),
#     }





def callback(channel, method, properties, body):
    try:
        logging.info("获取进来的值{}".format(body))
        msg_data = json.loads(body, encoding='utf8')
        if not isinstance(msg_data, dict) or 'serial_id' not in msg_data:
            raise MqBodyException("MQ body format error")

        handler( session, msg_data['serial_id'], logger)

    except Exception as e:
        logging.error( f'callback() : error: {e}')





def main():
    credentials = pika.PlainCredentials(RABBIT_MQ_USER_NAME, RABBIT_MQ_PASSWORD)
    # 创建连接
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        RABBIT_MQ_IP, RABBIT_MQ_PORT, RABBIT_MQ_VRIATUAL_HOST , credentials))

    # 建立信道
    channel = connection.channel()

    assert isinstance(channel, BlockingChannel)

    #一次只接受一条消息, 处理完了再处理下一条
    channel.basic_qos(prefetch_count=1, global_qos=True)

    channel.exchange_declare(exchange=MONITOR_EXCHANGE, exchange_type=RABBIT_DIRECT_MODE)

    # 是为了防止没找到queue队列名称报错
    channel.queue_declare(queue=Q_TX_MONITOR, durable=True)
    channel.queue_bind(exchange=MONITOR_EXCHANGE, queue=Q_TX_MONITOR, routing_key=MONITOR_ROUTINGKEY)


    channel.basic_recover(requeue=True)

    # 接收消息
    channel.basic_consume(queue=Q_TX_MONITOR,
                          on_message_callback=callback,
                          auto_ack=True)  # 直接自动回复即可, 这里不关系结果,  因为有定时扫描
    # 开始接收
    logging.info('start consuming......')
    channel.start_consuming()



if __name__ == '__main__':

    while True:
        try:
            main()
        except Exception as e:
            logger.error(f'main() ERROR:{e}')
            time.sleep(10)

    pass

