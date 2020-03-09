## 参考

- 官方API文档:  <https://developers.tron.network/reference>
- C++ <https://github.com/aUscCoder/TronWallet>
- 



## TRON资源模型

>  参考: https://tronprotocol.github.io/documentation-zh/mechanism&algorithm/resource/



- 如果是转账, 目标账户不存在，包括普通转账或发行Token转账，转账操作则会创建账户并转账，只会扣除创建账户消耗的Bandwidth Points，转账**不会**再消耗额外的Bandwidth Points。

- 如果交易需要创建新账户，Bandwidth Points消耗如下：

  - 尝试消耗交易发起者冻结获取的Bandwidth Points。如果交易发起者Bandwidth Points不足，则进入下一步

  - 尝试消耗交易发起者的TRX，这部分烧掉0.1TRX

    > 例如: <https://tronscan.org/#/transaction/f80dacb7b73219b86b45225dc58d7d5337a576ea190899dda5e5ebd3e5de9da5>

- 如果交易是Token转账，Bandwidth Points消耗如下：

  -  依次验证 发行Token资产总的免费Bandwidth Points是否足够消耗，转账发起者的Token剩余免费Bandwidth Points是否足够消耗，Token发行者冻结TRX获取Bandwidth Points剩余量是否足够消耗。如果满足则扣除Token发行者的Bandwidth Points，任意一个不满足则进入下一步

  - 尝试消耗交易发起者冻结获取的Bandwidth Points。如果交易发起者Bandwidth Points不足，则进入下一步

  - 尝试消耗交易发起者的免费Bandwidth Points。如果免费Bandwidth Points也不足，则进入下一步

  - 尝试消耗交易发起者的TRX，交易的字节数 * 10 sun

- 如果交易普通交易，Bandwidth Points消耗如下：

  - 尝试消耗交易发起者冻结获取的Bandwidth Points。如果交易发起者Bandwidth Points不足，则进入下一步

  - 尝试消耗交易发起者的免费Bandwidth Points。如果免费Bandwidth Points也不足，则进入下一步

  - 尝试消耗交易发起者的TRX，交易的字节数 * 10 sun

- 用户的带宽在24小时内恢复, 恢复过程是线性的.(具体公式在官方文档中) 



## TRON 充币技术实现方案



- 获取交易信息:<https://developers.tron.network/reference#transaction-information-by-account-address>

  ```
  curl --request GET \
    --url https://api.trongrid.io/v1/accounts/TPcUx2iwjomVzmX3CHDDYmnEPJFTVeyqqS/transactions
  
  ```




- 获取trc20交易信息: <https://developers.tron.network/reference#trc20-transaction-information-by-account-address>

  ```
  curl --request GET \
    --url https://api.trongrid.io/v1/accounts/TPcUx2iwjomVzmX3CHDDYmnEPJFTVeyqqS/transactions/trc20
  ```

  
  
  
  
- 其他交易费
  
  | 交易类型              | 费用     |
  | --------------------- | -------- |
  | 创建witness(观察节点) | 9999 TRX |
  | 发行token             | 1024 TRX |
  | 创建account           | 0.1 TRX  |
  | 创建exchange          | 1024 TRX |





### 普通TRX交易

`curl -X POST  https://api.trongrid.io/wallet/getblockbynum -d '{"num":14455630}'`



```
{
            "ret": [
                {
                    "contractRet": "SUCCESS"
                }
            ],
            "signature": [
                "16658b4d004737334df951cf8728e03108d3cc2a6ebcad306fb7a4e2984c02fa4bd1ad1664fe4768c36c585171d21207a1fcd8080a075f8b472585f8eaf6a53501"
            ],
            "txID": "f80dacb7b73219b86b45225dc58d7d5337a576ea190899dda5e5ebd3e5de9da5",
            "raw_data": {
                "contract": [
                    {
                        "parameter": {
                            "value": {
                                "amount": 997000000,  
                                "owner_address": "418a4a39b0e62a091608e9631ffd19427d2d338dbd",
                                "to_address": "4195a6569bdccc1bee832803b4116a020950818cba"
                            },
                            "type_url": "type.googleapis.com/protocol.TransferContract"
                        },
                        "type": "TransferContract"
                    }
                ],
                "ref_block_bytes": "933a",
                "ref_block_hash": "ad8de998be3a5ebc",
                "expiration": 1573700973000,
                "timestamp": 1573611260215
            },
            "raw_data_hex": "0a02933a2208ad8de998be3a5ebc40c8e38cbfe62d5a69080112650a2d747970652e676f6f676c65617069732e636f6d2f70726f746f636f6c2e5472616e73666572436f6e747261637412340a15418a4a39b0e62a091608e9631ffd19427d2d338dbd12154195a6569bdccc1bee832803b4116a020950818cba18c086b4db0370b792a994e62d"
        },
```



其中

```
"value": {
 	"amount": 997000000,  //转账金额,  即 997 TRX
 	
 	"owner_address": "418a4a39b0e62a091608e9631ffd19427d2d338dbd",   
 	                                 //发送地址, 即 TNaRAoLUyYEV2uF7GUrzSjRQTU8v5ZJ5VR
 	                                 
	"to_address": "4195a6569bdccc1bee832803b4116a020950818cba"   
	                                 //接收地址, 即 TPcUx2iwjomVzmX3CHDDYmnEPJFTVeyqqS
}
                         
```







### TRC20交易

同ERC20交易类似



TRC20交易

```
{
            "ret": [
                {
                    "contractRet": "SUCCESS"
                }
            ],
            "signature": [
                "2e0918c8b5c74f9f35f94d03044544f6acd2470024ec7d59f2019c91241a489569901812a789fb10a196f37984b374fe3253807cf1c6b3042f1bac6356bf86ad00"
            ],
            "txID": "7f88b3cae8b2721a2c124bed0af27d7c9f60fad51672756819732779a70a22a0",
            "raw_data": {
                "contract": [
                    {
                        "parameter": {
                            "value": {
                                "data": "a9059cbb0000000000000000000000008a4a39b0e62a091608e9631ffd19427d2d338dbd000000000000000000000000000000000000000000000000000000186d0d8e20",
                                "owner_address": "4136f75d3494f0093d412102853d29b3768735159e",
                                "contract_address": "41a614f803b6fd780986a42c78ec9c7f77e6ded13c"
                            },
                            "type_url": "type.googleapis.com/protocol.TriggerSmartContract"
                        },
                        "type": "TriggerSmartContract"
                    }
                ],
                "ref_block_bytes": "c710",
                "ref_block_hash": "138c16f4dc833693",
                "expiration": 1582009386000,
                "fee_limit": 10000000,
                "timestamp": 1581918923005
            },
```



其中的  `data`的组成和 ERC20转账完全一样

```
函数签名(4字节) + 接受者地址(32字节)  + 金额(32字节)
```

例如上面TRC20-USDT转账

```
a9059cbb   函数签名  即  transfer(address _to, uint256 _value)
0000000000000000000000008a4a39b0e62a091608e9631ffd19427d2d338dbd   #接受者地址
000000000000000000000000000000000000000000000000000000186d0d8e20   #金额
```



其中TRC20的接受者地址是不带`41`的十六进制字符串格式, 即和ETH地址完全一样,  所以, 在转换为 Base58格式的地址形式时需要加上`41`的前缀.





### TRON地址生成

python3源码

```python
#!coding:utf8

#author:yqq
#date:2019/11/12 0004 14:35
#description:  TRON地址生成算法
#参考: https://github.com/iexbase/tron-api-python/blob/master/tronapi/common/account.py

import hashlib
import ecdsa
import os
import sha3


#2019-11-12 根据官方定义修改  有限域
# http://www.secg.org/sec2-v2.pdf#page=9&zoom=100,0,249
# 关于 有限域的定义 请参考
# 0xEFFFFFC2F = 2**32 - 2**9 - 2**8 - 2**7 - 2**6 - 2**4 - 1
g_nFactor = 0xEFFFFFC2F + 0x23492397 #增值自定义
g_nMaxPrivKey = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364140 - g_nFactor #私钥最大值 (差值是自定义的)
g_nMinPrivKey = 0x0000000000000000000000000000000000000000000000000000000000000001 + g_nFactor #私钥最小值 (增值是自定义的)


def GenPrivKey():
    '''
    生成私钥, 使用 os.urandom (底层使用了操作系统的随机函数接口, 取决于CPU的性能,各种的硬件的数据指标)
    :return:私钥(16进制编码)
    '''

    #2019-05-15 添加私钥范围限制
    while True:
        privKey = os.urandom(32).encode('hex')    #生成 256位 私钥
        if  g_nMinPrivKey < int(privKey, 16) <   g_nMaxPrivKey:
            return privKey



g_b58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def Base58encode(n):
    '''
    base58编码
    :param n: 需要编码的数
    :return: 编码后的
    '''
    result = ''
    while n > 0:
        result = g_b58[n % 58] + result
        n /= 58
    return result


def Base256decode(s):
    '''
    base256编码
    :param s:
    :return:
    '''
    result = 0
    for c in s:
        result = result * 256 + ord(c)
    return result


def CountLeadingChars(s, ch):
    '''
    计算一个字符串开头的字符的次数
    比如:  CountLeadingChars('000001234', '0')  结果是5
    :param s:字符串
    :param ch:字符
    :return:次数
    '''
    count = 0
    for c in s:
        if c == ch:
            count += 1
        else:
            break
    return count


def Base58CheckEncode(version, payload):
    '''

    :param version: 版本前缀  , 用于区分主网 和 测试网络
    :param payload:
    :return:
    '''
    s = chr(version) + payload
    checksum = hashlib.sha256(hashlib.sha256(s).digest()).digest()[0:4]  #两次sha256, 区前4字节作为校验和
    result = s + checksum
    leadingZeros = CountLeadingChars(result, '\0')
    return '1' * leadingZeros + Base58encode(Base256decode(result))


def PrivKeyToPubKey(privKey):
    '''
    私钥-->公钥
    :param privKey: 共65个字节:  0x04   +  x的坐标  +   y的坐标
    :return:
    '''
    sk = ecdsa.SigningKey.from_string(privKey.decode('hex'), curve=ecdsa.SECP256k1)
    # vk = sk.verifying_key
    return ('\04' + sk.verifying_key.to_string()).encode('hex')


def PubKeyToAddr(pubKey, isTestnet = False):
    '''
    公钥 --> 地址
    :param pubKey: 公钥
    :param isTestnet:  是否是地址
    :return:  地址字符串
    '''

    addr1 = sha3.keccak_256(pubKey.decode('hex')[1:]).digest()

    addr2 = addr1[11 + 1: ]


    #不区分主网测试网
    # if isTestnet:
    #     return Base58CheckEncode(0xA0, addr2)  #test
    return Base58CheckEncode(0x41, addr2)  #main


def GenAddr(isTestnet=False):
    '''
    此函数用于C++调用,
    :param isTestnet: 是否是测试网络
    :return:  (私钥, 公钥, 地址)
    '''
    privKey = GenPrivKey()
    # print("privkey : " + privKey)
    # print("privkey WIF:" + PrivKeyToWIF(privKey, isTestnet))
    pubKey = PrivKeyToPubKey(privKey)
    # print("pubkey : " + pubKey)
    addr = PubKeyToAddr(pubKey, isTestnet)
    # print("addr : " + addr)
    return str(privKey), str(pubKey), str(addr)



def GenMultiAddr(nAddrCount = 1, isTestnet=True):
    '''
    生成多个地址
    :param nAddrCount:
    :param isTestnet:
    :return:
    '''
    # return [("1111", "2222", "3333"), ("4444", "55555", "66666")]
    # return [1, 2, 3, 4]
    # return ["1111", "2222", "3333", "4444"]

    lstRet = []
    for i in range(nAddrCount):
        lstRet.append(GenAddr(isTestnet))
    return lstRet

#
# def main2():
#
#     # addrs =  GenMultiAddr(10, False)
#     # print(addrs)
#
#     pass
#
#
# if __name__ == '__main__':
#
#     # main()
#     main2()


```



## TRON交易离线签名



- 步骤一:  使用接口创建交易, https://developers.tron.network/reference#walletcreatetransaction

- 步骤二: 修改 `expiration`  ,  `raw_data_hex`, `txid`

- 步骤三:  对`txid` 进行  secp256k1 签名,  `signature`字段为签名的 `r`, `s`, `i`(称为`v`) , 其中  `i = i + 27`, 具体请参考 ETH的签名

  

签名demo

```python

#!coding:utf8

#author:yqq
#date:2020/3/4 0004 10:23
#description:


import logging
from pprint import pprint
import hashlib
from binascii import hexlify, unhexlify
from time import sleep
import coincurve

# TRX  python sdk
from tronapi import Tron
from tronapi.trx import  Trx

def safe_ord(value):
    if isinstance(value, int):
        return value
    else:
        return ord(value)

def new_ecsign(rawhash, key):
    if coincurve and hasattr(coincurve, 'PrivateKey'):
        pk = coincurve.PrivateKey(key)
        signature = pk.sign_recoverable(rawhash, hasher=None)
        v = safe_ord(signature[64]) + 27
        r = signature[0:32]
        s = signature[32:64]

        sig = r + s + unhexlify(hex(v)[2:])

        return sig

    

def my_encode_int64( num : int ) -> str:
    """
    将一个整数编码为 protobuf 编码格式的 十六进制字符串
    """

    # num = 1583290890000

    assert  num > 0

    #原码字符
    raw = bin(num)[2:]
    print(f"原码: {raw}")


    #补码, 因为只处理正数, 所以 补码和原码相同
    complement = raw
    print(f'补码: {complement}')


    #如果长度不是7的倍数, 则补0凑齐
    tmp_complement = complement
    if len(complement) % 7 != 0:
        tmp_complement = '0' * (7 - (len(complement) % 7)) + complement


    print(f'补0后的补码: {tmp_complement}')


    #7位组 , 正序
    seven_bit_array = []
    i = len(tmp_complement) - 1
    tmp = ''
    while i >= 0:
        tmp  =   tmp_complement[i] + tmp
        if i % 7 == 0  :
            seven_bit_array.append(  tmp )
            tmp = ''
        i -= 1

    print(f'正序7位组: { seven_bit_array[::-1] }')
    print(f'反序后7位组: {seven_bit_array}')


    #加上 MSB, 标识位
    added_msb_seven_bit_array = []
    for i in range(0, len(seven_bit_array)):

        #如果是最后一个7位组, 则 MSB标识位是 0,  否则 MSB标识位是 1
        if i == len(seven_bit_array) - 1:
            added_msb_seven_bit_array.append( '0' + seven_bit_array[i] )
        else:
            added_msb_seven_bit_array.append( '1' + seven_bit_array[i] )

    print(f'加上MSB标识位的7位组: {added_msb_seven_bit_array}')


    #最终的 二进制字符串形式
    binstr = ''.join(added_msb_seven_bit_array)
    print(f'最终二进制形式:{binstr}')


    #十六进制字符串形式
    hexstr =  hex( int( binstr, 2  ) )
    print(f'十六进制字符串形式: {hexstr}')

    return hexstr[2:]
    


def main():
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger()

    full_node = 'https://api.trongrid.io'
    solidity_node = 'https://api.trongrid.io'
    event_server = 'https://api.trongrid.io'



    privkey = "这里填写你的私钥"  # this is your private key


    tron = Tron(full_node=full_node,
                solidity_node=solidity_node,
                event_server=event_server,
                private_key=privkey)


    trx = Trx(tron)


    from_addr = 'TPcUx2iwjomVzmX3CHDDYmnEPJFTVeyqqS'
    to_addr = 'TDUjsjJzQABwVv8DnLVDZ778uKQ7X5Fs7E'
    options = {
        'from' : from_addr
    }

    amount = float(0.123)

    # receipt = trx.send_transaction( to=to_addr, amount=amount, options=options )


    #构造交易
    tx = trx.tron.transaction_builder.send_transaction(
        to_addr,
        amount,
        options['from']
    )



    if  False:
        sign = trx.sign(tx)

        sleep(61)  # 休眠 61秒  广播时报错:  {'code': 'TRANSACTION_EXPIRATION_ERROR', 'message': 'transaction expired'}

        result = trx.broadcast(sign)
        pprint(result)

        return



    old_expiration_hex = my_encode_int64(tx['raw_data']['expiration'])

    #改变 raw_data.expiration,  增加一个小时
    tx['raw_data']['expiration'] +=  3600 * 1000

    new_expiration_hex = my_encode_int64(tx['raw_data']['expiration'])

    #也要改变  raw_data_hex 中相应的字段

    # tmp_hex = tx['raw_data_hex'][30:]
    # tx['raw_data_hex'] = tx['raw_data_hex'][0:30]



    raw_data_hex = str(tx['raw_data_hex'])
    index =  raw_data_hex.find(old_expiration_hex)
    logger.info( "index : {}".format( index) )

    new_raw_data_hex = raw_data_hex.replace(old_expiration_hex, new_expiration_hex)

    old_txid = hashlib.sha256( unhexlify( tx['raw_data_hex'] )).hexdigest()

    new_txid = hashlib.sha256( unhexlify( new_raw_data_hex) ).hexdigest()

    if old_txid == tx['txID'] :
        logger.info('txid 比对成功!')
    else:
        logger.info('txid比对失败!')

    tx['txID'] = new_txid


    sign = trx.sign(tx)


    my_sig = new_ecsign( unhexlify( new_txid), unhexlify( privkey) )

    logger.info( type(hexlify(my_sig)) )
    logger.info( type(sign['signature'][0] ))

    logger.info( "我的签名: {}".format( str(hexlify(my_sig), encoding='latin') ))

    logger.info("原始签名: {}".format( sign['signature'][0] ))

    if sign['signature'][0] == str(hexlify(my_sig), encoding='latin'):
        logger.info('签名对比成功!')
    else:
        logger.info('签名对比失败')



    sleep(61)  #休眠 61秒,  来测试修改 expiration的效果

    result = trx.broadcast(sign)
    pprint(result)

    #测试成功  txid为:  8c2b0a40812be8bcee3f92587e6824dc5a6035572cffe13707211821085ea7d3

    pass



if __name__ == '__main__':

    main()
```

