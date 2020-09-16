#!coding:utf8

#author:yqq
#date:2020/5/11 0011 12:48
#description:
from src.consumers.eth_erc20.eth_erc20_consumer_impl import EthErc20ConsumerImpl

import time

def main():

    while True:
        try:
            instance = EthErc20ConsumerImpl()
            instance.start()
        except Exception as e:
            print(f'main() ERROR:{e}')
            time.sleep(10)

    pass




if __name__ == '__main__':

    main()