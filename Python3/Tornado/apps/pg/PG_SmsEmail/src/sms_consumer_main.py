#!/usr/bin/env python
#-*- coding:utf-8 -*-

#VersionNo: 1.0
#Author: fhh
#DateTime: 2020/5/19 10:01
#Describe:  发送短信
#Function:
#Journal:
import datetime
import hashlib
import re
import logging
import time

import pika as pika
import redis as redis
import requests
import json

from urllib.parse import quote

from src.config.constant import REDIS_HOST, REDIS_PORT, REDIS_TEL_NO_DB_NAME, STR_MANDAO_SMS_API_URL, STR_MANDAO_SMS_SN, \
     RABBIT_MQ_USER_NAME, RABBIT_MQ_PASSWORD, RABBIT_MQ_VRIATUAL_HOST, RABBIT_MQ_PORT, \
    RABBIT_MQ_IP, RABBIT_DIRECT_MODE, RABBIT_MQ_HEARTBEAT_TIME, RABBIT_BLOCKED_CONNECTION_TIMEOUT, SMS_EXCHANGE, Q_SMS, \
    SMS_ROUTINGKEY, STR_MANDAO_SMS_PWD


def callback(channel, method, properties, body):
    """
    on_message_callback(channel, method, properties, body), where
                channel: pika.Channel
                method: pika.spec.Basic.Deliver
                properties: pika.spec.BasicProperties
                body: bytes
    """

    logging.info(body)
    try:
        rst = json.loads(body)
        connect = rst["msg_content"]
        tel_no = rst["tel_no"]
        send_rst = SendSms(tel_no, connect)
        if send_rst != True:
            raise  Exception("Failed to send")
        pass

    except Exception as e:
        logging.error(e)



def SendSms(telno:str, strcontent:str):
    """
    短信发送
    :param telno:   手机号
    :param strcontent:  内容
    :return: bool
    """
    #手机号格式是否正确
    try:
        mobile = telno
        # for i in mobile:
        if len(mobile) != 11:
            raise Exception("Phone length must be 11 digits")


        mobile_regex = r'^1[34578]\d{9}$'
        p = re.compile(mobile_regex)
        if not p.match(mobile):
            raise Exception('Phone length or format error')

        #短信内容长度问题
        if len(strcontent) > 600 and strcontent is None:
            raise Exception("SMS format is not qualified")

        #判断手机号是否 发送频繁
        rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_TEL_NO_DB_NAME, decode_responses=True)
        is_mobile = rds.get(mobile)
        if is_mobile:
            raise Exception("Send frequently")

        uri_ecoded_content = quote(strcontent.encode('gbk'))

        #拼装参数
        STR_MANDAO_SMS_KEY = STR_MANDAO_SMS_SN + STR_MANDAO_SMS_PWD
        STR_MANDAO_SMS_RSTPWD = hashlib.md5(STR_MANDAO_SMS_KEY.encode(encoding='iso-8859-1')).hexdigest()
        STR_MANDAO_SMS_RSTPWD = STR_MANDAO_SMS_RSTPWD.upper()

        strrequrl = STR_MANDAO_SMS_API_URL
        strrequrl += "sn=" + STR_MANDAO_SMS_SN
        strrequrl += "&pwd=" + STR_MANDAO_SMS_RSTPWD
        strrequrl += "&content=" + uri_ecoded_content
        strrequrl += "&mobile=" + mobile
        strrequrl += "&ext=2&rrid=&stime="

        #调用接口

        logging.info(f'request url: {strrequrl}')
        rsp = requests.get(strrequrl)
        logging.info(f'request rst:{rsp.status_code} : {rsp.text}')

        if rsp.status_code != 200:
            raise Exception("send fail")

        assert rsp.text is not None , 'text is none'
        rst = re.findall('<string xmlns="http://tempuri.org/">(.*?)</string>', rsp.text)

        assert isinstance(rst, list), f'rst is not list : {rst}'
        assert len(rst) >= 1, f'rst length is less than 1'
        ret_no = rst[0]
        assert  str(ret_no).isnumeric(),  f'ret_no is not numeric: {ret_no}'

        logging.info(f'{rsp.text}')
        rds.set(mobile, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        rds.expire(mobile, 15*60)
        logging.info(f'mobile save as redis')
        return True

        #成功失败处理
    except Exception as e:
        logging.error(e)
        return False


def init_mq_connect():
    """
    MQ连接
    """

    #  初始化 消息队列

    try:
        credentials = pika.PlainCredentials(RABBIT_MQ_USER_NAME, RABBIT_MQ_PASSWORD)

        connection = pika.BlockingConnection(pika.ConnectionParameters(
            RABBIT_MQ_IP, RABBIT_MQ_PORT, RABBIT_MQ_VRIATUAL_HOST, credentials,
            heartbeat = RABBIT_MQ_HEARTBEAT_TIME,
                    blocked_connection_timeout = RABBIT_BLOCKED_CONNECTION_TIMEOUT))

        if connection.is_closed:
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                RABBIT_MQ_IP, RABBIT_MQ_PORT, RABBIT_MQ_VRIATUAL_HOST, credentials))

        channel = connection.channel()

        # 同一时间, 只接受一条消息
        channel.basic_qos(prefetch_count=1, global_qos=True)

        # 是为了防止没找到queue队列名称报错
        channel.exchange_declare(exchange=SMS_EXCHANGE, exchange_type=RABBIT_DIRECT_MODE)
        channel.queue_declare(queue=Q_SMS, durable=True)

        # 将队列绑定到交换机,并设置 routing key
        channel.queue_bind(exchange=SMS_EXCHANGE, queue=Q_SMS,
                                routing_key=SMS_ROUTINGKEY)

        # 设置绑定队列,设置回调函数
        channel.basic_consume(queue=Q_SMS,
                                   on_message_callback=callback,  # 调用父类的方法,
                                   auto_ack=True)  # 如果接收消息，机器宕机消息就丢了
        channel.start_consuming()
    except Exception as e:
        logging.error(e)
        time.sleep(30)
    pass

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s | %(levelname)s | %(filename)s |%(funcName)s:%(lineno)d] %(message)s')

    #防止挂掉
    while True:
        init_mq_connect()
        time.sleep(30)

