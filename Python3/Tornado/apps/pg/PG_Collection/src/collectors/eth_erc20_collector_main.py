#!coding:utf8

#author:yqq
#date:2020/5/20 0020 20:29
#description:

import logging
import time

from src.collectors.eth.erc20_collector import collect_erc20_usdt
from src.collectors.eth.eth_collector import collect_eth
from src.config.constant import ENV_NAME


def get_default_logger(log_level=logging.INFO):
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s |  %(process)d  |  %(levelname)s | %(pathname)s |%(funcName)s:%(lineno)d] %(message)s')
    return logging.getLogger(__name__)


logger = get_default_logger()



def main():

    # 3 次  ERC20_USDT归集  1 次 ETH归集

    n = 0
    cap_time = 100 if str(ENV_NAME).upper() == 'PRO' else 30
    while True:
        try:
            collect_erc20_usdt()

            if n % 3 == 0  and n != 0:
                collect_eth()
                n  = 0
            else:
                n += 1

            for i in range(cap_time):
                logger.info('sleeping....')
                time.sleep(6)
        except Exception as e:
            logger.error(f'{e}')

    pass


if __name__ == '__main__':
    main()