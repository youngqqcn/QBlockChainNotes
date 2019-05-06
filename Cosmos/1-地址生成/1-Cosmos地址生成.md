# Cosmos地址生成算法

```python




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
    return  os.urandom(32).encode('hex')    #生成 256位 私钥


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


```

