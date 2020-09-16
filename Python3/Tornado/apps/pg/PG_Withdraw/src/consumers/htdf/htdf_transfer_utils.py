#!coding:utf8

#author:yqq
#date:2020/5/11 0011 14:48
#description:

import json
import hashlib
import coincurve
import base64
from binascii import  hexlify, unhexlify
import requests
import logging
import time

from src.config.constant import WithdrawStatus, g_IS_MAINNET, HTDF_CHAINID, HTDF_RPC_HOST, HTDF_GAS_PRICE, \
    HTDF_GAS_LIMIT
from src.consumers.consumer_base import TransferFuncResponse
from src.consumers.htdf.my_bech32 import MakeHRC20TransferHexData
from src.lib.addr_gen.htdf_addr_gen import PrivKeyToPubKeyCompress
from src.lib.exceptions import TxBroadcastFailedException, \
    InvalidParametersException, BalanceNotEnoughException, HttpConnectionError

HRC20_GASLIMIT = 200000  #默认即可
HRC20_GASPRICE =  100  #默认即可

def ecsign(rawhash, key):
    if coincurve and hasattr(coincurve, 'PrivateKey'):
        pk = coincurve.PrivateKey(key)
        signature = pk.sign_recoverable(rawhash, hasher=None)
        # v = safe_ord(signature[64]) + 27
        r = signature[0:32]
        s = signature[32:64]
        return r, s



def htdf_transfer(priv_key : str, from_addr : str,
                  to_addr : str, amount_in_htdf : float,
                  memo : str) -> TransferFuncResponse :
    '''
    转账
    :param from_addr:  源地址
    :param to_addr:  目的地址
    :param amount: 金额,   TODO: 这里是浮点数,  下面处理的时候   再乘以  10^8  将单位转为  satoshi
    :return: 无
    '''

    pub_key = PrivKeyToPubKeyCompress(privKey=priv_key)


    amount = int(amount_in_htdf * (10**8))
    if amount <= 1000  and  0 < amount_in_htdf < 999999999:
        logging.error("nAmount error|nAmount=%f" % amount)
        raise InvalidParametersException("nAmount error|nAmount=%f" % amount)

    if len(memo) > 51:
        logging.error("memo is too long")
        raise InvalidParametersException("memo is too long")


    time.sleep(6)

    #获取账户账户余额
    rsp = None

    try_times = 3
    for i in range(try_times):
        try:
            url = 'http://%s/auth/accounts/%s' % (HTDF_RPC_HOST.strip(), from_addr.strip())
            logging.info(f'url:{url}')
            rsp = requests.get(url=url, timeout=10)
            break
        except Exception as e:
            logging.error(f'get htdf account info , error: {e}')
            time.sleep(3)
            if i == try_times - 1: raise HttpConnectionError('get htdf account info error')
            pass

    logging.info(f'account meg:{rsp}')
    logging.info(f'account status_code:{rsp.status_code}')
    if rsp.status_code != 200:
        logging.error(f'get account info error: {rsp.status_code}')
        raise BalanceNotEnoughException(f'get account info error: {rsp.status_code}')

    rspJson = rsp.json()
    nAccountNumber = int(rspJson['value']['account_number'], 10)
    nSequence = int(rspJson['value']['sequence'], 10)

    logging.info('account_number : %d' % nAccountNumber)
    logging.info('sequence: %d' % nSequence)


    jUnTxStr = """{\
    "account_number": "%d",\
	"chain_id": "%s",\
	"fee": {\
			"gas_price": "%d",\
			"gas_wanted": "%d"\
	},\
    "memo": "%s",\
	"msgs": [{\
		"Amount": [{\
			"amount": "%d",\
            "denom": "satoshi"\
		}],\
        "Data": "",\
        "From": "%s",\
        "GasPrice": %s,\
        "GasWanted": %s,\
		"To": "%s"\
	}],\
    "sequence": "%d"\
    }"""  % (nAccountNumber, HTDF_CHAINID, HTDF_GAS_PRICE, HTDF_GAS_LIMIT, memo,
             amount, from_addr, HTDF_GAS_PRICE , HTDF_GAS_LIMIT, to_addr , nSequence)

    jUnTxStr = jUnTxStr.replace(' ', '')
    jUnTxStr = jUnTxStr.replace('\t', '')
    jUnTxStr = jUnTxStr.replace('\n', '')
    logging.info(jUnTxStr)


    strtmp = ''
    #将json转为二进制数组
    for  i in bytearray(jUnTxStr, encoding='utf-8'):
        strtmp += ('{0}({1}),'.format(i, chr(i)))
    logging.info("json字符转为byteArray: {}".format(strtmp))

    shaData =  hashlib.sha256( bytearray(jUnTxStr, encoding='utf-8') ).digest()
    logging.info('\n-----------------------------------\n')
    logging.info("Json的sha256结果: {}".format(hexlify(shaData)))
    #hexlify把二进制转16进制
    #privKey = unhexlify( g_PrivKey )
    privKey = unhexlify( priv_key )  #设置为船机那里的私钥

    logging.info('\n--------------------------------------\n')
    # logging.info("strPrivKey:{}".format( hexlify( privKey) )) #私钥不要打印
    #签名
    r, s = ecsign(shaData,  privKey)
    logging.info('r:' +  hexlify(r).decode(encoding='utf8'))
    logging.info('s:' + hexlify(s).decode(encoding='utf8'))

    logging.info('\n--------------------------------------\n')
    b64Data = base64.b64encode(r + s).decode(encoding='utf8')
    logging.info(type(b64Data))
    logging.info(b64Data)

    logging.info('--------------------------------------')
    pubKey = pub_key   #g_PubKey  由私钥推导出公钥
    b64PubKey = base64.b64encode(unhexlify( pubKey)).decode(encoding='utf8')
    logging.info("公钥的base64编码:" + b64PubKey)


    jSigTx = """{
        "type": "auth/StdTx",
        "value":{
            "msg": [{
                "type": "htdfservice/send",  
                "value":{
                    "From": "%s",
                    "To": "%s",
                    "Amount": [{
                        "denom": "satoshi",
                        "amount": "%d"
                    }],
                    "Data": "",
                    "GasPrice": "%d",
                    "GasWanted": "%d"
                }
            }],
            "fee": {
                "gas_wanted": "%d",
                "gas_price": "%d"
            },
            "signatures": [{
                "pub_key": {
                    "type": "tendermint/PubKeySecp256k1",
                    "value": "%s"
                },
                "signature": "%s"
            }],
            "memo": "%s"
        }
    }""" %(from_addr, to_addr , amount, HTDF_GAS_PRICE, HTDF_GAS_LIMIT,
           HTDF_GAS_LIMIT, HTDF_GAS_PRICE, b64PubKey, b64Data, memo)

    jSigTxStr = jSigTx
    jSigTxStr = jSigTxStr.replace(' ', '')
    jSigTxStr = jSigTxStr.replace('\t', '')
    jSigTxStr = jSigTxStr.replace('\n', '')
    bcastData = hexlify( bytes( jSigTxStr, encoding='utf8')).decode(encoding='utf8')
    logging.info("签名的json:" + jSigTxStr)
    logging.info("签名后的交易:"+ bcastData)

    logging.info(f'broadcast Start........................')


    # 广播交易
    bcastData = {'tx' :  bcastData }
    postData = json.dumps(bcastData)



    rsp = None
    for n in range(try_times):
        try:
            url = 'http://%s/hs/broadcast' % (HTDF_RPC_HOST)
            logging.info(f'url:{url}')
            rsp = requests.post(url=url, data=postData, timeout=15)
            break
        except Exception as e:
            logging.error(f'htdf tx broadcast, error: {e}')
            time.sleep(3)
            if n == try_times - 1: raise TxBroadcastFailedException('get htdf account info error')
            pass


    ret_info = TransferFuncResponse()
    ret_info.transaction_status = WithdrawStatus.transaction_status.PENDING
    if rsp.status_code == 200:
        rspJson = rsp.json()
        if 'code' in rspJson or 'raw_log' in rspJson:
            ret_info.transaction_status = WithdrawStatus.transaction_status.FAIL
            logging.error(f'error: {rspJson}')
            raise TxBroadcastFailedException(f"broadcast error:{rsp.text}")
    else:

        #TODO: 广播失败, 可能是组装的交易有问题,  不应该直接将订单改为失败
        ret_info.transaction_status = WithdrawStatus.transaction_status.FAIL
        logging.error(' broadcast failed,  ')
        logging.error(" broadcast failed: %s --> %s amount: %d , %s" % (from_addr, to_addr, amount, rsp.text))
        raise TxBroadcastFailedException("broadcast failed")

    tx_hash = rspJson['txhash']
    logging.info("broadcast success: %s --> %s  acount: %d  , tx_hash: %s" % (from_addr, to_addr , amount, tx_hash ))

    ret_info.tx_hash =  tx_hash

    return ret_info




def hrc20_transfer(
        priv_key: str,
        from_addr : str,
        contract_addr : str,
        token_recipient : str,
        token_amount : float,
        token_decimal : int,
        memo: str) -> TransferFuncResponse:

    """
    :param priv_key: 私钥
    :param fromaddr:  源地址
    :param contract_addr:   HRC20合约地址
    :param token_recipient:  HRC20代币 接收地址
    :param token_amount:  HRC20 代币金额
    :param token_decimal:  HRC20 代币合约的 精度
    :param memo :  备注
    :return: None
    """
    pub_key = PrivKeyToPubKeyCompress(privKey=priv_key)

    try_times = 3
    # 获取账户账户信息
    rsp = None
    for i in range(try_times):
        try:
            url = 'http://%s/auth/accounts/%s' % (HTDF_RPC_HOST.strip(), from_addr.strip())
            logging.info(f'url:{url}')
            rsp = requests.get(url=url, timeout=10)
            break
        except Exception as e:
            logging.error(f'get htdf account info , error: {e}')
            time.sleep(3)
            if i == try_times - 1: raise HttpConnectionError('get htdf account info error')
            pass

    logging.info(f'account meg:{rsp}')
    logging.info(f'account status_code:{rsp.status_code}')
    if rsp.status_code != 200:
        logging.error(f'get account info error: {rsp.status_code}')
        raise BalanceNotEnoughException(f'get account info error: {rsp.status_code}')

    rspJson = rsp.json()
    nAccountNumber = int(rspJson['value']['account_number'], 10)
    nSequence = int(rspJson['value']['sequence'], 10)

    logging.info('account_number : %d' % nAccountNumber)
    logging.info('sequence: %d' % nSequence)



    contract_data = MakeHRC20TransferHexData(token_recipient, token_amount, token_decimal)
    logging.info('contract_data : {}'.format(contract_data))

    htdf_amount = 0  #默认为0即可

    jUnTxStr = """{\
    "account_number": "%d",\
	"chain_id": "%s",\
	"fee": {\
			"gas_price": "%d",\
			"gas_wanted": "%d"\
	},\
    "memo": "%s",\
	"msgs": [{\
		"Amount": [{\
			"amount": "%d",\
            "denom": "satoshi"\
		}],\
        "Data": "%s",\
        "From": "%s",\
        "GasPrice": %s,\
        "GasWanted": %s,\
		"To": "%s"\
	}],\
    "sequence": "%d"\
    }"""  % (nAccountNumber, HTDF_CHAINID, HRC20_GASPRICE, HRC20_GASLIMIT, memo,
             htdf_amount, contract_data , from_addr, HRC20_GASPRICE,
             HRC20_GASLIMIT, contract_addr , nSequence)

    # jUnTxStr = json.dumps(jUnTx , sort_keys=False)
    jUnTxStr = jUnTxStr.replace(' ', '')
    jUnTxStr = jUnTxStr.replace('\t', '')
    jUnTxStr = jUnTxStr.replace('\n', '')
    logging.info(jUnTxStr)




    strtmp = ''
    for  i in bytearray(jUnTxStr, encoding='utf-8'):
        strtmp += ('{0}({1}),'.format(i, chr(i)))
    logging.info("json字符转为byteArray: {}".format(strtmp))


    shaData =  hashlib.sha256( bytearray(jUnTxStr, encoding='utf-8') ).digest()
    logging.info('\n-----------------------------------\n')
    logging.info("Json的sha256结果: {}".format(hexlify(shaData)))
    # privKey = g_PrivKey.decode('hex')
    privKey = unhexlify( priv_key )

    logging.info('\n--------------------------------------\n')
    logging.info("strPrivKey:{}".format( hexlify( privKey) ))
    r, s = ecsign(shaData,  privKey)
    logging.info('r:' +  hexlify(r).decode(encoding='utf8'))
    logging.info('s:' + hexlify(s).decode(encoding='utf8'))

    logging.info('\n--------------------------------------\n')
    b64Data = base64.b64encode(r + s).decode(encoding='utf8')
    logging.info(type(b64Data))
    logging.info(b64Data)

    logging.info('--------------------------------------')
    pubKey = pub_key
    b64PubKey = base64.b64encode(unhexlify( pubKey)).decode(encoding='utf8')
    logging.info("公钥的base64编码:" + b64PubKey)



    #---------------------------------------------------------

    jSigTx = """{
        "type": "auth/StdTx",
        "value":{
            "msg": [{
                "type": "htdfservice/send",  
                "value":{
                    "From": "%s",
                    "To": "%s",
                    "Amount": [{
                        "denom": "satoshi",
                        "amount": "%d"
                    }],
                    "Data": "%s",
                    "GasPrice": "%d",
                    "GasWanted": "%d"
                }
            }],
            "fee": {
                "gas_wanted": "%d",
                "gas_price": "%d"
            },
            "signatures": [{
                "pub_key": {
                    "type": "tendermint/PubKeySecp256k1",
                    "value": "%s"
                },
                "signature": "%s"
            }],
            "memo": "%s"
        }
    }""" %(from_addr, contract_addr , htdf_amount, contract_data,
           HRC20_GASPRICE, HRC20_GASLIMIT, HRC20_GASLIMIT, HRC20_GASPRICE,
           b64PubKey, b64Data, memo)

    jSigTxStr = jSigTx
    jSigTxStr = jSigTxStr.replace(' ', '')
    jSigTxStr = jSigTxStr.replace('\t', '')
    jSigTxStr = jSigTxStr.replace('\n', '')
    bcastData = hexlify( bytes( jSigTxStr, encoding='utf8')).decode(encoding='utf8')
    logging.info("签名的json:" + jSigTxStr)
    logging.info("签名后的交易:"+ bcastData)



    # 广播交易
    bcastData = {'tx' :  bcastData }
    postData = json.dumps(bcastData)


    rsp = None
    for n in range(try_times):
        try:
            url = 'http://%s/hs/broadcast' % (HTDF_RPC_HOST)
            logging.info(f'url:{url}')
            rsp = requests.post(url=url, data=postData, timeout=15)
            break
        except Exception as e:
            logging.error(f'htdf tx broadcast, error: {e}')
            time.sleep(3)
            if n == try_times - 1: raise TxBroadcastFailedException('get htdf account info error')
            pass


    ret_info = TransferFuncResponse()
    ret_info.transaction_status = WithdrawStatus.transaction_status.PENDING
    if rsp.status_code == 200:
        rspJson = rsp.json()
        if 'code' in rspJson or 'raw_log' in rspJson:
            ret_info.transaction_status = WithdrawStatus.transaction_status.FAIL
            logging.error(f'error: {rspJson}')
            raise TxBroadcastFailedException(f"broadcast error:{rsp.text}")
    else:

        #TODO: 广播失败, 可能是组装的交易有问题,  不应该直接将订单改为失败
        ret_info.transaction_status = WithdrawStatus.transaction_status.FAIL
        logging.error(' broadcast failed,  ')
        logging.error(" broadcast failed: %s --> %s amount: %d , %s"
                        % (from_addr, token_recipient, token_amount, rsp.text))
        raise TxBroadcastFailedException("broadcast failed")

    tx_hash = rspJson['txhash']
    logging.info("broadcast success: %s --> %s  acount: %d  , tx_hash: %s"
                 % (from_addr, token_recipient , token_amount, tx_hash ))

    ret_info.tx_hash =  tx_hash

    return ret_info
