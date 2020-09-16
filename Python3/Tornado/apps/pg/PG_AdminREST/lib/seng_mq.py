#!/usr/bin/env python
#-*- coding:utf-8 -*-

#VersionNo: 1.0
#Author: fhh
#DateTime: 2020/5/12 17:36
#Describe:  实现发送MQ
#Function:
#Journal:


import pika
import json

from PG_AdminREST.settings import RABBIT_MQ_IP,RABBIT_MQ_PORT,RABIIT_MQ_USER_NAME,RABIIT_MQ_PASSWORD,RABBIT_MQ_VRIATUAL_HOST,\
RABBIT_DELIVERY_MODE,ADDRESS_GENERATE_EXCHANGE,Q_ADDRESS_GENERATE,ADDRESS_GENERATE_ROUTINGKEY,RABBIT_MQ_HEARTBEAT_TIME,\
RABBIT_BLOCKED_CONNECTION_TIMEOUT


def send_order_id_to_msq(tx_hash_json : dict) -> None:
    '''
    发送mq队列：通知monitor_notify转账成功
    :param tx_hash:
    :return:
    '''
    print(f'send_order_msq : start')
    credentials = pika.PlainCredentials(RABIIT_MQ_USER_NAME, RABIIT_MQ_PASSWORD)
    # 创建连接
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        RABBIT_MQ_IP, RABBIT_MQ_PORT, RABBIT_MQ_VRIATUAL_HOST , credentials,
        heartbeat = RABBIT_MQ_HEARTBEAT_TIME,
        blocked_connection_timeout = RABBIT_BLOCKED_CONNECTION_TIMEOUT))

    channel = connection.channel()

    # 单条模式
    channel.exchange_declare(ADDRESS_GENERATE_EXCHANGE, 'direct')
    #创建一个新队列balance，设置durable=True 队列持久化，注意不要跟已存在的队列重名，否则有报错
    channel.queue_declare(queue=Q_ADDRESS_GENERATE, durable=True)

    #绑定队列与交换器
    channel.queue_bind(exchange=ADDRESS_GENERATE_EXCHANGE, queue=Q_ADDRESS_GENERATE, routing_key=ADDRESS_GENERATE_ROUTINGKEY)

    #发送消息
    # n RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange.
    channel.basic_publish(exchange=ADDRESS_GENERATE_EXCHANGE,
                              body= f'{json.dumps(tx_hash_json)}',
                            routing_key=ADDRESS_GENERATE_ROUTINGKEY,
                              properties=pika.BasicProperties(
                                  delivery_mode=RABBIT_DELIVERY_MODE,  # 使消息或任务也持久化存储
                                  )
                               )
    print(f'send_order_msq : end')

if __name__ == '__main__':
    send_order_id_to_msq({"test": "test"})