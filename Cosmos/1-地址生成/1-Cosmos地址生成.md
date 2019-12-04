# Cosmos地址生成算法

```python
#!coding:utf8

#author:yqq
#date:2019/5/5 0005 19:33
#description:  USDP地址生成



import hashlib
import ecdsa
import os



#-----------------------------bech32编码---------------------------------------------
# Copyright (c) 2017 Pieter Wuille
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Reference implementation for Bech32 and segwit addresses."""


CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def bech32_polymod(values):
    """Internal function that computes the Bech32 checksum."""
    generator = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for value in values:
        top = chk >> 25
        chk = (chk & 0x1ffffff) << 5 ^ value
        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0
    return chk


def bech32_hrp_expand(hrp):
    """Expand the HRP into values for checksum computation."""
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]


def bech32_verify_checksum(hrp, data):
    """Verify a checksum given HRP and converted data characters."""
    return bech32_polymod(bech32_hrp_expand(hrp) + data) == 1


def bech32_create_checksum(hrp, data):
    """Compute the checksum values given HRP and data."""
    values = bech32_hrp_expand(hrp) + data
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]


def bech32_encode(hrp, data):
    """Compute a Bech32 string given HRP and data values."""
    combined = data + bech32_create_checksum(hrp, data)
    return hrp + '1' + ''.join([CHARSET[d] for d in combined])


def bech32_decode(bech):
    """Validate a Bech32 string, and determine HRP and data."""
    if ((any(ord(x) < 33 or ord(x) > 126 for x in bech)) or
            (bech.lower() != bech and bech.upper() != bech)):
        return (None, None)
    bech = bech.lower()
    pos = bech.rfind('1')
    if pos < 1 or pos + 7 > len(bech) or len(bech) > 90:
        return (None, None)
    if not all(x in CHARSET for x in bech[pos+1:]):
        return (None, None)
    hrp = bech[:pos]
    data = [CHARSET.find(x) for x in bech[pos+1:]]
    if not bech32_verify_checksum(hrp, data):
        return (None, None)
    return (hrp, data[:-6])


def convertbits(data, frombits, tobits, pad=True):
    """General power-of-2 base conversion."""
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1
    for value in data:
        if value < 0 or (value >> frombits):
            return None
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        return None
    return ret


def decode(hrp, addr):
    """Decode a segwit address."""
    hrpgot, data = bech32_decode(addr)
    if hrpgot != hrp:
        return (None, None)
    decoded = convertbits(data[1:], 5, 8, False)
    if decoded is None or len(decoded) < 2 or len(decoded) > 40:
        return (None, None)
    if data[0] > 16:
        return (None, None)
    if data[0] == 0 and len(decoded) != 20 and len(decoded) != 32:
        return (None, None)
    return (data[0], decoded)


def encode(hrp, witver, witprog):
    """Encode a segwit address."""
    ret = bech32_encode(hrp, [witver] + convertbits(witprog, 8, 5))
    if decode(hrp, ret) == (None, None):
        return None
    return ret

#-----------------------------bech32编码---------------------------------------------



#--------------------------以下是USDP地址生成代码-------------------------------------



#2019-11-12 根据官方定义修改  有限域
# http://www.secg.org/sec2-v2.pdf#page=9&zoom=100,0,249
# 关于 有限域的定义 请参考
# 0xEFFFFFC2F = 2**32 - 2**9 - 2**8 - 2**7 - 2**6 - 2**4 - 1
g_nFactor = 0xEFFFFFC2F + 0x23492397 #增值自定义
g_nMaxPrivKey = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364140 - g_nFactor #私钥最大值 (差值是自定义的)
g_nMinPrivKey = 0x0000000000000000000000000000000000000000000000000000000000000001 + g_nFactor #私钥最小值 (增值是自定义的)

def PrivKeyToPubKeyCompress(privKey):
    '''
    私钥-->公钥  压缩格式公钥
    :param privKey:  ( 如果是奇数,前缀是 03; 如果是偶数, 前缀是 02)   +  x轴坐标
    :return:
    '''
    sk = ecdsa.SigningKey.from_string(privKey.decode('hex'), curve=ecdsa.SECP256k1)
    # vk = sk.verifying_key
    try:
        # print(sk.verifying_key.to_string().encode('hex'))
        point_x = sk.verifying_key.to_string().encode('hex')[     : 32*2] #获取点的 x 轴坐标
        point_y = sk.verifying_key.to_string().encode('hex')[32*2 :     ]  #获取点的 y 轴坐标
        # print("point_x:", point_x)

        if (long(point_y, 16) & 1) == 1:  # 如果是奇数,前缀是 03; 如果是偶数, 前缀是 02
            prefix = '03'
        else:
            prefix = '02'
        return prefix + point_x
    except:
        raise("array overindex")
        pass



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


def PubKeyToAddr( pubKey,  hrp='usdp'):
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(hashlib.sha256(pubKey.decode('hex')).digest())
    r160data = ripemd160.digest()
    dataList = [ ]
    for i in range(len(r160data)):    #将 二进制串 转为 整数数组
        dataList.append(ord(r160data[i]))
    addr = bech32_encode(hrp, convertbits(dataList, 8, 5))   #bech32编码
    return addr


def GenAddr(hrp = 'usdp'):
    '''
    USDP 生成地址
    :param hrp:  前缀 , USDP和 HTDF 通用
    :return: (privkey, pubKey, addr)
    '''

    #生成私钥
    privKey = GenPrivKey()

    #私钥-->公钥
    pubKey = PrivKeyToPubKeyCompress(privKey)

    #公钥-->地址
    addr = PubKeyToAddr(pubKey, hrp)
    return str(privKey),  str(pubKey), str(addr)



def GenMultiAddr(nAddrCount = 1, isTestnet=True):
    '''
    生成多个地址  此函数供C++调用
    :param nAddrCount:
    :param isTestnet:
    :return:
    '''
    # return [("1111", "2222", "3333"), ("4444", "55555", "66666")]

    lstRet = []
    for i in range(nAddrCount):
        lstRet.append(GenAddr('usdp'))
    return lstRet


# def main():
#
#     lstRet = GenMultiAddr(10)
#     print(lstRet)
#
#
#     pass
#
#
#
#
# if __name__ == '__main__':
#
#     main()
#--------------------------以上是地址生成核心代码-------------------------------------



```

