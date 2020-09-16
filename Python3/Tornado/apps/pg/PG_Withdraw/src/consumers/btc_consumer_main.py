#!coding:utf8

#author:yqq
#date:2020/7/10 0010 21:56
#description:
from src.consumers.btc.btc_withdraw_consumer import BtcConsumerImpl

import time

def main():

    while True:
        try:
            instance = BtcConsumerImpl()
            instance.start()
        except Exception as e:
            print(f'main() ERROR:{e}')
            time.sleep(10)

    pass





if __name__ == '__main__':

    main()