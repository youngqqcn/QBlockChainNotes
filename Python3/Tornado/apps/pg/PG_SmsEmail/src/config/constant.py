#!/usr/bin/env python
#-*- coding:utf-8 -*-

from .config import config as conf

#环境名称 (dev, sit, uat, pro)  小写的
ENV_NAME = conf.ENV_NAME


STR_MANDAO_SMS_API_URL = conf.SMS_API_URL
STR_MANDAO_SMS_SN = conf.SMS_SN
STR_MANDAO_SMS_PWD = conf.SMS_PWD



################### MQ 相关 #################################
RABBIT_MQ_IP = conf.RABBIT_MQ_HOST
RABBIT_MQ_PORT = conf.RABBIT_MQ_PORT
RABBIT_MQ_USER_NAME = conf.RABBIT_MQ_USER_NAME
RABBIT_MQ_PASSWORD = conf.RABBIT_MQ_PASSWORD

# mq 的心跳超时时间, 10分钟之内, client一直没有回心跳, sever就连接
RABBIT_MQ_HEARTBEAT_TIME= 60 * 10
RABBIT_BLOCKED_CONNECTION_TIMEOUT = 60*50

RABBIT_MQ_VRIATUAL_HOST = ENV_NAME  #小写
RABBIT_DIRECT_MODE = 'direct'
RABBIT_DELIVERY_MODE = 2


SMS_EXCHANGE = 'sms_exchange'
SMS_ROUTINGKEY = 'sms'
Q_SMS = 'q_sms'

##########################################################

############################ redis 相关 #######################
REDIS_HOST = conf.REDIS_HOST
REDIS_PORT = conf.REDIS_PORT
REDIS_API_KEY_DB_NAME = 2

REDIS_TEL_NO_DB_NAME = 3

###############################################################