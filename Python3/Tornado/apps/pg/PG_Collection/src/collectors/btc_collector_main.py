#!coding:utf8

#author:yqq
#date:2020/7/13 0013 15:34
#description:  BTC归集主函数
import logging
import time

from src.collectors.btc.btc_collector import btc_collect
from src.config.constant import ENV_NAME


def get_default_logger(log_level=logging.INFO):
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s |  %(process)d  |  %(levelname)s | %(pathname)s |%(funcName)s:%(lineno)d] %(message)s')
    return logging.getLogger(__name__)


logger = get_default_logger()


def main():
    cap_time = 45*10 if str(ENV_NAME).upper() == 'PRO' else 2*10   #PRO环境 45分钟一次 , 测试环境 2分钟一次
    while True:
        try:
            btc_collect()
            # break
            for i in range(cap_time):
                logger.info('sleeping....')
                time.sleep(6)
        except Exception as e:
            logger.error(f'{e}')


    pass


if __name__ == '__main__':

    main()