#!coding:utf8

#author:yqq
#date:2020/5/27 0027 18:09
#description:

from .config import config as conf

#环境名称 (dev, sit, uat, pro)  小写的
ENV_NAME = conf.ENV_NAME

#助记词
g_MNEMONIC = conf.MNEMONIC

#是否是主网
g_IS_MAINNET = conf.IS_MAINNET

#支持的币种
g_TOKEN_NAME_LIST = ['BTC', 'HTDF', 'USDT', 'ETH', 'BTU']



############################ redis 相关 #######################
REDIS_HOST = conf.REDIS_HOST  #'192.168.10.29'
REDIS_PORT = conf.REDIS_PORT  #6379
REDIS_API_KEY_DB_NAME = 2
REDIS_ADDRESS_POOL_DB_NAME = 1
REDIS_DEPOSIT_ADDRESS_POOL_NAME =  f'deposit_address_{ENV_NAME}'
###############################################################


################## HTDF 全节点相关 ############################
HTDF_NODE_RPC_HOST = conf.HTDF_NODE_HOST   #'123.56.71.141'
HTDF_NODE_RPC_PORT= conf.HTDF_NODE_PORT  #1317
HTDF_RPC_HOST = f'{HTDF_NODE_RPC_HOST}:{HTDF_NODE_RPC_PORT}'
HTDF_GAS_LIMIT= 30000  #默认即可
HTDF_GAS_PRICE =  100  #默认即可
if g_IS_MAINNET:
    HTDF_CHAINID = 'mainchain'

    HRC20_CONTRACT_MAP = {
        # 例如: "contract_addr" : { "decimal": 精度, "symbol":"AJC"  }
        "htdf1w43aazq9sjlcrwj4y7nnsck7na5zljzu4x5nrq" : { "decimal": 18, "symbol":"BTU"  },
    }


else:
    HTDF_CHAINID = 'testchain'

    HRC20_CONTRACT_MAP = {
        # 例如: "contract_addr" : { "decimal": 精度, "symbol":"AJC"  }
        "htdf1vw4dq4teurls7yg8254pz5esn0gpg0492yvt95": {"decimal": 18, "symbol": "BTU"},
    }

###############################################################




########################### 数据库相关 #########################
MYSQL_DB_NAME = f'pg_database_{ENV_NAME}'
MYSQL_HOST = conf.MYSQL_HOST  #'192.168.10.29'
MYSQL_PORT = conf.MYSQL_PORT #3306
MYSQL_USERNAME = conf.MYSQL_USERNAME  #'root'
MYSQL_PWD = conf.MYSQL_PWD  #'eWFuZ3FpbmdxaW5n'
MYSQL_CONNECT_INFO = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PWD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB_NAME}"

###############################################################


################## ETH 全节点相关 #############################

ETH_ERC20_GAS_PRICE = 65    #Gwei
ERC20_GAS_LIMIT = 70000
ETH_FULL_NODE_HOST = conf.ETH_FULL_NODE_HOST
ETH_FULL_NODE_PORT = conf.ETH_FULL_NODE_PORT
#'http://192.168.10.199:28545'  #ropsten
ETH_FULL_NODE_RPC_URL = 'http://{}:{}'.format(ETH_FULL_NODE_HOST, ETH_FULL_NODE_PORT)


if g_IS_MAINNET:
    ETH_CHAIN_ID = 1   #1:mainnet, 3: ropsten 4: rinkeby
    ERC20_USDT_CONTRACT_ADDRESS = '0xdac17f958d2ee523a2206206994597c13d831ec7' #主网USDT
else:
    ETH_CHAIN_ID = 3   #1:mainnet, 3: ropsten 4: rinkeby
    ERC20_USDT_CONTRACT_ADDRESS = '0x1f2648f4437edf90240810e30aa561e1a8b2b802' #ropsten的测试
    #ERC20_USDT_CONTRACT_ADDRESS = '0xEca059F3d6De135E520E789CDfEeCBf5CECa3770' #rinkeby的测试

###################################################################


ETH_BLOCK_TO_WAIT_FOR_CONFIRM = 11
HTDF_BLOCK_TO_WAIT_FOR_CONFIRM = 0
ERC20_TRANSFER_EVENT_HASH = 'ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
ERC20_CONTRACTS_LIST = [
    ERC20_USDT_CONTRACT_ADDRESS,  # ERC20-USDT test
]


###################### BTC 相关 ##################
BTC_API_HOST = conf.BTC_NODE_API_HOST
BTC_API_PORT = conf.BTC_NODE_API_PORT