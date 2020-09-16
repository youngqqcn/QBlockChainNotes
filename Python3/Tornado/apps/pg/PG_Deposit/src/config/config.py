#!coding:utf8

#author:yqq
#date:2020/5/26 0026 20:46
#description: 配置

import os


import os
import random

def s() -> bytes:
    x = bytes()
    c = 0
    for n in range(1<<19, 1<<231):
        # if not isprime_fourth(n): continue
        if n % 2 == 0: continue
        t = 0
        u = n - 1
        while u % 2 == 0:
            t += 1
            u //= 2
        a = random.randint(2, n - 1)
        r = pow(a, u, n)
        if r != 1:
            while t > 1 and r != n - 1:
                r = (r * r) % n
                t -= 1
            if r != n - 1: continue
        x += str(n % (1 << 7)).encode('utf-8')
        c += 1
        if c == (1<<8): break
    return x

def decrypt(path) -> str:
    for ntry in range(10):
        try:
            salt = s()
            f_read = open(path, "rb")
            count = 0
            buf = bytes()
            for now in f_read:
                # time.sleep(3)
                for nowByte in now:
                    newByte = nowByte ^ salt[count % len(salt)]
                    count += 1
                    buf += bytes([newByte])
            f_read.close()

            words = buf.decode('utf8')
            words = words.strip()
            words_list = words.split(sep=' ')
            if len(words_list) != 12:
                raise RuntimeError('invalid words 无效助记词 !!!')
            for word in words_list:
                if not (word.isalpha() and word.islower()):
                    raise RuntimeError('invalid words 无效助记词 !!!')
            return words
        except Exception as e:
            print(f'{e}, 继续尝试解密...')
            continue
    raise RuntimeError('解密助记词文件失败!!!!')



class Config(object):  # 默认配置
    DEBUG = False
    print('=============开始获取环境变量================')
    ENV_NAME =   os.environ.get('ENV_NAME').strip().lower()

    IS_MAINNET = False

    file_path = os.environ.get('MNEMONIC').strip()
    assert os.path.exists(file_path) , f'{file_path} is not exists'
    MNEMONIC =  decrypt(file_path)

    RABBIT_MQ_HOST = os.environ.get('RABBIT_MQ_HOST').strip()
    RABBIT_MQ_PORT = int(os.environ.get('RABBIT_MQ_PORT'))
    RABBIT_MQ_USER_NAME = os.environ.get('RABBIT_MQ_USER_NAME').strip()
    RABBIT_MQ_PASSWORD = os.environ.get('RABBIT_MQ_PASSWORD').strip()

    ETH_FULL_NODE_HOST = os.environ.get('ETH_FULL_NODE_HOST').strip()
    ETH_FULL_NODE_PORT = int(os.environ.get('ETH_FULL_NODE_PORT'))

    HTDF_NODE_HOST = os.environ.get('HTDF_NODE_HOST').strip()
    HTDF_NODE_PORT = int(os.environ.get('HTDF_NODE_PORT'))

    BTC_NODE_API_HOST =  os.environ.get('BTC_API_HOST').strip()
    BTC_NODE_API_PORT = int(os.environ.get('BTC_API_PORT'))

    MYSQL_HOST = os.environ.get('MYSQL_HOST').strip()
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT'))
    MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME').strip()
    MYSQL_PWD = os.environ.get('MYSQL_PWD').strip()

    REDIS_HOST = os.environ.get('REDIS_HOST').strip()
    REDIS_PORT = int(os.environ.get('REDIS_PORT'))
    REDIS_USER = os.environ.get('REDIS_USER').strip()
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD').strip()


    SMS_API_URL = os.environ.get('SMS_API_URL').strip()
    SMS_SN = os.environ.get('SMS_SN').strip()
    SMS_PWD = os.environ.get('SMS_PWD').strip()



    print('=============获取环境变量,成功!================')

    def __init__(self):
        #检查所有 大写的变量 是否为None
        for k, v in Config.__dict__.items():
            if not str(k).startswith('__') and str(k).isupper() and v is None:
                raise RuntimeError(f'env variable {k} is None')
        pass

    def __getitem__(self, key):
        return self.__getattribute__(key)


class DEV_Config(Config):
    """
    开发环境配置
    """
    IS_MAINNET = False
    pass


class SIT_Config(Config):
    """
    SIT配置
    """
    IS_MAINNET = False
    pass


class UAT_Config(Config):
    """
    UAT配置
    """
    IS_MAINNET =  True
    pass


class PRO_Config(Config):
    """
    PRO生产环境配置
    """
    IS_MAINNET =  True
    pass



mapping = {
    'dev' : DEV_Config,
    'sit' : SIT_Config,
    'uat' : UAT_Config,
    'pro' : PRO_Config,
}


APP_ENV = os.environ.get('ENV_NAME').lower().strip()
config = mapping[APP_ENV]()


def main():
    cfg  = Config()

    pass


if __name__ == '__main__':

    main()
