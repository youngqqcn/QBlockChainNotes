#coding:utf8
#!/usr/bin/python

#####################################################################################################
# MySQL Info ########################################################################################
#####################################################################################################
import os

SQL_IP_ADDR, SQL_PORT = '127.0.0.1',3306
SQL_USRNAME = 'root'
SQL_PASSWD = os.environ.get('SQL_PWD')
DBNAME =  'wallet'

#####################################################################################################
# Http Connection Info###############################################################################
#####################################################################################################

WALLET_API_PORT=9000

#####################################################################################################
# RPC Info###########################################################################################
#####################################################################################################
# Bitcoin Family
### BTC
BTC_IP_ADDR =  '192.168.10.199'
BTC_RPC_USERNAME = 'btc'
BTC_RPC_PASSWD = 'btc2018'
BTC_RPC_PORT = 18332
BTC_RPC_URL = "http://%s:%s@%s:%d" % (BTC_RPC_USERNAME, BTC_RPC_PASSWD,BTC_IP_ADDR,BTC_RPC_PORT)

### USDT(OMNI)
OMNI_IP_ADDR =  '192.168.10.200'
OMNI_RPC_USERNAME = 'btc'
OMNI_RPC_PASSWD = 'btc2018'
OMNI_RPC_PORT = 18332
OMNI_RPC_URL = "http://%s:%s@%s:%d" % (OMNI_RPC_USERNAME, OMNI_RPC_PASSWD,OMNI_IP_ADDR,OMNI_RPC_PORT)

# Ethereum Family
### ETH
ETH_IP_ADDR = '192.168.10.199'
ETH_RPC_PORT = 18545

#ETH_IP_ADDR = 'api.etherscan.io'
#ETH_RPC_PORT = 8545
ETH_GETBALANCE_API_URL = 'api.blockcypher.com'  #这是getBalance接口的备用方案

#USDP
USDP_IP_ADDR = '47.99.81.158'
#USDP_IP_ADDR = '192.168.10.23'
USDP_RPC_PORT = 1317


#HTDF
#HTDF_IP_ADDR = '47.88.173.14'
HTDF_IP_ADDR = '47.98.194.7'
#HTDF_IP_ADDR = '192.168.10.69'
HTDF_RPC_PORT = 1317

 
#####################################################################################################
# Ethereum###########################################################################################
#####################################################################################################
BLOCK_TAG_EARLIEST = 'earliest'
BLOCK_TAG_LATEST   = 'latest'
BLOCK_TAG_PENDING  = 'pending'
BLOCK_TAGS = (
    BLOCK_TAG_EARLIEST,
    BLOCK_TAG_LATEST,
    BLOCK_TAG_PENDING,
)
ETH_BLK_BUFFER_SIZE = 30
#####################################################################################################
# OMNI ##############################################################################################
#####################################################################################################
OMNI_PROPERTY_ID = 2 # Test: 2, Tether: 31
OMNI_TRANSACTION_FEE = '0.00006'# 0.00000257
OMNI_TRANSACTION_RECIPIENT_GAIN = 0.00000546

if __name__ == "__main__":
    pass
