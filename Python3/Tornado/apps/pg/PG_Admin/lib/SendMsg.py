# #!/usr/bin/env python
# #-*- coding:utf-8 -*-
#
# #VersionNo: 1.0
# #Author: fhh
# #DateTime: 2020/5/19 14:47
# #Describe:  MQ发送信息
# #Function:
# #Journal:
#
# import pika
# import json
# import logging
#
#
# RABBIT_MQ_USER_NAME = 'admin'
# RABBIT_MQ_PASSWORD = '123456'
# RABBIT_MQ_IP = '192.168.10.29'
# RABBIT_MQ_PORT = 5672
# RABBIT_MQ_VRIATUAL_HOST = 'sms'
# STR_SMS_EXCHANGE = 'q_sms_email_exchange'
# RABBIT_DIRECT_MODE = 'direct'
# STR_SMS_ROUTING_KEY = 'sms'
# STR_SMS_QUEUE = 'q_sms_queue'
#
# STR_EMAIL_EXCHANGE = 'q_sms_email_exchange'
# STR_EMAIL_ROUTING_KEY = 'email'
# STR_EMAIL_QUEUE = 'q_email_queue'
#
#
# credentials = pika.PlainCredentials(RABBIT_MQ_USER_NAME,RABBIT_MQ_PASSWORD)
# #创建连接
# connection = pika.BlockingConnection(pika.ConnectionParameters(
#     RABBIT_MQ_IP,RABBIT_MQ_PORT,RABBIT_MQ_VRIATUAL_HOST,credentials))
#
# #建立信道
#
# def SendSms(Tmsg):
#     """
#     发送短信
#     :param Tmsg:  json
#     :return:  none
#     """
#     if connection.is_closed:
#         channel = pika.BlockingConnection(pika.ConnectionParameters(
#             RABBIT_MQ_IP, RABBIT_MQ_PORT, RABBIT_MQ_VRIATUAL_HOST, credentials)).channel()
#     else:
#         channel = connection.channel()
#     channel.exchange_declare(STR_SMS_EXCHANGE, RABBIT_DIRECT_MODE)#
#     # 声明queue
#     #创建一个新队列balance，设置durable=True 队列持久化，注意不要跟已存在的队列重名，否则有报错
#     channel.queue_declare(queue=STR_SMS_QUEUE, durable=True)
#
#     #绑定队列与交换器
#     channel.queue_bind(exchange=STR_SMS_EXCHANGE, queue=STR_SMS_QUEUE, routing_key=STR_SMS_ROUTING_KEY)
#
#     #发送消息
#     # n RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange.
#     channel.basic_publish(exchange=STR_SMS_EXCHANGE,
#                               routing_key=STR_SMS_ROUTING_KEY,
#                               body= f'{json.dumps(Tmsg)}',
#                               properties=pika.BasicProperties(
#                                   delivery_mode=2,  # 使消息或任务也持久化存储
#                                   )
#                                )
#     logging.info("ok")
#
# def SendEmail(Emsg):
#     """
#     发送邮件
#     :param Emsg:  json
#     :return:  none
#     """
#
#     if connection.is_closed:
#         channel = pika.BlockingConnection(pika.ConnectionParameters(
#             RABBIT_MQ_IP, RABBIT_MQ_PORT, RABBIT_MQ_VRIATUAL_HOST, credentials)).channel()
#     else:
#         channel = connection.channel()
#     channel.exchange_declare(STR_EMAIL_EXCHANGE, RABBIT_DIRECT_MODE)  #
#     # 声明queue
#     # 创建一个新队列balance，设置durable=True 队列持久化，注意不要跟已存在的队列重名，否则有报错
#     channel.queue_declare(queue=STR_EMAIL_QUEUE, durable=True)
#
#     # 绑定队列与交换器
#     channel.queue_bind(exchange=STR_EMAIL_EXCHANGE, queue=STR_EMAIL_QUEUE, routing_key=STR_EMAIL_ROUTING_KEY)
#
#     # 发送消息
#     # n RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange.
#     channel.basic_publish(exchange=STR_EMAIL_EXCHANGE,
#                           routing_key=STR_EMAIL_ROUTING_KEY,
#                           body=f'{json.dumps(Emsg)}',
#                           properties=pika.BasicProperties(
#                               delivery_mode=2,  # 使消息或任务也持久化存储
#                           )
#                           )
#     logging.info("ok")
#
#
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
