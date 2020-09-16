#!/usr/bin/env python
#-*- coding:utf-8 -*-

#VersionNo: 1.0
#Author: fhh
#DateTime: 2020/5/19 14:47
#Describe:  MQ发送信息
#Function:  
#Journal:

import pika
import json
import logging


from src.config.constant import RABBIT_MQ_USER_NAME, RABBIT_MQ_PASSWORD, \
    RABBIT_MQ_VRIATUAL_HOST, RABBIT_MQ_PORT, RABBIT_MQ_IP, RABBIT_DIRECT_MODE, SMS_EXCHANGE, Q_SMS, SMS_ROUTINGKEY

STR_EMAIL_EXCHANGE = 'q_sms_email_exchange'
STR_EMAIL_ROUTING_KEY = 'email'
STR_EMAIL_QUEUE = 'q_email_queue'


credentials = pika.PlainCredentials(RABBIT_MQ_USER_NAME,RABBIT_MQ_PASSWORD)
#创建连接
connection = pika.BlockingConnection(pika.ConnectionParameters(
    RABBIT_MQ_IP,RABBIT_MQ_PORT,RABBIT_MQ_VRIATUAL_HOST,credentials))

#建立信道
Tmsg = {
    "msg_content": '【shbao】 尊敬的管理员，余额预警。BTC地址BTC余额为0.1516511，请立即充值。2020-05-25 19:58:00 SIT',
    # "msg_content": "尊敬的管理员，HTDF余额不够,已经导致用提笔失败,请立即充值。",
    # 'tel_no' : "15361022029"
               'tel_no' : "18565659593"
}
Emsg = {
    "msg_content" : "【Hetbi】初，权谓吕蒙曰：“卿今当涂掌事，不可不学！”蒙辞以军中多务。权曰：“孤岂欲卿治经为博士邪！但当涉猎，见往事耳。卿言多务，孰若孤？孤常读书，自以为大有所益。”蒙乃始就学。及鲁肃过寻阳，与蒙论议，大惊曰：“卿今者才略，非复吴下阿蒙！”蒙曰：“士别三日，即更刮目相待，大兄何见事之晚乎！”肃遂拜蒙母，结友而别。",
    "email" : "1064216495@qq.com"
}

def SendSms(Tmsg):
    """
    发送短信
    :param Tmsg:  json
    :return:  none
    """
    channel = connection.channel()
    channel.exchange_declare(SMS_EXCHANGE, RABBIT_DIRECT_MODE)#
    # 声明queue
    #创建一个新队列balance，设置durable=True 队列持久化，注意不要跟已存在的队列重名，否则有报错
    channel.queue_declare(queue=Q_SMS, durable=True)

    #绑定队列与交换器
    channel.queue_bind(exchange=SMS_EXCHANGE, queue=Q_SMS, routing_key=SMS_ROUTINGKEY)

    #发送消息
    # n RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange.
    channel.basic_publish(exchange=SMS_EXCHANGE,
                              routing_key=SMS_ROUTINGKEY,
                              body= f'{json.dumps(Tmsg)}',
                              properties=pika.BasicProperties(
                                  delivery_mode=2,  # 使消息或任务也持久化存储
                                  )
                               )
    logging.info("ok")

def SendEmail(Emsg):
    """
    发送邮件
    :param Emsg:  json
    :return:  none
    """

    channel = connection.channel()
    channel.exchange_declare(STR_EMAIL_EXCHANGE, RABBIT_DIRECT_MODE)  #
    # 声明queue
    # 创建一个新队列balance，设置durable=True 队列持久化，注意不要跟已存在的队列重名，否则有报错
    channel.queue_declare(queue=STR_EMAIL_QUEUE, durable=True)

    # 绑定队列与交换器
    channel.queue_bind(exchange=STR_EMAIL_EXCHANGE, queue=STR_EMAIL_QUEUE, routing_key=STR_EMAIL_ROUTING_KEY)

    # 发送消息
    # n RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange.
    channel.basic_publish(exchange=STR_EMAIL_EXCHANGE,
                          routing_key=STR_EMAIL_ROUTING_KEY,
                          body=f'{json.dumps(Emsg)}',
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # 使消息或任务也持久化存储
                          )
                          )
    logging.info("ok")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    SendSms(Tmsg)
    # # SendEmail(Emsg)