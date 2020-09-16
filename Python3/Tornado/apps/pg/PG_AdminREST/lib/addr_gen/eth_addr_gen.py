#!coding:utf8

#author:yqq
#date:2019/3/6 0006 17:00
#description:  以太坊私钥,公钥,地址生成



import ecdsa
import os
import sha3

from binascii import hexlify, unhexlify


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
        privKey = hexlify( os.urandom(32) )    #生成 256位 私钥
        if  g_nMinPrivKey < int(privKey, 16) <   g_nMaxPrivKey:
            return privKey



def gen_addr_from_privkey(priv_key : str) -> str:
    """
    根据私钥生成地址
    :param priv_key:
    :return: 地址
    """
    sk = ecdsa.SigningKey.from_string( unhexlify( priv_key ), curve=ecdsa.SECP256k1) #通过私钥生成密钥对
    pubKey = hexlify(sk.verifying_key.to_string())   #获取公钥
    keccak = sha3.keccak_256()  # keccak_256哈希运算
    keccak.update(unhexlify(pubKey))
    address = "0x" + keccak.hexdigest()[24:]  # 截取后面40字符
    return address

    pass


def GenEthAddr():

    # privKey = GenPrivKey() #os.urandom(32).encode('hex')
    privKey = '562ab29e70ba373fad8a77627dfe1be4dde70f882cf1aefc113ed159bfe938f5'
    address = gen_addr_from_privkey(priv_key=privKey)
    print(address)

    # sk = ecdsa.SigningKey.from_string(privKey.decode('hex'), curve=ecdsa.SECP256k1)
    sk = ecdsa.SigningKey.from_string( unhexlify( privKey), curve=ecdsa.SECP256k1) #通过私钥生成密钥对
    pubKey = hexlify(sk.verifying_key.to_string())   #获取公钥

    keccak = sha3.keccak_256()   # keccak_256哈希运算
    keccak.update(  unhexlify( pubKey) )
    addr = "0x" + keccak.hexdigest()[24:]  #截取后面40字符

    # print(privKey)
    # print(pubKey)
    # print(addr)

    return (str(privKey), str(pubKey), str(addr))


def GenMultiAddr(nAddrCount = 1, isTestnet = True):
    listRet = []
    for i in range(nAddrCount):
        listRet.append(GenEthAddr())
    return listRet

def main():
    print(GenMultiAddr(1))

if __name__ == '__main__':

    main()
