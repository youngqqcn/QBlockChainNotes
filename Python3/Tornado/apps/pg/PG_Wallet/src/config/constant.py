#!coding:utf8

#author:yqq
#date:2020/5/14 0014 12:50
#description: 常量


from .config import config as conf

#环境名称 (dev, sit, uat, pro)  小写的
ENV_NAME = conf.ENV_NAME

#助记词
g_MNEMONIC = conf.MNEMONIC

#是否是主网
g_IS_MAINNET = conf.IS_MAINNET

#支持的币种
# g_TOKEN_NAME_LIST = ['BTC', 'HTDF', 'USDT', 'ETH']
g_TOKEN_NAME_LIST = ['BTC', 'HTDF', 'ETH']  #仅含主币的地址, ERC20, HRC20 分配使用ETH, HTDF地址即可


################### MQ 相关 #################################
RABBIT_MQ_IP = conf.RABBIT_MQ_HOST  #'192.168.10.29'
RABBIT_MQ_PORT = conf.RABBIT_MQ_PORT   #5672
RABBIT_MQ_USER_NAME = conf.RABBIT_MQ_USER_NAME  #'admin'
RABBIT_MQ_PASSWORD = conf.RABBIT_MQ_PASSWORD   #'123456'

# mq 的心跳超时时间, 10分钟之内, client一直没有回心跳, sever就连接
RABBIT_MQ_HEARTBEAT_TIME= 60 * 10
RABBIT_BLOCKED_CONNECTION_TIMEOUT = 60*50

RABBIT_MQ_VRIATUAL_HOST = ENV_NAME  #小写
RABBIT_DIRECT_MODE = 'direct'
RABBIT_DELIVERY_MODE = 2

#
# # ENV_NAME = 'dev'
# ENV_NAME = 'sit'
# #
# RABBIT_MQ_IP = '192.168.10.29'
# RABBIT_MQ_PORT = 5672
# RABBIT_MQ_USER_NAME = 'admin'
# RABBIT_MQ_PASSWORD = '123456'
# # mq 的心跳超时时间, 10分钟之内, client一直没有回心跳, sever就连接
# RABBIT_MQ_HEARTBEAT_TIME= 60 * 30
# RABBIT_BLOCKED_CONNECTION_TIMEOUT = 60*50
#
# # RABBIT_MQ_VRIATUAL_HOST = '/'
# RABBIT_MQ_VRIATUAL_HOST = ENV_NAME
# RABBIT_DIRECT_MODE = 'direct'
# RABBIT_DELIVERY_MODE = 2


ADDRESS_GENERATE_EXCHANGE = 'address_generate_exchange'
Q_ADDRESS_GENERATE = 'q_address_generate'
ADDRESS_GENERATE_ROUTINGKEY = 'address_generate'



############################ redis 相关 #######################
REDIS_HOST = conf.REDIS_HOST  #'192.168.10.29'
REDIS_PORT = conf.REDIS_PORT  #6379
REDIS_API_KEY_DB_NAME = 2
###############################################################

REDIS_ADDRESS_POOL_DB_NAME = 1
REDIS_DEPOSIT_ADDRESS_POOL_NAME =  f'deposit_address_{ENV_NAME}'
# REDIS_HOST = '192.168.10.29'
# REDIS_PORT = 6379
# REDIS_API_KEY_DB_NAME = 2
#
# MYSQL_DB_NAME = f'pg_database_{ENV_NAME}'
# MYSQL_HOST = '192.168.10.29'
# MYSQL_PORT = 3306
# MYSQL_USERNAME = 'root'
# MYSQL_PWD = 'eWFuZ3FpbmdxaW5n'

# g_MNEMONIC = 'puzzle vanish isolate claw ugly ramp scheme sheriff asthma dream skin banana'




########################### 数据库相关 #########################
MYSQL_DB_NAME = f'pg_database_{ENV_NAME}'
MYSQL_HOST = conf.MYSQL_HOST  #'192.168.10.29'
MYSQL_PORT = conf.MYSQL_PORT #3306
MYSQL_USERNAME = conf.MYSQL_USERNAME  #'root'
MYSQL_PWD = conf.MYSQL_PWD  #'eWFuZ3FpbmdxaW5n'
MYSQL_CONNECT_INFO = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PWD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB_NAME}"

###############################################################

class AddAddressOrderStatus:
    PROCESSING = 'PROCESSING'
    SUCCESS = 'SUCCESS'
    FAIL = 'FAIL'

class AddrAddressOrderAuditStatus:
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    PASSED = "PASSED"

class AddrAddressOrderGenerateStatus:
    NOTYET = "NOTYET"
    SUCCESS = "SUCCESS"


class AddrAddressOrderActiveStatus:
    NO = 'NO'
    YES = 'YES'

