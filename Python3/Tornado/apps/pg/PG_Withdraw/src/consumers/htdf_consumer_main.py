#!coding:utf8

#author:yqq
#date:2020/5/11 0011 12:48
#description:
from src.consumers.htdf.htdf_consumer_impl import HTDFConsumerImpl

import time

def main():

    while True:
        try:
            instance   = HTDFConsumerImpl()
            instance.start()
        except Exception as e:
            print(f'main() ERROR:{e}')
            time.sleep(5)

    pass


if __name__ == '__main__':

    main()